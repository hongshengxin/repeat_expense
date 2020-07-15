# -*- coding:utf-8 -*-


from calfnlp.FAQ_engine.own_synonyms.xgb_rerank import XgbRerank
from utils.util import Traditional2Simplified
from typing import List, Set, Dict, Text
from utils.util import filer_num, sentence_filter
import jieba
from utils.sentence_cut import SentenceCut
from app.libs.log_util import LogUtils
import os
import datetime
import math

from repeat_expense.strPreprocess import StrPreprocess

log = LogUtils.get_stream_logger('controller/module')
today_str = str(datetime.date.today())
log2 = LogUtils.get_rotating_file_logger(__name__, os.path.join("logs", today_str))


class RepeatExpense():
    def __init__(self, config):
        self.use_tra2sim = config.USE_TRA2SIM
        self.use_split_sentence = config.USE_SPLIT_SENTENCE
        self.use_filter_num = config.USE_FILTER_NUM
        self.use_filter_bracket = config.USE_FILTER_BRACKET
        self.sencut_server = SentenceCut.get_sentence_cut()
        self.name_score = config.name_score
        self.money_score = config.money_score
        self.companey_score = config.companey_score
        self.project_score = config.preject_score
        self.ponum_score = config.ponum_score
        self.strPreprocess = StrPreprocess()

    def repeat_expense_cheack(self, text: str, similar_texts: List[str]) -> List[int]:
        '''
        主方法
        :param text:
        :param similar_texts:
        :return:
        '''
        if not text or not similar_texts:
            return []

        filter_result = []

        try:

            text, similar_text_dic = self.pre_process(text, similar_texts)

            text_keyinfos = self.strPreprocess.get_all_key_features(text)

            words1 = self.sencut_server.sentence_cut_filter(text)

            similar_texts_dic = XgbRerank.candi_senten_filter(text=text,
                                                              similar_texts=similar_text_dic)

            '''相似度计算'''

            for item in similar_texts_dic:
                words2 = self.sencut_server.sentence_cut_filter(item["sen"])
                lcs, diffL, jaccard = XgbRerank.get_xgb_feature(words1, words2)
                score = XgbRerank.get_rerank_score(lcs, diffL, jaccard, item["score"])
                '''获取候选集合的关键词信息'''
                sub_item_keyinfos = self.strPreprocess.get_sub_key_features(text_keyinfos, item["sen"])

                res_score = self.mix_keyinfo_score(text_keyinfos=text_keyinfos,
                                                   items_keyinfors=sub_item_keyinfos,
                                                   score=score)

                if res_score > 0.8:
                    filter_result.append({"index": item["index"],
                                          "score": res_score})
            filter_result = sorted(filter_result, key=lambda x: x["score"], reverse=True)[:3]
            log2.info(filter_result)
        except Exception as ex:
            log2.info("计算相似度发生错误:{}".format(str(ex)))

        if filter_result:
            return [item["index"] for item in filter_result]
        else:
            return []

    def pre_process(self, text: str, similar_texts: List[str]):
        '''
        前处理
        :param text:
        :param similar_texts:
        :return:
        '''

        text = text.strip()
        for i in range(len(similar_texts)):
            similar_texts[i] = similar_texts[i].strip()
        if self.use_tra2sim:
            text = Traditional2Simplified(text)
            similar_texts = [Traditional2Simplified(sen) for sen in similar_texts]
        text = self.strPreprocess.cn2num(text)
        similar_texts = [self.strPreprocess.cn2num(sen) for sen in similar_texts]
        if self.use_filter_num:
            text = filer_num(text)
            similar_texts = [filer_num(sen) for sen in similar_texts]
        if self.use_filter_bracket:
            text = sentence_filter(text)
            similar_texts = [sentence_filter(sen) for sen in similar_texts]
        if self.use_split_sentence:
            add_similar_texts = {}
            for index, sen in enumerate(similar_texts):
                sen_split_texts = sen.split("\n")
                add_similar_texts[index] = sen_split_texts
            similar_texts = add_similar_texts
        else:
            add_similar_texts = {}
            for index, sen in enumerate(similar_texts):
                add_similar_texts[index] = sen
            similar_texts = add_similar_texts
        return text, similar_texts

    def mix_keyinfo_score(self, text_keyinfos: List, items_keyinfors: List, score: int):
        '''

        :param text_keyinfos: (names, companys, moneys, ponums)
        :param items_keyinfors: (names, companys, moneys, ponums, project_names)
        :param score:
        :return: score-
        '''
        mix_keyinfos = list(zip(text_keyinfos, items_keyinfors))
        '''名字处理'''
        mix_names = mix_keyinfos[0]
        score = self.merge_name(mix_names[0], mix_names[1], score, self.name_score)

        '''公司名字处理'''
        mix_companeys = mix_keyinfos[1]

        score = self.merge_po_score(mix_companeys[0], mix_companeys[1], score, self.companey_score)

        '''金额处理'''
        mix_moneys = mix_keyinfos[2]
        score = self.merge_score(mix_moneys[0], mix_moneys[1], score, self.money_score)
        '''项目号合同号的处理'''
        mix_ponums = mix_keyinfos[3]
        score = self.merge_po_score(mix_ponums[0], mix_ponums[1], score,  self.ponum_score)


        return score

    def merge_score(self, item1: List, item2: List, score, add_score):
        '''得分融合'''

        count_same_item = 0
        if not item1 and not item2:
            return score

        if len(item1) > len(item2):
            item1, item2 = item2, item1
        num_item = len(item2)
        if item1 and item2:
            for item in item1:
                if item in item2:
                    count_same_item += 1
        if count_same_item > 0:
            score = score + (add_score)
        else:
            score = score - (add_score) * (math.sqrt(num_item))
        return score

    def merge_componey_score(self,item1: List, item2: List, score, add_score):
        '''合并公司名'''
        count_same_item = 0
        if not item1 and not item2:
            return score
        if len(item1) > len(item2):
            item1, item2 = item2, item1

        if item1 and item2:
            for it1 in item1:
                for it2 in item2:
                    if it1 in it2 or it2 in it1:
                        count_same_item += 1
        if count_same_item > 0:
            score = score + (add_score)
        return score

    def merge_name(self, item1: List, item2: List, score, add_score):


        if not item1 and not item2:
            return score
        elif len(item1) > 0 and len(item2) > 0:
            # if len(item1) == len(item2):
            count_same_item = 0
            with_flag = False
            if len(item2) > len(item1):
                item1, item2 = item2, item1
            if "等" in item2 or "等" in item1:
                with_flag = True
            for it in item1:
                if it in item2:
                    count_same_item += 1
            if with_flag:
                if count_same_item > 0:
                    score += add_score*len(item1)
            else:
                if count_same_item == len(item1):
                    score += add_score * len(item1)
                else:
                    score -= add_score*(len(item1)*math.sqrt(len(item1)))
            # else:
            #     count_same_item = 0
            #     with_flag = False
            #     if len(item2) > len(item1):
            #         item1, item2 = item2, item1
            #     if "等" in item2 or "等" in item1:
            #         with_flag = True
            #     for item in item1:
            #         if item in item2:
            #             count_same_item+=1
            #
            #     if count_same_item > 0 and with_flag:
            #         score = score + (add_score) * count_same_item / math.sqrt(count_same_item)
            #     else:
            #         score = 0
            #
            #         if item in item2:
            #             count_same_item += 1
            #     if count_same_item > 0:
            #         score = score + (add_score) * count_same_item / math.sqrt(count_same_item)
            #     else:
            #         score = score - add_score * num_item

        return score


    def merge_po_score(self,item1: List, item2: List, score, add_score):


        if not item1 and not item2:
            return score
        elif len(item1) > 0 and len(item2) > 0:
            count_same_item = 0
            if len(item2) > len(item1):
                item1, item2 = item2, item1
            for it in item1:
                if it in item2:
                    count_same_item += 1

            if count_same_item > 0:
                if count_same_item == len(item1):
                    score += add_score * len(item1)
                else:
                    score += add_score*(len(item1)-count_same_item)
            else:
                score -= add_score*(len(item1))
        return score

if __name__ == '__main__':
    from app import config

    repeat_expense = RepeatExpense(config)
    print(repeat_expense.repeat_expense_cheack("2020年2月精斗云伙伴市场费-物料制作（无锡亦勋信息咨询有限公司、安徽云蝶网络科技有限公司）",
                                               ["跟另一个事由重复:2020年2月精斗云伙伴市场费-物料制作（山东金福恩信息科技有限公司、淄博祥顺软件技术有限公司）",
                                                "跟另一个事由重复:2020年2月精斗云伙伴市场费-物料制作（山东金福恩信息科技有限公司、淄博祥顺软件技术有限公司）",
                                                "2018年7月15日——8月15日服务器托管费用，总额28700元。服务器托管合同《合同编号：NF-KX-YZ20117233》，请参见附件。"]))
