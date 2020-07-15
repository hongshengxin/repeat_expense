#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/20 16:39
# @Author  : zhm
# @File    : TimeNormalizer.py
# @Software: PyCharm
import pickle
import regex as re
import arrow
import json
import re as ree
from .StringPreHandler import StringPreHandler
from .TimePoint import TimePoint
from .TimeUnit import TimeUnit
from .time_re import get_pattern
# from .common.log import *
import os


# 时间表达式识别的主要工作类
class TimeNormalizer:
    def __init__(self, isPreferFuture=True):
        self.isPreferFuture = isPreferFuture
        self.pattern, self.holi_solar, self.holi_lunar = self.init()

    def init(self):
        pattern = re.compile(get_pattern())
        with open(os.path.dirname(__file__) + '/resource/holi_solar.json', 'r', encoding='utf-8') as f:
            holi_solar = json.load(f)
        with open(os.path.dirname(__file__) + '/resource/holi_lunar.json', 'r', encoding='utf-8') as f:
            holi_lunar = json.load(f)
        return pattern, holi_solar, holi_lunar

    def parse(self, target, timeBase=arrow.now()):
        """
        TimeNormalizer的构造方法，timeBase取默认的系统当前时间
        :param timeBase: 基准时间点
        :param target: 待分析字符串
        :return: 时间单元数组
        """
        self.isTimeSpan = False  # 是时间跨度
        self.invalidSpan = False  # 无效的时间跨度
        self.timeSpan = ''  # 时间跨度
        self.target = str(target)
        self.timeBase = arrow.get(timeBase).format('YYYY-M-D-H-m-s')
        self.oldTimeBase = self.timeBase
        self.timeToken = self.__timeEx()
        dic = {}
        re_list = []
        time_extract_identity = []
        res = self.timeToken
        if self.isTimeSpan:
            if self.invalidSpan:
                return re_list, time_extract_identity
            else:
                dic['type'] = 'timedelta'
                dic['timedelta'] = self.timeSpan
                dic['raw'] = [str(i.exp_time) for i in res]
        else:
            if len(res) == 0:
                return re_list, time_extract_identity
            else:
                # dic['type'] = 'timespan'
                # 提取前两个时间为时间跨度
                # dic['timespan'] = [res[0].time.format("YYYY-MM-DD HH:mm:ss"), res[1].time.format("YYYY-MM-DD HH:mm:ss")]

                dic['times'] = [re.time.format("YYYY-MM-DD HH:mm:ss") for re in res]
                dic['raw'] = [self.target[i:j] for i, j in zip(self.begin, self.end) if i != -1 and j != -1]
                time_extract_identity = [re.time_extract_identity for re in res]
                for time, time_words in zip(dic['times'], dic['raw']):
                    re_list.append((time_words, time))
        return re_list, time_extract_identity

    def __preHandling(self, s):
        """
        待匹配字符串的清理空白符和语气助词以及大写数字转化的预处理
        :return:
        """
        s = StringPreHandler.delKeyword(s, "\\s+")  # 清理空白符
        s = StringPreHandler.delKeyword(s, "[的]+")  # 清理语气助词
        s = StringPreHandler.numberTranslator(s)  # 大写数字转化
        s = StringPreHandler.sbctodbc(s)

        return s

    def __timeEx(self):
        """
        时间识别主控制流程
        :param target: 输入文本字符串
        :param timeBase: 输入基准时间
        :return: TimeUnit[]时间表达式类型数组
        """
        self.begin = []
        self.end = []
        startline = -1
        endline = -1
        rpointer = 0
        temp = []
        match = self.pattern.finditer(self.target)
        for m in match:
            the_data = m.group()
            mstart = m.start()
            mend = m.end()

            the_data = self.__preHandling(the_data)
            # 字符串中以 1点结尾 如：今天下午1点
            # if '1点' in the_data and len(str(the_data).split('1点')[0]) < 2:
            #     continue
            # # 如： 今天下午1点钟
            # if '点' in the_data and len(str(the_data).split('点')[-1]) == 1 and str(the_data).split('点')[-1] != '半':
            #     the_data = the_data[:-1]
            #     mend -= 1

            startline = mstart
            if startline == endline:
                rpointer -= 1
                temp[rpointer] = temp[rpointer] + the_data
                self.end[-1] = mend
            elif startline > endline and ree.match(r'[的\s()（）]+$', self.target[endline:startline]):
                rpointer -= 1
                temp[rpointer] = temp[rpointer] + self.target[endline:startline] + the_data
                self.end[-1] = mend
            else:
                self.begin.append(mstart)
                temp.append(the_data)
                self.end.append(mend)
            endline = mend
            rpointer += 1
        res = []
        # 时间上下文： 前一个识别出来的时间会是下一个时间的上下文，用于处理：周六3点到5点这样的多个时间的识别，第二个5点应识别到是周六的。
        contextTp = TimePoint()
        for i in range(0, rpointer):
            res.append(TimeUnit(temp[i], self, contextTp))
            if self.invalidSpan:
                res.pop()
                self.begin[i] = -1
                self.end[i] = -1
                self.isTimeSpan = False  # 是时间跨度
                self.invalidSpan = False  # 无效的时间跨度
            if len(res) == 0:
                continue
            contextTp = res[len(res) - 1].tp
        res = self.__filterTimeUnit(res)
        return res

    def __filterTimeUnit(self, tu_arr):
        """
        过滤timeUnit中无用的识别词。无用识别词识别出的时间是1970.01.01 00:00:00(fastTime=0)
        :param tu_arr:
        :return:
        """
        if (tu_arr is None) or (len(tu_arr) < 1):
            return tu_arr
        res = []
        for tu in tu_arr:
            if tu.time.timestamp != 0:
                res.append(tu)
        return res

if __name__ == '__main__':
    t = TimeNormalizer()
    t.parse('清明')
