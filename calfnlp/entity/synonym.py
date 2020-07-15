# _*_ coding: UTF-8 _*_
'''
组织定义的同义词字典, 在标准分词WordSegmenter中使用
_synonym_map (orgid, seg) -> 标准词
_synonym_map_general 词 -> 标准词

目前暂停使用同义词的设置

'''

import codecs
import threading
import time

from calfnlp.const import ResourceFile



class Synonym(object):
    _id_to_data = {}
    _synonym_map = {}
    _synonym_map_general = {}
    _last_update_timestamp = 0
    _lock = threading.Lock()

    @classmethod
    def init_general_synonym(cls):
        '''
        从资源文件中加载同义词
        :return:
        '''
        synonym_map_general = {}
        synonyms_general = codecs.open(ResourceFile.GeneralSynonym, encoding='utf-8').read().split("\n")
        for item in synonyms_general:
            syn_list = item.split()
            if len(syn_list) > 2:
                if syn_list[0].endswith("="):
                    std_word = syn_list[1]
                    other_words = syn_list[2:]
                    for word in other_words:
                        if synonym_map_general.get(word):
                            # print '词重复. {}, 已有标准词:[{}], 新标准词是:{}.'.format(word.encode('utf-8'), ' '.join(synonym_map_general.get(word)).encode('utf-8'), std_word.encode('utf-8'))
                            synonym_map_general[word].append(std_word)
                        else:
                            synonym_map_general[word] = [std_word, ]

        with cls._lock:
            cls._synonym_map_general = synonym_map_general

    @classmethod
    def update_org_synonym(cls, synonym_list):
        '''
        初始化企业的同义词词典

        字典数据格式为
        {
            id:
            org_id:
            synonym:
            std_word:
            isDeleted:
        }

        :return:
        '''

        try:
            for x in synonym_list:
                _id = x.get("id") or str(x.get("_id"))
                org_id = x.get("org_id")
                org_id = str(org_id)
                synonym = x.get("synonym")
                std_word = x.get("std_word")
                is_delete = x.get("isDeleted")

                if not (_id and org_id and synonym and std_word and is_delete):
                    continue

                if is_delete == 'Y':
                    cls._id_to_data.pop(_id, None)
                else:
                    cls._id_to_data[_id] = (org_id, synonym, std_word)
        except Exception as e:
            TraceLogger.error(e)

        synonym_map = {}
        for org_id, synonym, std_word in cls._id_to_data.values():
            for seg in synonym.split(','):
                if seg != std_word:
                    synonym_map[(org_id, seg)] = std_word

        with cls._lock:
            cls._synonym_map = synonym_map

        cls._last_update_timestamp = int(time.time() * 1000)

        # count_dict = {}
        # for (org_id, synonym), std_word in cls._synonym_map.items():
        #     count_dict.setdefault(org_id, 0)
        #     count_dict[org_id] += 1

        # for org_id, count in count_dict.items():
        #     TraceLogger.debug("[Synonym]%s: %d" % (org_id, count))

    @classmethod
    def get(cls, org_id, word):
        with cls._lock:
            syn = cls._synonym_map.get((org_id, word))
        if syn:
            return syn

        res = cls._synonym_map_general.get(word)
        if res:
            return res[0]  # 返回第一个
        return None

    @classmethod
    def getAll(cls, org_id, word):
        with cls._lock:
            syn = cls._synonym_map.get((org_id, word))
        if syn:
            return [syn, ]

        res = cls._synonym_map_general.get(word)
        if res:
            return res
        return []

    # @classmethod
    # def get(cls, tenant_id, word):
    #     with cls._lock:
    #         syn = cls._synonym_map.get((tenant_id, word))
    #     if syn:
    #         return syn
    #     loop_limit = 20
    #     syn_set = set()
    #     while loop_limit > 0:
    #         loop_limit -= 1
    #         res = cls._synonym_map_general.get(word, word)
    #         syn_set.update(res)
    #         if word == res:
    #             break
    #         word = res
    #     if loop_limit == 0:
    #         return sorted(syn_set)[0]
    #     return res


#
# def add_orgkeywords(org_id, synonyms, stdword):
#     record = {"org_id":str(org_id), "std_word":stdword, "synonym":synonyms, "isDeleted":"N", }
#     db_util.add_record(T_ORG_SYNONYMS, record)


if __name__ == "__main__":
    Synonym.init_general_synonym()

    # Synonym.update_org_synonym()
    org_id = "10109"
    orgs = [None, org_id]
    for org_id in orgs:
        print("org_id: ", org_id, '同义词查找如下: ----')
        wordlist = ["女人家", "怎么", "要", "自己", "怎样", "阻挡", "买", "办公", "我", "请", "请个假", "我们",
                    "一起", "在", "坪", "山", "开", "个", "会"]
        for word in wordlist:
            print('词:{}, 同义词标准词:[{}].'.format(word, ' '.join(Synonym.getAll(org_id, word))))

    # add_orgkeywords(org_id=org_id, synonyms="到哪里,招谁,怎么办,怎么样,怎样,哪里,问谁,去哪里,怎么,找谁,如何处理", stdword="如何")
    # add_orgkeywords(org_id=org_id, synonyms="买,买过,申购", stdword="购买")
