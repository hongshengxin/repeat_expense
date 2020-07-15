# -*- coding: utf-8 -*-
import re
import cn2an
from calfnlp.time_nlp.TimeNormalizer import TimeNormalizer
import calendar
import time
import arrow
from typing import Text, Dict, Tuple, List
from calfnlp.entity.common_entitys.common_entitys_extract import CommonNameExtract
import ahocorasick
import codecs
from calfnlp.const import ResourceFile
import os
import pickle



class StrPreprocess:

    def __init__(self):
        self.tn = TimeNormalizer()
        self.org_tree = self.build_tree()
        self.name_extract_tool = CommonNameExtract

    def build_tree(self, ):
        '''构造AC树'''
        companey_names = self.reload_companey_names(ResourceFile.companey_file_path,"pickle")
        org_name = self.reload_companey_names(ResourceFile.organization_file_path)
        wordlist = list(set(companey_names + org_name))
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    def reload_companey_names(self, file_path: str, file_mark=None):

        if not os.path.exists(file_path):
            return []

        if file_mark == "pickle":
            f = open(file_path, "rb")
            all_companeys = pickle.load(f)
            return all_companeys
        else:
            companey_datas = codecs.open(file_path, "r", encoding="utf-8")

            companey_names = [name.strip() for name in companey_datas.readlines()]

            return companey_names

    def cn2num(self, question: Text):

        if not question:
            return None
        # 更改中文数字-->阿拉伯数字
        mm = re.findall(r'[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七八九十0123456789]{1,}'
                        r'[亿|万|千|百]{1}[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七八九十百千万0123456789]{0,}'
                        r'|[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七八九十0123456789]{2,}|'
                        r'(?<=周)[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七]{1,}|(?<=前|上|近)'
                        r'[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七八九十]{1,}|'
                        r'[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七八九十]{1,}'
                        r'(?=月|到|个|号|日|周|天|年)|(?<=数字)'
                        r'[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七八九十]{1,}',
                        question)
        if mm:
            for item in mm:
                if item.startswith('0'):
                    pass
                else:
                    v = cn2an.cn2an(item, 'smart')
                    if (item.startswith('零') and len(item) > 1):
                        question = question.replace(item, ''.join(['0', str(v)]), 1)

                    else:
                        question = question.replace(item, str(v), 1)

        return question

    def name_extract(self, text: Text):
        names_info = self.name_extract_tool.common_name_extract(text=text)
        names = [info.get("text") for info in names_info]
        names = list(set(names))
        stop_names = []
        for n1 in names:
            for n2 in names:
                if n1 in n2 and n1 != n2:
                    stop_names.append(n1)
        final_names = [i for i in names if i not in stop_names]
        '''判断是否有等'''
        for name in final_names:
            if self.with_flag(text=text, name=name):
                return final_names + ["等"]
        return final_names

    def companey_extract(self, text: Text):

        region_wds = []
        for i in self.org_tree.iter(text):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        return final_wds

    def money_extract(self, text: Text):
        '''
        费用的提取
        '''

        patten_money = re.findall(r'([1-9][0-9]*)人民币', text)
        patten_money2 = re.findall(r'([1-9][0-9]*)元', text)
        spe_money = re.findall(r'[放款|金额]+：([1-9][0-9]*)', text)
        res = list(set(patten_money + patten_money2 + spe_money))

        return res

    def po_num_extract(self, text: Text):
        '''
        预算号
        '''
        if not text:
            return []
        '''合同号'''
        po_num = re.findall(r"[a-z|A-Z]{1,}[\d]{1,}[-]{0,1}[\d]{1,}", text)

        return po_num

    def project_name_extract(self, text: Text):
        return []

    def get_all_key_features(self, text: Text):

        names = self.name_extract(text)

        companys = self.companey_extract(text)

        real_names = self.merge_name_companey(names,companys)

        moneys = self.money_extract(text)
        ponums = self.po_num_extract(text)
        # project_names = self.project_name_extract(text)

        return (real_names, companys, moneys, ponums)

    def get_sub_key_features(self, text_keyinfos: List, sen: Text):
        '''
        获取候选句子的关键信息
        :param text_keyinfos:
        :param candi_text:
        :return:
        '''

        names_info = text_keyinfos[0]
        names = self.get_sub_text_names(names_info, sen)
        companys = self.companey_extract(sen)

        real_names = self.merge_name_companey(names,companys)
        moneys = self.money_extract(sen)
        ponums = self.po_num_extract(sen)


        return (real_names, companys, moneys, ponums)

    def get_sub_text_names(self, names_info: List, text: Text):

        filte_names = []
        for name in names_info:
            if name in text:
                filte_names.append(name)

        names_info = self.name_extract_tool.common_name_extract(text=text)
        names = [info.get("text") for info in names_info]
        names = list(set(names+filte_names))
        stop_names = []
        for n1 in names:
            for n2 in names:
                if n1 in n2 and n1 != n2:
                    stop_names.append(n1)
        final_names = [i for i in names if i not in stop_names]
        '''判断是否有等'''
        for name in final_names:
            if self.with_flag(text=text, name=name):
                return final_names + ["等"]
        return final_names

    def with_flag(self, text: Text, name: Text):
        pattern = name + "(等)"
        res_0 = re.search(pattern, text)

        return True if res_0 else False


    def merge_name_companey(self,names: List, companeys:List):

        real_names =[]
        if names and companeys:
            for name in names:
                for companey in companeys:
                    if name not in companey:
                        real_names.append(name)
            return real_names
        else:
            return names





# def strPreProcess(question):
#     # print('进入strpreprocess')
#     value = question
#
#     try:
#         if re.search(r'为负值|为负|是负', value):
#             value = re.sub(r'为负值|为负|是负', '小于0', value)
#         if re.search(r'为正值|为正|是正', value):
#             value = re.sub(r'为正值|为正|是正', '大于0', value)
#
#         # X.x块钱  X毛钱
#         value = value.replace('块钱', '块')
#         value = value.replace('千瓦', 'kw')
#         value = value.replace('月份', '月')
#         value = value.replace('，', ',')
#
#         # value = value.replace('个', '')
#         # value = value.replace(' ', '')              #空格处理
#
#         # 更改中文数字-->阿拉伯数字壹贰叁肆伍陆柒捌玖拾佰仟
#         mm = re.findall(r'[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七八九十0123456789]{1,}'
#                         r'[亿|万|千|百]{1}[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七八九十百千万0123456789]{0,}'
#                         r'|[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七八九十0123456789]{2,}|'
#                         r'(?<=周)[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七]{1,}|(?<=前|上|近)'
#                         r'[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七八九十]{1,}|'
#                         r'[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七八九十]{1,}'
#                         r'(?=月|到|个|号|日|周|天|年)|(?<=数字)'
#                         r'[壹贰叁肆伍陆柒捌玖拾佰仟〇零一幺二两三四五六七八九十]{1,}',
#                         value)
#         if mm:
#             for item in mm:
#                 if item.startswith('0'):
#                     pass
#                 else:
#                     v = cn2an.cn2an(item, 'smart')
#                     if (item.startswith('零') and len(item) > 1):
#                         value = value.replace(item, ''.join(['0', str(v)]), 1)
#
#                     else:
#                         # print(value)
#                         # print(item,str(v))
#                         value = value.replace(item, str(v), 1)
#                         # print(value)
#
#         # 时间处理-区分时间点还是时间段
#         if re.search(r'从?([^截止]到(.*?))', value):  # 时间段,去年到今年三月
#             value = value.replace('月份', "月").replace('从', '')
#             if re.search(r'\d+?到\d+?月', value):
#                 match = re.search(r'(\d+?)到\d+?月', value)
#                 month_begin = match.group(1)
#                 value = re.sub(r'\d+?到', month_begin + '月到', value)
#
#             res_tn = tn.parse(value)
#             # print(res_tn)
#             if res_tn:
#                 for idx, item in enumerate(res_tn['raw']):
#                     if idx > 0 and re.search(r'(\d+?)月$', item):
#                         match_1 = re.search(r'(\d+?)/(\d+?)/(\d+?)$', res_tn['timespan'][idx])
#                         year, month = match_1.group(1), match_1.group(2)
#                         _, monthRange = calendar.monthrange(int(year), int(month))
#                         res_tn['timespan'][idx] = res_tn['timespan'][idx].replace('-01',
#                                                                                   ''.join(['-', str(monthRange)]))
#                         value = value.replace(res_tn['raw'][idx], res_tn['timespan'][idx])
#                     else:
#                         value = value.replace(res_tn['raw'][idx], res_tn['timespan'][idx])
#
#         if re.search(
#                 r'上上个?周|上上个?(月|季度)|下下个?周|下下个?月|[前上过]去?(\d)个?(星期|周|礼拜|月份?|天|日)|[前上](\d)个?季度|(?<!年)(今年|去年|前年)?(\d){1,2}月份?(?!\d)|(今|去|前)?年?(上|下)?半年(?!前|后)|(近|过去|上|下)(半|\d{1,2})个?月(?!以前|以后)|(中旬|上旬|下旬)|前年(?!\d)',
#                 value):  # 时间区间
#
#             value = get_time_span(value)
#             # print('value:',value)
#             res_tn = tn.parse(value)
#             # print("时间区间:",res_tn)
#             for idx, item in enumerate(res_tn['timespan']):
#                 value = value.replace(res_tn['raw'][idx], res_tn['timespan'][idx])
#
#         if re.search(
#                 r'((\d+?|[上下]个?)(月份?)(\d+?[号日])(以来|之后)?|(\d+?|([上下]个?))(月份?)(以来|之后)|大前天|前天|大后天|后天|[上本这]周\d+?|截止到?|之前)',
#                 value):  # 时间点
#
#             res_tn = tn.parse(value)
#             # print("时间点:",res_tn)
#             for idx, item in enumerate(res_tn['raw']):
#                 value = value.replace(res_tn['raw'][idx], res_tn['timestamp'])
#
#         if re.search(r'(\d+|半)个?月|年以?(?=前|后)', value):  # 时间点
#             if re.search(r'(\d+)个月(?=以前)', value):
#                 res = re.search(r'(\d+)个月(?=以前)', value)
#                 month = res.group(1)
#                 # print(month)
#                 time = arrow.now().replace(months=-int(month)).format('YYYY/MM/DD')
#                 # print("time is:",time)
#                 value = re.sub(r'(\d+)个月(?=以前)', time, value)
#
#             elif re.search(r'半个?月以前', value):
#                 time = arrow.now().replace(days=-15).format('YYYY/MM/DD')
#                 # print("time is:",time)
#                 value = re.sub(r'半个?月(?=以前)', time, value)
#
#             elif re.search(r'半年以?前', value):
#                 time = arrow.now().replace(months=-6).format('YYYY/MM/DD')
#                 # print("time is:",time)
#                 value = re.sub(r'半年', time, value)
#
#         if re.search(r'\d+?到|至\d+?', value):
#             value = re.sub(r'到|至', "-", value)
#
#         patten_money = re.compile(r'[〇零一幺二两三四五六七八九十百千万0123456789]{1,}点[〇零一幺二两三四五六七八九十0123456789]{1,}')
#         k = patten_money.findall(value)
#         if k:
#             for item in k:
#                 listm = item.split('点')
#                 front = cn2an.cn2an(listm[0], "smart")
#                 end = cn2an.cn2an(listm[1], "smart")
#                 val = str(front) + '.' + str(end)
#                 value = value.replace(item, val, 1)
#
#         patten_kuai = re.compile(r'[〇零一幺二两三四五六七八九十百千万0123456789]{1,}块[〇零一幺二两三四五六七八九十0123456789]{,1}')
#         km = patten_kuai.findall(value)
#         if km:
#             for item in km:
#                 listm = item.split('块')
#                 front = cn2an.cn2an(listm[0], "smart")
#                 if (listm[1] == ''):
#                     end = False
#                 else:
#                     end = cn2an.cn2an(listm[1], "smart")
#                 if end:
#                     val = str(front) + '.' + str(end) + '元'
#                 else:
#                     val = str(front) + '元'
#                 value = value.replace(item, val, 1)
#             # value = value.replace('毛钱', '元',)
#             # value = value.replace('毛', '元')
#         patten_mao = re.compile(r'[〇零一幺二两三四五六七八九十百千万0123456789]{1,}毛')
#         kmao = patten_mao.findall(value)
#         if kmao:
#             for item in kmao:
#                 strmao = item.replace('毛', '')
#                 valmao = cn2an.cn2an(strmao, "smart")
#                 maoflo = str(float(valmao) / 10) + '元'
#                 value = value.replace(item, maoflo, 1)
#         value = value.replace('元毛', '元')
#
#         patten_jao = re.compile(r'[〇零一幺二两三四五六七八九十百千万0123456789]角')
#         kjao = patten_jao.findall(value)
#         if kjao:
#             for item in kjao:
#                 strjiao = item.replace('角', '')
#                 valjiao = cn2an.cn2an(strjiao, 'smart')
#                 jaoflo = str(float(valjiao) / 10) + '元'
#                 value = value.replace(item, jaoflo, 1)
#
#         value = value.replace('元毛', '元')
#         value = value.replace('元角', '元')
#         # 百分之几----\d%
#         if re.search(r'百分之', value):
#             items_one = re.findall(r'百分之\d{1,}\.?\d*', value)
#             if items_one:
#                 for item in items_one:
#                     item_t = item.replace('百分之', '') + '%'
#                     value = re.sub(str(item), str(item_t), value)
#
#             items_two = re.findall(r'百分之[零|一|幺|二|两|三|四|五|六|七|八|九|十|百]{1,}', value)
#
#             if items_two:
#                 for item in items_two:
#                     item_t = item.replace('百分之', '')
#                     val_t = cn2an.cn2an(item_t)
#                     item_t = str(val_t) + '%'
#                     value = re.sub(str(item), str(item_t), value)
#
#         if re.search(r'百分点', value):
#             items_we = re.findall(r'[零|一|幺|二|两|三|四|五|六|七|八|九|十|百]{1,}.??百分点', value)
#             if items_we:
#                 for item in items_we:
#                     item_t = re.sub('.??百分点', '', item)
#                     val_t = cn2an.cn2an(item_t)
#                     item_t = str(val_t) + '%'
#                     value = re.sub(str(item), str(item_t), value)
#
#             items_se = re.findall(r'\d+?\.??\d*.??百分点', value)
#             if items_se:
#                 for item in items_se:
#                     item_t = re.sub('.??百分点', '', item) + '%'
#                     # item_t = re.sub('百分点', '', item) + '%'
#                     value = re.sub(str(item), str(item_t), value)
#
#         mm3 = re.findall(r'[大于|小于|前|超过|第|破][〇零一幺二两三四五六七八九十百千]{1}(?!车间|部门)', value)
#         if mm3:
#             for item in mm3:
#                 mm33 = re.findall(r'[〇零一幺二两三四五六七八九十百千]{1}', item)
#                 for item2 in mm33:
#                     v3 = cn2an.cn2an(item2)
#                     itemvalue = item.replace(item2, str(v3), 1)
#                 # v, r = chinese_to_digits(item)
#
#                 value = value.replace(item, itemvalue, 1)
#
#         mm4 = re.findall(r'[排名|排行|达到|排在|排|列|率]{1,}前[0123456789]{1,}', value)
#         if mm4:
#
#             for item in mm4:
#                 v = re.sub(r'[排名|排行|达到|排在|排|列|率]{1,}前', '', item)
#                 s1 = item.replace('前', '大于', 1)
#                 vs = s1.replace(v, str(int(v) + 1), 1)
#                 value = value.replace(item, vs, 1)
#
#         # 更改中文年份并补充完整
#
#         pattern_date1 = re.compile(r'(\d{2,4}年(?=\D))')
#         # pattern_date1 = re.compile(r'(.{1}月.{,2})日|号')
#         date1 = pattern_date1.findall(value)
#         dateList1 = list(set(date1))
#         if dateList1:
#             for item in dateList1:
#                 v = str_to_date(item)
#                 day_begin = '{}/01/01'.format(v.strip('年'))  # 年初肯定是1月1号
#                 day_end = '{}/12/31'.format(v.strip('年'))  # 年末是12月31号
#                 timespan = "{}-{}".format(day_begin, day_end)
#                 item = ''.join(list(item))
#                 value = re.sub(str(item), timespan, value)
#
#         pattern_date2 = re.compile(
#             r'(\d+)(\-|年)(\d{1,2}|零|一|幺|二|两|三|四|五|六|七|八|九|十)(\-|月)(\d{1,2}|零|一|幺|二|两|三|四|五|六|七|八|九|十)([日|号]){0,1}')
#         date2 = pattern_date2.findall(value)
#         if date2:
#
#             for item in date2:
#                 item = ''.join(list(item))
#                 v = str_to_date(item)
#                 value = re.sub(str(item), str(v), value)
#
#         pattern_date3 = re.compile(r'(\d*?|零|一|幺|二|两|三|四|五|六|七|八|九|十)(月)(\d*?|零|一|幺|二|两|三|四|五|六|七|八|九|十)([号|日])')
#         date3 = pattern_date3.findall(value)
#         if date3:
#             for item in date3:
#                 item = ''.join(list(item))
#                 v = str_to_date(item)
#                 value = re.sub(str(item), str(v), value)
#
#         pattern_date4 = re.compile(r'(\d*?)(年)(\d*?|零|一|幺|二|两|三|四|五|六|七|八|九|十)(月)')
#         date4 = pattern_date4.findall(value)
#         if date4:
#
#             for item in date4:
#                 year = ''.join([item[0], item[1]])
#                 year = str_to_date(year).strip('年')
#                 _, monthRange = calendar.monthrange(int(year), int(item[2]))
#                 # print(monthRange)
#                 day_begin = '{}/{}/01'.format(year, item[2])  # 月初肯定是1号
#                 day_end = '{}/{}/{}'.format(year, item[2], monthRange)  # 月末最后一天
#                 timespan = "{}-{}".format(day_begin, day_end)
#                 item = ''.join(list(item))
#                 value = re.sub(str(item), timespan, value)
#
#                 # v = str_to_date(item)
#                 # value = re.sub(str(item), str(v), value)
#
#         if re.search(r'1下|1共|.1元股|1线', value):
#             value = value.replace('1下', '一下')
#             value = value.replace('.1元股', '元一股')
#             value = value.replace('1共', '一共')
#             value = value.replace('1线', '一线')
#
#     except Exception as exc:
#         print(exc)
#         # print('strPreProcess_error', exc,'--',value)
#         pass
#
#     return value


# 转换时间区间

def get_time_span(question):
    question = re.sub(r'上上周(?<=\D)', "上上周一-上上周日", question)
    question = re.sub(r'下下周(?<=\D)', "下下周一-下下周日", question)
    cur = arrow.now()

    pattern_0 = r'(?<!上)上个?月(?=\D)'
    res_0 = re.search(pattern_0, question)

    if res_0:
        day_now = time.localtime()
        day_begin = '%d/%02d/01' % (day_now.tm_year, day_now.tm_mon - 1)  # 月初肯定是1号
        _, monthRange = calendar.monthrange(day_now.tm_year,
                                            day_now.tm_mon - 1)  # 得到本月的天数 第一返回为月第一日为星期几（0-6）, 第二返回为此月天数
        day_end = '%d/%02d/%02d' % (day_now.tm_year, day_now.tm_mon - 1, monthRange)
        timespan = "{}-{}".format(day_begin, day_end)
        question = re.sub(r'上个?月(?<=\D)', timespan, question)

    pattern_1 = r'上上个?(月|季度)(?<=\D)'
    res_1 = re.search(pattern_1, question)

    if res_1:
        if res_1.group(1) == '月':
            day_now = time.localtime()
            day_begin = '%d/%02d/01' % (day_now.tm_year, day_now.tm_mon - 2)  # 月初肯定是1号
            _, monthRange = calendar.monthrange(day_now.tm_year,
                                                day_now.tm_mon - 2)  # 得到本月的天数 第一返回为月第一日为星期几（0-6）, 第二返回为此月天数
            day_end = '%d/%02d/%02d' % (day_now.tm_year, day_now.tm_mon - 2, monthRange)
            timespan = "{}-{}".format(day_begin, day_end)
            question = re.sub(r'上上个?月(?<=\D)', timespan, question)
        elif res_1.group(1) == '季度':
            quater_start_now = cur.floor("quarter")  # 当前季度的开始时间
            quater_end_now = cur.ceil("quarter")  # 当前季度的结束时间
            day_begin = quater_start_now.replace(months=-6).format("YYYY/MM/DD")
            day_end = quater_end_now.replace(months=-6).format("YYYY/MM/DD")
            timespan = "{}-{}".format(day_begin, day_end)
            question = re.sub(r'上上个?季度(?<=\D)', timespan, question)

    pattern_2 = r'下下个?月(?<=\D)'
    res_2 = re.search(pattern_2, question)
    if res_2:
        day_now = time.localtime()
        day_begin = '%d/%02d/01' % (day_now.tm_year, day_now.tm_mon + 2)  # 月初肯定是1号
        _, monthRange = calendar.monthrange(day_now.tm_year,
                                            day_now.tm_mon + 2)  # 得到本月的天数 第一返回为月第一日为星期几（0-6）, 第二返回为此月天数
        day_end = '%d/%02d/%02d' % (day_now.tm_year, day_now.tm_mon + 2, monthRange)
        timespan = "{}-{}".format(day_begin, day_end)
        question = re.sub(r'下下个?月(?<=\D)', timespan, question)

    pattern_3 = r'[上前过]去?(\d)个?(星期|周|礼拜|月份?|天|日)'
    res_3 = re.search(pattern_3, question)

    if res_3:
        # print(res_3.groups())
        if res_3.group(2) in ['星期', '周', '礼拜']:
            week = int(res_3.group(1))
            span = -cur.weekday()
            day_begin = cur.replace(weeks=-week, days=span).format("YYYY/MM/DD")
            day_end = cur.replace(weeks=-1, days=6 + span).format("YYYY/MM/DD")
            timespan = "{}-{}".format(day_begin, day_end)
            question = re.sub(r'[上前过]去?(\d)个?(星期|周|礼拜)', timespan, question)
        elif res_3.group(2) in ['月', '月份']:
            cur_month_begin = cur.floor("month")
            cur_month_end = cur.ceil("month")
            month = int(res_3.group(1))
            day_begin = cur_month_begin.replace(months=-month).format("YYYY/MM/DD")
            day_end = cur_month_end.replace(months=-1).format("YYYY/MM/DD")
            timespan = "{}-{}".format(day_begin, day_end)
            question = re.sub(r'[上前过]去?(\d)个?(月份?)', timespan, question)
        elif res_3.group(2) in ['天', '日']:
            day = int(res_3.group(1))
            day_begin = cur.replace(days=-day).format("YYYY/MM/DD")
            day_end = cur.format("YYYY/MM/DD")
            timespan = "{}-{}".format(day_begin, day_end)
            question = re.sub(r'[上前过]去?(\d)个?(天|日)', timespan, question)

    pattern_5 = r'(今年|去年|前年)?(\d+?)月份?(?!\d)'
    res_5 = re.search(pattern_5, question)
    if res_5:
        # print(res_5.groups())
        year = res_5.group(1)
        month = res_5.group(2)
        day_now = time.localtime()
        if year == '今年' or year == None:  # 没有年份默认是今年
            year = day_now.tm_year
        elif year == '去年':
            year = day_now.tm_year - 1
        elif year == '前年':
            year = day_now.tm_year - 2
        day_begin = '%d/%02d/01' % (year, int(month))  # 月初肯定是1号
        # print("month:",month)
        _, monthRange = calendar.monthrange(year, int(month))  # 得到本月的天数 第一返回为月第一日为星期几（0-6）, 第二返回为此月天数
        day_end = '%d/%02d/%02d' % (year, int(month), monthRange)
        timespan = "{}-{}".format(day_begin, day_end)
        question = re.sub(r'(今年|去年)?(\d){1,2}月份?(?!\d)', timespan, question)

    # print("question:",question)

    pattern_5_1 = r'前年(?!\d)'
    res_5_1 = re.search(pattern_5_1, question)
    if res_5_1:
        day_now = time.localtime()
        # print('=============================')
        day_begin = '%d/01/01' % (day_now.tm_year - 2)  # 月初肯定是1号
        day_end = '%d/12/31' % (day_now.tm_year - 2)
        timespan = "{}-{}".format(day_begin, day_end)
        question = re.sub(r'前年(?!\d)', timespan, question)

    pattern_6 = r'(去年)?[前上](\d)个?季度'
    res_6 = re.search(pattern_6, question)
    if res_6:
        if res_6.group(1) == '去年':
            day_begin = cur.floor("year").replace(years=-1)
            qua = int(re.search(pattern_6, question).group(2))
            # print(qua)
            day_end = day_begin.replace(months=qua * 3).format("YYYY/MM/DD")
            timespan = "{}-{}".format(day_begin.format("YYYY/MM/DD"), day_end)
            question = re.sub(r'(去年)?[前上](\d)个?季度', timespan, question)

        else:
            quater_start_now = cur.floor("quarter")  # 当前季度的开始时间
            quater_end_now = cur.ceil("quarter")  # 当前季度的结束时间
            mon = int(re.search(pattern_6, question).group(2))
            day_begin = quater_start_now.replace(months=-mon * 3).format("YYYY/MM/DD")
            day_end = quater_end_now.replace(months=-3).format("YYYY/MM/DD")
            timespan = "{}-{}".format(day_begin, day_end)
            question = re.sub(r'[前上](\d)个?季度', timespan, question)

    pattern_7 = r'(今|去|前)年(上|下)半年'
    res_7 = re.search(pattern_7, question)
    if res_7:
        if res_7.group(1) == '今':
            year = cur.format("YYYY")  # 年份
        elif res_7.group(1) == '去':
            year = cur.replace(years=-1).format("YYYY")
        elif res_7.group(1) == '前':
            year = cur.replace(years=-2).format("YYYY")
        if res_7.group(2) == "上":
            timespan = "{}/01/01-{}/06/30".format(year, year)
        else:
            timespan = "{}/07/01-{}/12/31".format(year, year)
        question = re.sub(r'(今|去|前)年(上|下)半年', timespan, question)

    pattern_7_1 = r'(?<!上|下)半年'  # 处理半年前这种表达
    res_7_1 = re.search(pattern_7_1, question)
    if res_7_1:
        day_begin = cur.replace(months=-6).format("YYYY/MM/DD")
        day_end = cur.format('YYYY/MM/DD')
        timespan = "{}-{}".format(day_begin, day_end)
        question = re.sub(r'(?<!上|下)半年', timespan, question)

    pattern_7_2 = r'(上|下)半年'  # 只说了上下半年，默认是今年上半年、今年下半年这种表达
    res_7_2 = re.search(pattern_7_2, question)
    if res_7_2:
        if res_7_2.group(1) == '上':
            day_begin = cur.floor("year")
            day_end = day_begin.replace(months=+6).replace(days=-1)
            timespan = "{}-{}".format(day_begin.format("YYYY/MM/DD"), day_end.format("YYYY/MM/DD"))
            question = re.sub(r'(上|下)半年', timespan, question)
        else:
            day_end = cur.ceil("year")
            day_begin = day_end.replace(months=+6).replace(days=+1)
            timespan = "{}-{}".format(day_begin.format("YYYY/MM/DD"), day_end.format("YYYY/MM/DD"))
            question = re.sub(r'(上|下)半年', timespan, question)

    pattern_8 = r'(近|过去)(半)个?月'
    res_8 = re.search(pattern_8, question)
    if res_8:
        day_begin = cur.replace(days=-15).format("YYYY/MM/DD")

        day_end = cur.format("YYYY/MM/DD")
        timespan = "{}-{}".format(day_begin, day_end)
        question = re.sub(r'(近|过去)(半)个?月', timespan, question)

    pattern_8_1 = r'(上|下)半个?月'
    res_8_1 = re.search(pattern_8_1, question)
    if res_8_1:
        # print('==============================')
        if res_8_1.group(1) == '上':
            day_begin = cur.floor("month").format("YYYY/MM/DD")
            day_end = cur.floor("month").replace(days=+14).format("YYYY/MM/DD")
        else:
            day_end = cur.ceil("month").format("YYYY/MM/DD")
            day_begin = cur.floor("month").replace(days=+14).format("YYYY/MM/DD")

        timespan = "{}-{}".format(day_begin, day_end)
        question = re.sub(r'(上|下)半个?月', timespan, question)

    pattern_9 = '(上旬|中旬|下旬|中上旬|中下旬)'
    res_9 = re.search(pattern_9, question)
    if res_9:
        xun = res_9.group(1)
        if xun == '上旬':
            res = re.search(r'(\d+/\d+/\d+-\d+/\d+/\d+)上旬', question).group(1)
            # print(res)
            day_begin, _ = res.split('-')
            day_end = arrow.get(day_begin).replace(days=+9).format('YYYY/MM/DD')
            timespan = "{}-{}".format(day_begin, day_end)
            question = re.sub(r'(\d+/\d+/\d+-\d+/\d+/\d+)上旬', timespan, question)
        elif xun == '中旬':
            res = re.search(r'(\d+/\d+/\d+-\d+/\d+/\d+)中旬', question).group(1)
            # print(res)
            day_begin, day_end = res.split('-')
            day_begin = arrow.get(day_begin).replace(days=+9).format('YYYY/MM/DD')
            day_end = arrow.get(day_begin).replace(days=+10).format('YYYY/MM/DD')
            timespan = "{}-{}".format(day_begin, day_end)
            question = re.sub(r'(\d+/\d+/\d+-\d+/\d+/\d+)中旬', timespan, question)
        elif xun == '下旬':
            res = re.search(r'(\d+/\d+/\d+-\d+/\d+/\d+)下旬', question).group(1)
            # print(res)
            day_begin, day_end = res.split('-')
            day_begin = arrow.get(day_begin).replace(days=+19).format('YYYY/MM/DD')
            timespan = "{}-{}".format(day_begin, day_end)
            question = re.sub(r'(\d+/\d+/\d+-\d+/\d+/\d+)下旬', timespan, question)
        elif xun == '中上旬':
            res = re.search(r'(\d+/\d+/\d+-\d+/\d+/\d+)中上旬', question).group(1)
            # print(res)
            day_begin, day_end = res.split('-')
            day_end = arrow.get(day_begin).replace(days=+19).format('YYYY/MM/DD')
            timespan = "{}-{}".format(day_begin, day_end)
            question = re.sub(r'(\d+/\d+/\d+-\d+/\d+/\d+)中上旬', timespan, question)
        elif xun == '中下旬':
            res = re.search(r'(\d+/\d+/\d+-\d+/\d+/\d+)中下旬', question).group(1)
            # print(res)
            day_begin, day_end = res.split('-')
            day_begin = arrow.get(day_begin).replace(days=+9).format('YYYY/MM/DD')
            timespan = "{}-{}".format(day_begin, day_end)
            question = re.sub(r'(\d+/\d+/\d+-\d+/\d+/\d+)中下旬', timespan, question)

    return question


# 汉字数字转阿拉伯数字
def Chinese2digits(uchars_chinese):
    total = 0

    common_used_numerals_tmp = {
        '0': 0,
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        '〇': 0,
        '零': 0,
        '一': 1,
        '幺': 1,
        '二': 2,
        '两': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9,
        '十': 10,
        '百': 100,
        '千': 1000,
        '万': 10000,
        '百万': 1000000,
        '千万': 10000000,
        '亿': 100000000,
        '百亿': 10000000000
    }
    r = 1  # 表示单位：个十百千...
    try:

        for i in range(len(uchars_chinese) - 1, -1, -1):
            # print(uchars_chinese[i])
            val = common_used_numerals_tmp.get(uchars_chinese[i])

            if val is not None:
                # print('val,r', val,r)
                if val >= 10 and i == 0:  # 应对 十三 十四 十*之类
                    if val > r:
                        r = val
                        total = total + val
                    else:
                        r = r * val
                        # total = total + r * x
                elif val >= 10:
                    if val > r:
                        r = val
                    else:
                        r = r * val
                elif val == 0 and i != 0:
                    r = r * 10
                elif r == 1:
                    total = total + pow(10, len(uchars_chinese) - i - 1) * val
                else:

                    total = total + r * val

    except Exception as exc:
        print(exc)

    return total, r


# 日期字符转日期
def str_to_date(date_str):
    try:
        # 是数字 有年月日三位
        date_search = re.search(r'(\d+)(\-|\.|\/)(\d+)(\-|\.|\/)(\d+)', date_str)
        if date_search:
            year_str = date_search.group(1)
            month_str = date_search.group(3)
            day_str = date_search.group(5)
            if len(year_str) == 2:
                year_str = '20' + year_str
            if len(year_str) == 3:
                year_str = '2' + year_str
            date_date = '{}/{}/{}'.format(year_str, month_str, day_str)
            return date_date

        # 是数字 只有年月
        # 辅导公告 默认是月底
        date_search = re.search(r'(\d+)(\-|\.|\/)(\d+)', date_str)
        if date_search:
            year_str = date_search.group(1)
            month_str = date_search.group(3)
            if len(year_str) == 2:
                year_str = '20' + year_str
            if len(year_str) == 3:
                year_str = '2' + year_str
            date_date = '%s/%s月' % (year_str, month_str)
            return date_date

        # 以下包含汉字
        date_str = date_str.replace('号', '日')
        # 有年月日三位
        date_search = re.search('(.{2,4})年(.*?)月(.*?)日', date_str)
        if date_search:
            # 不能用isnumeric 汉字一二三四会被认为是数字
            # 只有年月日是汉字 数字还是阿拉伯数字
            if date_search.group(1).isdigit():
                year_str = date_search.group(1)
                month_str = cn2an.cn2an(date_search.group(2), "smart")
                day_str = cn2an.cn2an(date_search.group(3), "smart")
            # 年份不足4位 把前面的补上
            if len(year_str) == 2:
                year_str = '20' + year_str
            if len(year_str) == 3:
                year_str = '2' + year_str
            # print(year_str,month_str,day_str)
            date_str = '%s/%s/%s' % (year_str, month_str, day_str)
            return date_str

        date_search = re.search(r'(.{2,4})年(.*?)月(\d{1,2})$', date_str)
        if date_search:
            if date_search.group(1).isdigit():  # 不能用isnumeric 汉字一二三四会被认为是数字
                # 只有年月日是汉字 数字还是阿拉伯数字
                year_str = date_search.group(1)
                month_str = cn2an.cn2an(date_search.group(2), "smart")
                day_str = cn2an.cn2an(date_search.group(3), "smart")
            # 年份不足4位 把前面的补上
            if len(year_str) == 2:
                year_str = '20' + year_str
            if len(year_str) == 3:
                year_str = '2' + year_str
            print(year_str, month_str, day_str)
            date_str = '%s/%s/%s' % (year_str, month_str, day_str)
            return date_str

        # 只有两位
        date_search = re.search('(.{2,4})年(.*?)月', date_str)
        if date_search:
            if date_search.group(1).isdigit():
                year_str = date_search.group(1)
                month_str = cn2an.cn2an(date_search.group(2), "smart")
            if len(year_str) == 2:
                year_str = '20' + year_str
            if len(year_str) == 3:
                year_str = '2' + year_str
            date_str = '%s/%s月' % (year_str, month_str)
            return date_str

        date_search = re.search('(.{1,2})月(.{1,2})([日])', date_str)
        if date_search:
            month_str = cn2an.cn2an(date_search.group(1), "smart")
            day_str = cn2an.cn2an(date_search.group(2), "smart")
            date_str = '%s/%s日' % (month_str, day_str)
            return date_str
        # 只有一位

        date_search = re.search(r'(\d{2,4})年', date_str)
        if date_search:
            if date_search.group(1).isdigit():
                year_str = date_search.group(1)
            if len(year_str) == 2 and int(year_str[0]) < 2:
                year_str = '20' + year_str
            if len(year_str) == 3:
                year_str = '2' + year_str
            date_str = '%s年' % (year_str)
            return date_str

        # print('处理不了的日期 %s' % date_str)
    except Exception as exc:
        print('exception:', exc)
    return None


def unit_convert(ques):
    value = ques
    try:
        mmw = re.findall(r'[一幺二两三四五六七八九十]万', value)
        if mmw:
            for item in mmw:
                v, r = cn2an.cn2an(item)
                value = re.sub(item, str(v), value)
        mmy = re.findall(r'[一幺二两三四五六七八九十百]亿', value)
        if mmy:
            for item in mmy:
                v, r = cn2an.cn2an(item)
                value = re.sub(item, str(v), value)

        mmf = re.findall(r'\d*\.?\d+万|\d*\.?\d+百万|\d*\.?\d+千万|\d*\.?\d+亿', value)
        if mmf:

            for item in mmf:
                mmf_v = re.sub(r'万|百万|千万|亿', '', item)
                mmf_r = re.sub(mmf_v, '', item)
                v, r = cn2an.cn2an(mmf_r)
                # print('dig', mmf,v,'--',r)
                value = re.sub(item, str(int(float(mmf_v) * r)), value)

    except Exception as exc:
        print('unit_convert_error', exc, '---', ques)

    return value


def money_extract(text: Text):
    '''费用的提取'''

    patten_money = re.findall(r'([1-9][0-9]*)人民币', text)
    patten_money2 = re.findall(r'([1-9][0-9]*)元', text)
    spe_money = re.findall(r'[放款|金额]+：([1-9][0-9]*)', text)
    res = list(set(patten_money + patten_money2 + spe_money))

    return res


def with_flag(text: Text, name: Text):
    pattern = name + "(等)"
    res_0 = re.search(pattern, text)

    return True if res_0 else False


if __name__ == '__main__':
    # strpre = StrPreprocess()
    # print(strpre.money_extract("输送新员工（刘兴璐、赵语国）参加顾问学院上岗培训费用，8800元/人，2人合计17600元"))
    # print(with_flag("新员工（刘兴璐、赵语国等）参加顾","赵语国"))
    print(money_extract("由代理商（无锡亦勋信息咨询有限公司）成功推荐客户（王学东 王培锦），累计放款：550000，按照协议约定应按照放款金额1%支付5500元。"))
    # str_test = '从四月份到5月份的收款'
    # # print(cn2an.cn2an('三','smart'))
    # print('原句:', str_test, '\n', '替换后的句子：', strPreProcess(str_test))
