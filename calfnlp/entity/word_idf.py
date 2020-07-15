# _*_ coding: UTF-8 _*_
'''
计算两个文本的相似性使用的字典.
calf.core.answerengine.questionsimilarity.rank_utils 和 calf.core.answerengine.questionsimilarity.rankingstrategy中使用

'''

import io

from calfnlp.const import ResourceFile


class WordIDF(object):
    with io.open(ResourceFile.WordIDF, encoding='utf-8') as fin:
        _datas = {line.split()[0]: float(line.split()[1]) for line in fin}

    @staticmethod
    def get():
        return WordIDF._datas
