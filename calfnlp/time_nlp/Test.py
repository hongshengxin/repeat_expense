#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from calfnlp.nlp_algorithm.time_nlp.TimeNormalizer import TimeNormalizer # 引入包

tn = TimeNormalizer()
# timeBase='2018-06-01 13:01:01'
res,time_extract_identity = tn.parse(target='''20180209 12:31''',) # target为待分析语句，timeBase为基准时间默认是当前时间
print(res, time_extract_identity)

# res = tn.parse(target='2013年二月二十八日下午四点三十分二十九秒', timeBase='2013-02-28 16:30:29') # target为待分析语句，timeBase为基准时间默认是当前时间
# print(res)
#
# res = tn.parse(target='我需要大概33天2分钟', timeBase='2013-02-28 16:30:29') # target为待分析语句，timeBase为基准时间默认是当前时间
# print(res)
#
# res = tn.parse(target='1月末') # target为待分析语句，timeBase为基准时间默认是当前时间
# print(res)
# print(eval(res)['raw'])
