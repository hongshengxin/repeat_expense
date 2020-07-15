#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-06-08 16:47
# @Author  : xinhongsheng

import ahocorasick
from typing import Text, List
import re


class SensitiveWordDetector(object):
    '''
    敏感词检验类
    '''

    tree_dict = dict()

    @classmethod
    def detect(cls, text: Text, model_id: Text, keywords: List, rebuildModel: bool):
        '''
        敏感词检验的方法
        :param text:
        :param model_id:
        :param keywords:
        :return:
        '''

        model_tree = cls.create_model(model_id, keywords, rebuildModel)

        normalized_text = cls.trim_illegal_char(text)

        return cls.parse_text(model_tree, normalized_text)

    @classmethod
    def create_model(cls, model_id: Text, keywords: List, rebuild: bool):

        if rebuild:

            tree = cls.create_tree(keywords)
            cls.tree_dict[model_id] = tree
        else:

            tree = cls.tree_dict.get(model_id, None)
            if not tree:
                tree = cls.create_tree(keywords)
        return tree

    @classmethod
    def create_tree(cls, keywords: List):
        '''
        构建关键词的树林
        :param keywords:
        :return:
        '''

        actree = ahocorasick.Automaton()
        for index, word in enumerate(keywords):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    @classmethod
    def trim_illegal_char(cls, text: Text):
        sub_str = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", text)

        length = len(sub_str)
        res = []
        for i in range(length):
            if cls.is_chinese(text[i]):
                res.append(text[i])
            else:
                if i == 0 or i == length-1:
                    res.append(text[i])
                else:
                    continue
        return "".join(res)


    @classmethod
    def is_chinese(cls, char: Text) ->bool:

        return char >= '\u4e00' and char<= '\u9fff'

    @classmethod
    def parse_text(cls, ac_tree, text):
        '''
        解析句子
        :param text:
        :return:
        '''
        res = []
        for end_index, (insert_order, original_value) in ac_tree.iter(text):
            start_index = end_index - len(original_value) + 1
            res.append(str(start_index)+":"+str(end_index)+"="+original_value)
            assert text[start_index:start_index + len(original_value)] == original_value
        return res

if __name__ == '__main__':
    sens = SensitiveWordDetector()
    print(sens.detect("2你滚2远点好吧2，你大爷的", "23", ["滚远点", "滚", "卧槽", "你大爷的"],True))







