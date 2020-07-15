# _*_ coding: UTF-8 _*_
'''
标点符号相关定义

'''

import string
from zhon import hanzi


class Punctuations():
    AllPuncUnicode = string.punctuation + hanzi.punctuation
    ZHPuncUnicode = hanzi.punctuation
    ENPuncUnicode = string.punctuation
    AllPunc = AllPuncUnicode
    ZHPunc = ZHPuncUnicode
    ENPunc = ENPuncUnicode
    PUNCTUATIONS = set(
        ENPuncUnicode + ZHPuncUnicode + u''':!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻︽︿﹁﹃﹙﹛﹝（｛“‘-—_…''')
    PUNCTUATIONS.remove(':')
    PUNCTUATIONS.remove('︰')


if __name__ == '__main__':
    print(Punctuations.PUNCTUATIONS)
    print('ZHPunc', type(Punctuations.ZHPuncUnicode))
    zh = []
    for s in Punctuations.ZHPuncUnicode:
        zh.append(s)
    for s in zh:
        print(s, type(s))

    print('\nENPunc')
    for s in Punctuations.PUNCTUATIONS:
        print(s, )
