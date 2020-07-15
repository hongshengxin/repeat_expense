#-*- coding:utf-8 -*-

from utils.langconv import *
from string import digits


def Traditional2Simplified(sentence):
    '''
    将sentence中的繁体字转为简体字
    :param sentence: 待转换的句子
    :return: 将句子中繁体字转换为简体字之后的句子
    '''
    sentence = Converter('zh-hans').convert(sentence)
    return sentence

def sentence_filter(sen):
    # format_sen = re.sub(u"\\(.*?\\)|\\{.*?}|\\[.*?]", "", sen)
    #
    # format_sen = re.sub("[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）]+',"",sen)
    format_sen = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".encode('utf-8').decode('utf-8'),
           "".encode('utf-8').decode('utf-8'), sen)
    return format_sen

def filer_num(sen):

    remove_digits = str.maketrans('', '', digits)

    res = sen.translate(remove_digits)
    return res


if __name__=="__main__":
    traditional_sentence = '憂郁的臺灣烏龜'
    simplified_sentence = filer_num("sadfas127sdf83")
    print(simplified_sentence)
