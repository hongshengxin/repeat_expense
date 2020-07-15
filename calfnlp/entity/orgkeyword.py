# _*_ coding: UTF-8 _*_
'''
组织定义的关键字字典, orgid -> set(关键字)
提供热加载能力

组织关键字，目前主要用于调整计算相似度

'''

import threading

from typing import Set, Text, Dict


class OrgKeyword():
    _dict_map: Dict[Text, Set] = {}  # org_id -> set(word)
    _lock = threading.Lock()

    @classmethod
    def update_org_keyword(cls, org_id: Text, wordset: Set[Text]):
        with cls._lock:
            cls._dict_map[org_id] = wordset

    @classmethod
    def remove_org_keyword(cls, org_id: Text, word: Text):
        with cls._lock:
            if org_id in cls._dict_map:
                cls._dict_map[org_id].remove(word)

    @classmethod
    def add_org_keyword(cls, org_id: Text, word: Text):
        with cls._lock:
            if org_id in cls._dict_map:
                cls._dict_map[org_id].add(word)
            else:
                cls._dict_map.setdefault(org_id, set())
                cls._dict_map[org_id].add(word)

    @classmethod
    def init_org_keyword(cls, org_id: Text, org_words):

        org_words = set(org_words)
        with cls._lock:
            cls._dict_map[org_id] = org_words

    @classmethod
    def get_by_org(cls, org_id):
        with cls._lock:
            return cls._dict_map.get(str(org_id), set())


# def add_orgkeywords(org_id, word):
#     record = {"modified":int(time.time()*1000), "org_id":str(org_id), "word":word, "isDeleted":"N"}
#     db_util.add_record(T_ORG_KEYWORDS, record)

if __name__ == '__main__':

    org_id = "10109"

    OrgKeyword.add_org_keyword(org_id, "云之家")
    OrgKeyword.add_org_keyword(org_id, "报表秀秀")
    for k in OrgKeyword.get_by_org(org_id):
        print(k)

    OrgKeyword.remove_org_keyword(org_id, "报表秀秀")
    for k in OrgKeyword.get_by_org(org_id):
        print(k)

    # add_orgkeywords(org_id, "云之家")
    # add_orgkeywords(org_id, "报表秀秀")
