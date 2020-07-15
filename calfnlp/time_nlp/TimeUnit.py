# @Author  : zhm
# @File    : TimeUnit.py
# @Software: PyCharm
import regex as re
import arrow
import copy
import json
from .TimePoint import TimePoint
from .RangeTimeEnum import RangeTimeEnum
from .LunarSolarConverter import get_solar_date, get_holi_date


# 时间语句分析
class TimeUnit:
    def __init__(self, exp_time, normalizer, contextTp):
        self.exp_time = exp_time
        self.normalizer = normalizer
        self.tp = TimePoint()
        self.tp_origin = contextTp
        self.isFirstTimeSolveContext = True
        self.isAllDayTime = True
        self.timeType = ''  # timespan/timestamp/timedelta
        self.time = arrow.now()
        self.time_extract_identity = {'Y':'', 'M':'', 'D':'', 'H':'', 'm':'', 's':''} # 字符串对应的时间
        self.time_normalization()

    def time_normalization(self):
        self.norm_setyear() #规范--年
        self.norm_setmonth() #规范--月
        self.norm_setday() #规范--日
        self.norm_setmonth_fuzzyday() # 规范--模糊日
        self.norm_setBaseRelated() # 规范--基准时间的偏移
        self.norm_setCurRelated() # 规范--时间表达式（今天、明天等）
        self.norm_setHarfRelated() # 规范--时间表达式（半天、半个小时等）
        self.norm_setSpecial()  # 特殊形式时间的规范化
        self.norm_sethour() #规范--小时
        self.norm_setminute() #规范--分钟
        self.norm_setsecond() #规范--秒
        # self.norm_setSpanRelated()
        self.norm_setHoliday() #节假日
        self.modifyTimeBase() #修改基准时间
        self.norm_spanTime()
        self.tp_origin.tunit = copy.deepcopy(self.tp.tunit)

        # 判断是时间点还是时间区间
        flag = True
        for i in range(0, 4):
            if self.tp.tunit[i] != -1:
                flag = False
        if flag:
            self.normalizer.isTimeSpan = True

        if self.normalizer.isTimeSpan:
            days = 0
            if self.tp.tunit[0] > 0:
                days += 365 * self.tp.tunit[0]
            if self.tp.tunit[1] > 0:
                days += 30 * self.tp.tunit[1]
            if self.tp.tunit[2] > 0:
                days += self.tp.tunit[2]
            tunit = self.tp.tunit
            for i in range(3, 6):
                if self.tp.tunit[i] < 0:
                    tunit[i] = 0
            seconds = tunit[3] * 3600 + tunit[4] * 60 + tunit[5]
            if seconds == 0 and days == 0:
                self.normalizer.invalidSpan = True
            self.normalizer.timeSpan = self.genSpan(days, seconds)
            return

        time_grid = self.normalizer.timeBase.split('-')
        tunitpointer = 5
        while tunitpointer >= 0 and self.tp.tunit[tunitpointer] < 0:
            if tunitpointer == 3:
                self.tp.tunit[i] = 10
            tunitpointer -= 1
        for i in range(0, tunitpointer):
            if self.tp.tunit[i] < 0:
                self.tp.tunit[i] = int(time_grid[i])

        self.time = self.genTime(self.tp.tunit)

    def genSpan(self, days, seconds):
        day = seconds // (3600*24)
        h = (seconds % (3600*24)) // 3600
        m = ((seconds % (3600*24)) % 3600) // 60
        s = ((seconds % (3600*24)) % 3600) % 60
        return str(days+day) + ' days, ' + "%d:%02d:%02d" % (h, m, s)

    def genTime(self, tunit):
        time = arrow.get('1970-01-01 00:00:00')
        try:
            if tunit[0] > 0:
                time = time.replace(year=tunit[0])
            if tunit[1] > 0:
                time = time.replace(month=tunit[1])
            if tunit[2] > 0:
                time = time.replace(day=tunit[2])
            if tunit[3] > 0:
                time = time.replace(hour=tunit[3])
            if tunit[4] > 0:
                time = time.replace(minute=tunit[4])
            if tunit[5] > 0:
                time = time.replace(second=tunit[5])
        except:
            return time
        return time

    def norm_setyear(self):
        """
        年-规范化方法--该方法识别时间表达式单元的年字段
        :return:
        """
        # 一位数表示的年份
        rule = "(?<![0-9])[0-9]{1}(?=年)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            # self.normalizer.isTimeSpan = True
            year = int(match.group())
            self.tp.tunit[0] = year
            self.time_extract_identity['Y'] = match.group() + '年'

        # 两位数表示的年份
        rule = "[0-9]{2}(?=年)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            year = int(match.group())
            self.tp.tunit[0] = year
            self.time_extract_identity['Y'] = match.group() + '年'

        # 三位数表示的年份
        rule = "(?<![0-9])[0-9]{3}(?=年)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            # self.normalizer.isTimeSpan = True
            year = int(match.group())
            self.tp.tunit[0] = year
            self.time_extract_identity['Y'] = match.group() + '年'

        # 四位数表示的年份
        rule = "[0-9]{4}(?=年)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            year = int(match.group())
            self.tp.tunit[0] = year
            self.time_extract_identity['Y'] = match.group() + '年'

        if 30 <= self.tp.tunit[0] < 100:
            self.tp.tunit[0] = 1900 + self.tp.tunit[0]
        if 0 < self.tp.tunit[0] < 30:
            self.tp.tunit[0] = 2000 + self.tp.tunit[0]

    def norm_setmonth(self):
        """
        月-规范化方法--该方法识别时间表达式单元的月字段
        :return:
        """
        # todo:识别月底
        rule = "((?<=\D)|^)\d+(?=月[底末])"
        pattern =re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            figure = int(match.group())
            if 1<=figure<=12:
                self.tp.tunit[1] = figure
                if self.tp.tunit[0] == -1:
                    tmp = arrow.get(self.normalizer.timeBase, "YYYY-M-D-H-m-s")
                    self.tp.tunit[0] = tmp.year
                temp_time = arrow.get(self.tp.tunit[0], self.tp.tunit[1], 1)
                temp_time = temp_time.shift(months=1)
                temp_time = temp_time.shift(days=-1)
                self.tp.tunit[2] = temp_time.day
                self.time_extract_identity['M'] = re.search("((?<=\D)|^)\d+月[底末]", self.exp_time).group()
                self.time_extract_identity['D'] = re.search("((?<=\D)|^)\d+月[底末]", self.exp_time).group()


        # rule = "((10)|(11)|(12)|([1-9]))(?=月)"
        rule = "((?<=\D)|^)\d+(?=月)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            figure = int(match.group())
            if 1<=figure<=12:
                self.tp.tunit[1] = figure
                # 处理倾向于未来时间的情况
                self.preferFuture(1)
                self.time_extract_identity['M'] = self.exp_time[match.start():match.end() + 1]

    def norm_setmonth_fuzzyday(self):
        """
        月-日 兼容模糊写法：该方法识别时间表达式单元的月、日字段
        :return:
        """
        rule = "((10)|(11)|(12)|([1-9]))(月|\\.|\\-)([0-3][0-9]|[1-9])"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            matchStr = match.group()
            p = re.compile("(月|\\.|\\-)")
            m = p.search(matchStr)
            if match is not None:
                splitIndex = m.start()
                month = matchStr[0: splitIndex]
                day = matchStr[splitIndex + 1:]
                self.tp.tunit[1] = int(month)
                self.tp.tunit[2] = int(day)
                # 处理倾向于未来时间的情况
                self.preferFuture(1)
                self.time_extract_identity['M'] = matchStr[:m.end()]
                if not matchStr[m.end():] in self.time_extract_identity['D']:
                    self.time_extract_identity['D'] = matchStr[m.end():]

    def norm_setday(self):
        """
        日-规范化方法：该方法识别时间表达式单元的日字段
        :return:
        """
        rule = "((?<!\\d))([0-3][0-9]|[1-9])(?=(日|号))"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.tp.tunit[2] = int(match.group())
            # 处理倾向于未来时间的情况
            self.preferFuture(2)
            self.time_extract_identity['D'] = self.exp_time[match.start():match.end() + 1]

    def norm_sethour(self):
        """
        时-规范化方法：该方法识别时间表达式单元的时字段
        :return:
        """
        rule = "(?<!(周|星期))([0-2]?[0-9])(?=(点|时))"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.tp.tunit[3] = int(match.group())
            # 处理倾向于未来时间的情况
            self.preferFuture(3)
            self.isAllDayTime = False
            self.time_extract_identity['H'] = self.exp_time[match.start():match.end() + 1]

        # * 对关键字：早（包含早上/早晨/早间），上午，中午,午间,下午,午后,晚上,傍晚,晚间,晚,pm,PM的正确时间计算
        # * 规约：
        # * 1.中午/午间0-10点视为12-22点
        # * 2.下午/午后0-11点视为12-23点
        # * 3.晚上/傍晚/晚间/晚1-11点视为13-23点，12点视为0点
        # * 4.0-11点pm/PM视为12-23点
        rule = "凌晨"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            if self.tp.tunit[3] == -1: # 增加对没有明确时间点，只写了“凌晨”这种情况的处理
                self.tp.tunit[3] = RangeTimeEnum.day_break
                # 处理倾向于未来时间的情况
                self.preferFuture(3)
                self.isAllDayTime = False
                self.time_extract_identity['H'] = match.group()

        rule = "早上|早晨|早间|晨间|今早|明早|1早"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            if self.tp.tunit[3] == -1:  # 增加对没有明确时间点，只写了“早上/早晨/早间”这种情况的处理
                self.tp.tunit[3] = RangeTimeEnum.early_morning
                # 处理倾向于未来时间的情况
                self.preferFuture(3)
                self.isAllDayTime = False
                self.time_extract_identity['H'] = match.group()

        rule = "上午"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            if self.tp.tunit[3] == -1:  # 增加对没有明确时间点，只写了“上午”这种情况的处理
                self.tp.tunit[3] = RangeTimeEnum.morning
                # 处理倾向于未来时间的情况
                self.preferFuture(3)
                self.isAllDayTime = False
                self.time_extract_identity['H'] = match.group()

        rule = "(中午)|(午间)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            if 0 <= self.tp.tunit[3] <= 10:
                self.tp.tunit[3] += 12
            if self.tp.tunit[3] == -1:  # 增加对没有明确时间点，只写了“中午/午间”这种情况的处理
                self.tp.tunit[3] = RangeTimeEnum.noon
            # 处理倾向于未来时间的情况
            self.preferFuture(3)
            self.isAllDayTime = False
            self.time_extract_identity['H'] = match.group() + self.time_extract_identity['H']

        rule = "(下午)|(午后)|(pm)|(PM)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            if 0 <= self.tp.tunit[3] <= 11:
                self.tp.tunit[3] += 12
            if self.tp.tunit[3] == -1:  # 增加对没有明确时间点，只写了“下午|午后”这种情况的处理
                self.tp.tunit[3] = RangeTimeEnum.afternoon
            # 处理倾向于未来时间的情况
            self.preferFuture(3)
            self.isAllDayTime = False
            self.time_extract_identity['H'] = match.group() + self.time_extract_identity['H']

        rule = "下班"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match:
            if not self.tp.tunit[3] == -1:
                # 判断为下午的时间
                if 0 < self.tp.tunit[3] < 12:
                    self.tp.tunit[3] += 12
            else:
                self.tp.tunit[3] = RangeTimeEnum.gooffwork
            self.preferFuture(3)
            self.isAllDayTime = False
            if re.search(rule + '[前后]?$', self.exp_time):
                self.time_extract_identity['H'] += match.group()
            else:
                self.time_extract_identity['H'] = match.group() + self.time_extract_identity['H']

        rule = "(上午|中午)下班"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.tp.tunit[3] = 12
            self.preferFuture(3)
            self.isAllDayTime = False
            self.time_extract_identity['H'] = match.group() + self.time_extract_identity['H']

        rule = "晚上|夜间|夜里|今晚|明晚|昨晚"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            if 0 <= self.tp.tunit[3] <= 10:
                self.tp.tunit[3] += 12
            elif self.tp.tunit[3] == 12:
                self.tp.tunit[3] = 0
            elif self.tp.tunit[3] == -1:  # 增加对没有明确时间点，只写了“下午|午后”这种情况的处理
                self.tp.tunit[3] = RangeTimeEnum.lateNight
            # 处理倾向于未来时间的情况
            self.preferFuture(3)
            self.isAllDayTime = False
            self.time_extract_identity['D'] = match.group()
            self.time_extract_identity['H'] = match.group() + self.time_extract_identity['H']

    def norm_setminute(self):
        """
        分-规范化方法：该方法识别时间表达式单元的分字段
        :return:
        """
        rule = "([0-9]+(?=分(?!钟)))|((?<=((?<!小)[点时]))[0-5]?[0-9](?!刻))"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            if match.group() != '':
                self.tp.tunit[4] = int(match.group())
                # 处理倾向于未来时间的情况
                # self.preferFuture(4)
                self.isAllDayTime = False
                self.time_extract_identity['m'] = re.search("([0-9]+分(?!钟))|((?<=((?<!小)[点时]))[0-5]?[0-9](?!刻))",
                                                            self.exp_time).group()

        # 加对一刻，半，3刻的正确识别（1刻为15分，半为30分，3刻为45分）
        rule = "(?<=[点时])[1一]刻(?!钟)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.tp.tunit[4] = 15
            # 处理倾向于未来时间的情况
            # self.preferFuture(4)
            self.isAllDayTime = False
            self.time_extract_identity['m'] = match.group()

        rule = "(?<=[点时])半"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.tp.tunit[4] = 30
            # 处理倾向于未来时间的情况
            self.preferFuture(4)
            self.isAllDayTime = False
            self.time_extract_identity['m'] = match.group()

        rule = "(?<=[点时])[3三]刻(?!钟)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.tp.tunit[4] = 45
            # 处理倾向于未来时间的情况
            # self.preferFuture(4)
            self.isAllDayTime = False
            self.time_extract_identity['m'] = match.group()

    def norm_setsecond(self):
        """
        添加了省略“秒”说法的时间：如17点15分32
        :return:
        """
        rule = "([0-9]+(?=秒))|((?<=分)[0-5]?[0-9])"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.tp.tunit[5] = int(match.group())
            self.isAllDayTime = False
            self.time_extract_identity['s'] = re.search("([0-9]+秒)|((?<=分)[0-5]?[0-9])", self.exp_time).group()

    def norm_setSpecial(self):
        """
        特殊形式的规范化方法-该方法识别特殊形式的时间表达式单元的各个字段
        :return:
        """
        rule = "(?<!(周|星期))([0-2]?[0-9]):[0-5]?[0-9]:[0-5]?[0-9]"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            tmp_target = match.group()
            tmp_parser = tmp_target.split(":")
            self.tp.tunit[3] = int(tmp_parser[0])
            self.tp.tunit[4] = int(tmp_parser[1])
            self.tp.tunit[5] = int(tmp_parser[2])
            # 处理倾向于未来时间的情况
            self.preferFuture(3)
            self.isAllDayTime = False
            self.time_extract_identity['H'] = tmp_target
            self.time_extract_identity['m'] = tmp_target
            self.time_extract_identity['s'] = tmp_target
        else:
            rule = "(?<!(周|星期))([0-2]?[0-9]):[0-5]?[0-9]"
            pattern = re.compile(rule)
            match = pattern.search(self.exp_time)
            if match is not None:
                tmp_target = match.group()
                tmp_parser = tmp_target.split(":")
                self.tp.tunit[3] = int(tmp_parser[0])
                self.tp.tunit[4] = int(tmp_parser[1])
                # 处理倾向于未来时间的情况
                self.preferFuture(3)
                self.isAllDayTime = False
                self.time_extract_identity['H'] = tmp_target
                self.time_extract_identity['m'] = tmp_target

        # 处理如：2018-01-01、18-01-01
        rule = "[0-9]?[0-9]?[0-9]{2}-((10)|(11)|(12)|(0?[1-9]))-((?<!\\d))([0-3][0-9]|0?[1-9])"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            tmp_target = match.group()
            tmp_parser = tmp_target.split("-")
            self.tp.tunit[0] = int(tmp_parser[0])
            self.tp.tunit[1] = int(tmp_parser[1])
            self.tp.tunit[2] = int(tmp_parser[2])
            self.time_extract_identity['Y'] = tmp_target
            self.time_extract_identity['M'] = tmp_target
            self.time_extract_identity['D'] = tmp_target

        # 处理如：10/1/2018
        rule = "((10)|(11)|(12)|(0?[1-9]))/((?<!\\d))([0-3][0-9]|0?[1-9])/[0-9]?[0-9]?[0-9]{2}"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            tmp_target = match.group()
            tmp_parser = tmp_target.split("/")
            self.tp.tunit[1] = int(tmp_parser[0])
            self.tp.tunit[2] = int(tmp_parser[1])
            self.tp.tunit[0] = int(tmp_parser[2])
            self.time_extract_identity['Y'] = tmp_target
            self.time_extract_identity['M'] = tmp_target
            self.time_extract_identity['D'] = tmp_target

        # 处理如：2018/01/01
        rule = "(\d+/((10)|(11)|(12)|(0?[1-9]))/([0-3][0-9]|0?[1-9])(?!\d))"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            tmp_target = match.group()
            tmp_parser = tmp_target.split("/")
            self.tp.tunit[0] = int(tmp_parser[0])
            self.tp.tunit[1] = int(tmp_parser[1])
            self.tp.tunit[2] = int(tmp_parser[2])
            self.time_extract_identity['Y'] = tmp_target
            self.time_extract_identity['M'] = tmp_target
            self.time_extract_identity['D'] = tmp_target

        #处理如：2018.01.01
        rule = "[0-9]?[0-9]?[0-9]{2}\\.((10)|(11)|(12)|(0?[1-9]))\\.((?<!\\d))([0-3][0-9]|[1-9])"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            tmp_target = match.group()
            tmp_parser = tmp_target.split(".")
            self.tp.tunit[0] = int(tmp_parser[0])
            self.tp.tunit[1] = int(tmp_parser[1])
            self.tp.tunit[2] = int(tmp_parser[2])
            self.time_extract_identity['Y'] = tmp_target
            self.time_extract_identity['M'] = tmp_target
            self.time_extract_identity['D'] = tmp_target

        # 处理格式如：20180101
        rule = '((?!<\d)[12]\d{3}((10)|(11)|(12)|(0[1-9]))([0-3][0-9]|0[1-9])(?!\d))'
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            tmp_target = match.group()
            self.tp.tunit[0] = int(tmp_target[:4])
            self.tp.tunit[1] = int(tmp_target[4:6])
            self.tp.tunit[2] = int(tmp_target[6:])
            self.time_extract_identity['Y'] = tmp_target
            self.time_extract_identity['M'] = tmp_target
            self.time_extract_identity['D'] = tmp_target

    def norm_setBaseRelated(self):
        """
        设置以上文时间为基准的时间偏移计算
        :return:
        """
        cur = arrow.get(self.normalizer.timeBase, "YYYY-M-D-H-m-s")
        flag = [False, False, False, False, False]

        rule = "\\d+(?=分钟[以之]?前)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[4] = True
            minute = int(match.group())
            cur = cur.shift(minutes=-minute)
            self.time_extract_identity['m'] = re.search("\\d+分钟[以之]?前", self.exp_time).group()

        rule = "\\d+(?=分钟[以之]?后)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[4] = True
            minute = int(match.group())
            cur = cur.shift(minutes=minute)
            self.time_extract_identity['m'] = re.search("\\d+分钟[以之]?后", self.exp_time).group()

        rule = "\\d+(?=(个)?小时[以之]?前)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[3] = True
            hour = int(match.group())
            cur = cur.shift(hours=-hour)
            self.time_extract_identity['H'] = re.search("\\d+(个)?小时[以之]?前", self.exp_time).group()

        rule = "\\d+(?=(个)?小时[以之]?后)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[3] = True
            hour = int(match.group())
            cur = cur.shift(hours=hour)
            self.time_extract_identity['H'] = re.search("\\d+(个)?小时[以之]?后", self.exp_time).group()

        rule = "\\d+(?=天[以之]?前)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            day = int(match.group())
            cur = cur.shift(days=-day)
            self.time_extract_identity['D'] = re.search("\\d+天[以之]?前", self.exp_time).group()

        rule = "\\d+(?=天[以之]?后)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            day = int(match.group())
            cur = cur.shift(days=day)
            self.time_extract_identity['D'] = re.search("\\d+天[以之]?后", self.exp_time).group()

        rule = "\\d+(?=(个)?月[以之]?前)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[1] = True
            month = int(match.group())
            cur = cur.shift(months=-month)
            self.time_extract_identity['M'] = re.search("\\d+(个)?月[以之]?前", self.exp_time).group()

        rule = "\\d+(?=(个)?月[以之]?后)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[1] = True
            month = int(match.group())
            cur = cur.shift(months=month)
            self.time_extract_identity['M'] = re.search("\\d+(个)?月[以之]?后", self.exp_time).group()

        rule = "\\d+(?=年[以之]?前)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[0] = True
            year = int(match.group())
            cur = cur.shift(years=-year)
            self.time_extract_identity['Y'] = re.search("\\d+年[以之]?前", self.exp_time).group()

        rule = "\\d+(?=年[以之]?后)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[0] = True
            year = int(match.group())
            cur = cur.shift(years=year)
            self.time_extract_identity['Y'] = re.search("\\d+年[以之]?后", self.exp_time).group()


        if flag[0] or flag[1] or flag[2] or flag[3] or flag[4]:
            self.tp.tunit[0] = int(cur.year)
        if flag[1] or flag[2] or flag[3] or flag[4]:
            self.tp.tunit[1] = int(cur.month)
        if flag[2] or flag[3] or flag[4]:
            self.tp.tunit[2] = int(cur.day)
        if flag[3] or flag[4]:
            self.tp.tunit[3] = int(cur.hour)
        if flag[4]:
            self.tp.tunit[4] = int(cur.minute)

    # todo 时间长度相关
    def norm_setSpanRelated(self):
        """
        设置时间长度相关的时间表达式
        :return:
        """
        rule = "\\d+(?=个月(?![以之]?[前后]))"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.normalizer.isTimeSpan = True
            month = int(match.group())
            self.tp.tunit[1] = int(month)
            self.time_extract_identity['M'] = re.search("\\d+个月(?![以之]?[前后])", self.exp_time).group()

        rule = "\\d+(?=天(?![以之]?[前后]))"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.normalizer.isTimeSpan = True
            day = int(match.group())
            self.tp.tunit[2] = int(day)
            self.time_extract_identity['D'] = re.search("\\d+天(?![以之]?[前后])", self.exp_time).group()

        rule = "\\d+(?=(个)?小时(?![以之]?[前后]))"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.normalizer.isTimeSpan = True
            hour = int(match.group())
            self.tp.tunit[3] = int(hour)
            self.time_extract_identity['H'] = re.search("\\d+(个)?小时(?![以之]?[前后])", self.exp_time).group()

        rule = "\\d+(?=分钟(?![以之]?[前后]))"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.normalizer.isTimeSpan = True
            minute = int(match.group())
            self.tp.tunit[4] = int(minute)
            self.time_extract_identity['m'] = re.search("\\d+分钟(?![以之]?[前后])", self.exp_time).group()

        rule = "\\d+(?=秒钟(?![以之]?[前后]))"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.normalizer.isTimeSpan = True
            second = int(match.group())
            self.tp.tunit[5] = int(second)
            self.time_extract_identity['s'] = re.search("\\d+秒钟(?![以之]?[前后])", self.exp_time).group()

        rule = "\\d+(?=(个)?(周|星期|礼拜)(?![以之]?[前后]))"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            self.normalizer.isTimeSpan = True
            week = int(match.group())
            if self.tp.tunit[2] == -1:
                self.tp.tunit[2] = 0
            self.tp.tunit[2] += int(week*7)
            self.time_extract_identity['D'] = re.search("\\d+(个)?(周|星期|礼拜)(?![以之]?[前后])", self.exp_time).group()

    # todo 节假日相关
    def norm_setHoliday(self):
        rule = "(清明)|(青年节)|(教师节)|(中元节)|(端午)|(劳动节)|(7夕)|(建党节)|(建军节)|(中和节)|(圣诞)|(中秋)|(春节)|(元宵)|(航海日)|(儿童节)|(国庆)|(植树节)|(元旦)|(重阳节)|(妇女节)|(记者节)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            if self.tp.tunit[0] == -1:
                self.tp.tunit[0] = int(self.normalizer.timeBase.split('-')[0])
            holi = match.group()
            if '节' not in holi:
                holi += '节'
            date = [-1, -1]
            if holi in self.normalizer.holi_solar:
                date = self.normalizer.holi_solar[holi].split('-')
            elif holi in self.normalizer.holi_lunar:
                date = self.normalizer.holi_lunar[holi].split('-')
                lunar = get_solar_date(self.tp.tunit[0], int(date[0]), int(date[1]))
                date[0] = lunar['month']
                date[1] = lunar['day']
            else:
                lunar = get_holi_date(self.tp.tunit[0], holi)
                date[0] = lunar['month']
                date[1] = lunar['day']
            self.tp.tunit[1] = int(date[0])
            self.tp.tunit[2] = int(date[1])
            self.time_extract_identity['M'] = match.group()
            self.time_extract_identity['D'] = match.group()


    def norm_setCurRelated(self):
        """
        设置当前时间相关的时间表达式
        :return:
        """
        cur = arrow.get(self.normalizer.timeBase, "YYYY-M-D-H-m-s")
        flag = [False, False, False]

        rule = "前年"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[0] = True
            cur = cur.shift(years=-2)
            self.time_extract_identity['Y'] = match.group()

        rule = "去年"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[0] = True
            cur = cur.shift(years=-1)
            self.time_extract_identity['Y'] = match.group()

        rule = "今年"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[0] = True
            cur = cur.shift(years=0)
            self.time_extract_identity['Y'] = match.group()

        rule = "明年"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[0] = True
            cur = cur.shift(years=1)
            self.time_extract_identity['Y'] = match.group()

        rule = "后年"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[0] = True
            cur = cur.shift(years=2)
            self.time_extract_identity['Y'] = match.group()

        rule = "上(个)?月"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[1] = True
            cur = cur.shift(months=-1)
            self.time_extract_identity['M'] = match.group()

        rule = "(本|这个)月"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[1] = True
            cur = cur.shift(months=0)
            self.time_extract_identity['M'] = match.group()

        rule = "下(个)?月"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[1] = True
            cur = cur.shift(months=1)
            self.time_extract_identity['M'] = match.group()

        rule = "大前天"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            cur = cur.shift(days=-3)
            self.time_extract_identity['D'] = match.group()

        rule = "(?<!大)前天"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            cur = cur.shift(days=-2)
            self.time_extract_identity['D'] = match.group()

        rule = "昨"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            cur = cur.shift(days=-1)
            self.time_extract_identity['D'] = match.group()

        rule = "今(?!年)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            cur = cur.shift(days=0)
            self.time_extract_identity['D'] = self.exp_time[match.start():match.end() + 1]

        rule = "明(?!年)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            cur = cur.shift(days=1)
            self.time_extract_identity['D'] = self.exp_time[match.start():match.end() + 1]

        rule = "(?<!大)后天"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            cur = cur.shift(days=2)
            self.time_extract_identity['D'] = match.group()

        rule = "大后天"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            cur = cur.shift(days=3)
            self.time_extract_identity['D'] = match.group()

        # todo 补充星期相关的预测 done
        rule = "(?<=(上上个?(周|星期|礼拜)))[1-7]?"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            try:
                week = int(match.group())
            except:
                week = 1
            week -= 1
            span = week - cur.weekday()
            cur = cur.replace(weeks=-2, days=span)
            self.time_extract_identity['D'] = re.search("(上上个?(周|星期|礼拜))[1-7]?", self.exp_time).group()

        rule = "(?<=((?<!上)上个?(周|星期|礼拜)))[1-7]?"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            try:
                week = int(match.group())
            except:
                week = 1
            week -= 1
            span = week - cur.weekday()
            cur = cur.replace(weeks=-1, days=span)
            self.time_extract_identity['D'] = re.search("((?<!上)上个?(周|星期|礼拜))[1-7]?", self.exp_time).group()

        rule = "(?<=([这本]个?(周|星期|礼拜)))[1-7]"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            try:
                week = int(match.group())
            except:
                week = 1
            week -= 1
            span = week - cur.weekday()
            cur = cur.replace(days=span)
            self.time_extract_identity['D'] = re.search("([这本]个?(周|星期|礼拜))[1-7]", self.exp_time).group()

        rule = "(?<=((?<!下)下个?(周|星期|礼拜)))[1-7]?"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            try:
                week = int(match.group())
            except:
                week = 1
            week -= 1
            span = week - cur.weekday()
            cur = cur.replace(weeks=1, days=span)
            self.time_extract_identity['D'] = re.search("((?<!下)下个?(周|星期|礼拜))[1-7]?", self.exp_time).group()

        rule = "(?<=(下下个?(周|星期|礼拜)))[1-7]?"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            try:
                week = int(match.group())
            except:
                week = 1
            week -= 1
            span = week - cur.weekday()
            cur = cur.replace(weeks=2, days=span)
            self.time_extract_identity['D'] = re.search("(下下个?(周|星期|礼拜))[1-7]?", self.exp_time).group()

        rule = "(?<=((?<!(上|下|个|这|本|[0-9]))(周|星期|礼拜)))[1-7]"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            try:
                week = int(match.group())
            except:
                week = 1
            week -= 1
            span = week - cur.weekday()
            cur = cur.replace(days=span)
            # 处理未来时间
            # cur = self.preferFutureWeek(week, cur)
            self.time_extract_identity['D'] = re.search("((?<!(上|下|个|这|本|[0-9]))(周|星期|礼拜))[1-7]", self.exp_time).group()


        if flag[0] or flag[1] or flag[2]:
            self.tp.tunit[0] = int(cur.year)
        if flag[1] or flag[2]:
            self.tp.tunit[1] = int(cur.month)
        if flag[2]:
            self.tp.tunit[2] = int(cur.day)

    def norm_setHarfRelated(self):
        """
        设置以上文时间为基准的时间偏移计算
        :return:
        """
        cur = arrow.get(self.normalizer.timeBase, "YYYY-M-D-H-m-s")
        flag = [False, False, False, False, False]

        rule = "(半(个)?小时[以之]?前)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[4] = True
            cur = cur.shift(minutes=-30)
            self.time_extract_identity['H'] = match.group()

        rule = "(过半(个)?小时)|(半(个)?小时[以之]?后)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[4] = True
            cur = cur.shift(minutes=30)
            self.time_extract_identity['H'] = match.group()

        rule = "(半天[以之]?前)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[3] = True
            cur = cur.shift(hours=-12)
            self.time_extract_identity['D'] = match.group()

        rule = "(过半天)|(半天[以之]?后)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[3] = True
            cur = cur.shift(hours=12)
            self.time_extract_identity['H'] = match.group()

        rule = "(半(个)?月[以之]?前)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            month = int(match.group())
            cur = cur.shift(days=-15)
            self.time_extract_identity['M'] = match.group()

        rule = "(过半(个)?月)|(半(个)?月[以之]?后)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[2] = True
            cur = cur.shift(days=15)
            self.time_extract_identity['M'] = match.group()

        rule = "(半年[以之]?前)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[1] = True
            cur = cur.shift(months=-6)
            self.time_extract_identity['Y'] = match.group()

        rule = "(过半年)|(半年[以之]?后)"
        pattern = re.compile(rule)
        match = pattern.search(self.exp_time)
        if match is not None:
            flag[1] = True
            cur = cur.shift(months=6)
            self.time_extract_identity['Y'] = match.group()


        if flag[1] or flag[2] or flag[3] or flag[4]:
            self.tp.tunit[0] = int(cur.year)
            self.tp.tunit[1] = int(cur.month)
        if flag[2] or flag[3] or flag[4]:
            self.tp.tunit[2] = int(cur.day)
        if flag[3] or flag[4]:
            self.tp.tunit[3] = int(cur.hour)
        if flag[4]:
            self.tp.tunit[4] = int(cur.minute)

    def norm_spanTime(self):
        '''
        正则化跨度时间
        :return:
        '''
        if self.exp_time == '今年':
            pass



    def modifyTimeBase(self):
        """
        该方法用于更新timeBase使之具有上下文关联性
        :return:
        """
        if not self.normalizer.isTimeSpan:
            time_grid = self.normalizer.timeBase.split('-')
            arr = []
            for i in range(0, 6):
                if self.tp.tunit[i] == -1:
                    arr.append(str(time_grid[i]))
                else:
                    arr.append(str(self.tp.tunit[i]))
            ## 为什么注销？
            # self.normalizer.timeBase = '-'.join(arr)

    def preferFutureWeek(self, weekday, cur):
        # 1. 确认用户选项
        if not self.normalizer.isPreferFuture:
            return cur
        # 2. 检查被检查的时间级别之前，是否没有更高级的已经确定的时间，如果有，则不进行处理.
        for i in range(0, 2):
            if self.tp.tunit[i] != -1:
                return cur
        # 获取当前是在周几，如果识别到的时间小于当前时间，则识别时间为下一周
        tmp = arrow.get(self.normalizer.timeBase, "YYYY-M-D-H-m-s")
        curWeekday = tmp.weekday()
        if curWeekday > weekday:
            cur = cur.shift(days=7)
        return cur

    def preferFuture(self, checkTimeIndex):
        """
        如果用户选项是倾向于未来时间，检查checkTimeIndex所指的时间是否是过去的时间，如果是的话，将大一级的时间设为当前时间的+1。
        如在晚上说“早上8点看书”，则识别为明天早上;
        12月31日说“3号买菜”，则识别为明年1月的3号。
        :param checkTimeIndex: _tp.tunit时间数组的下标
        :return:
        """
        # 1. 检查被检查的时间级别之前，是否没有更高级的已经确定的时间，如果有，则不进行处理.
        for i in range(0, checkTimeIndex):
            if self.tp.tunit[i] != -1:
                return
        # 2. 根据上下文补充时间
        self.checkContextTime(checkTimeIndex)
        # 3. 根据上下文补充时间后再次检查被检查的时间级别之前，是否没有更高级的已经确定的时间，如果有，则不进行倾向处理.
        for i in range(0, checkTimeIndex):
            if self.tp.tunit[i] != -1:
                return
        # 4. 确认用户选项
        if not self.normalizer.isPreferFuture:
            return
        # 5. 获取当前时间，如果识别到的时间小于当前时间，则将其上的所有级别时间设置为当前时间，并且其上一级的时间步长+1
        time_arr = self.normalizer.timeBase.split('-')
        cur = arrow.get(self.normalizer.timeBase, "YYYY-M-D-H-m-s")
        cur_unit = int(time_arr[checkTimeIndex])
        if cur_unit < self.tp.tunit[checkTimeIndex]:
            return
        # 准备增加的时间单位是被检查的时间的上一级，将上一级时间+1
        # cur = self.addTime(cur, checkTimeIndex - 1)
        time_arr = cur.format("YYYY-M-D-H-m-s").split('-')
        for i in range(0, checkTimeIndex):
            self.tp.tunit[i] = int(time_arr[i])
            # if i == 1:
            #     self.tp.tunit[i] += 1

    def checkContextTime(self, checkTimeIndex):
        """
        根据上下文时间补充时间信息
        :param checkTimeIndex:
        :return:
        """
        for i in range(0, checkTimeIndex):
            if self.tp.tunit[i] == -1 and self.tp_origin.tunit[i] != -1:
                self.tp.tunit[i] = self.tp_origin.tunit[i]

        # 在处理小时这个级别时，如果上文时间是下午的且下文没有主动声明小时级别以上的时间，则也把下文时间设为下午
        if self.isFirstTimeSolveContext is True and checkTimeIndex == 3 and self.tp_origin.tunit[
            checkTimeIndex] >= 12 and self.tp.tunit[checkTimeIndex] < 12:
            self.tp.tunit[checkTimeIndex] += 12
        self.isFirstTimeSolveContext = False

    def addTime(self, cur, fore_unit):
        if fore_unit == 0:
            cur = cur.shift(years=1)
        elif fore_unit == 1:
            cur = cur.shift(months=1)
        elif fore_unit == 2:
            cur = cur.shift(days=1)
        elif fore_unit == 3:
            cur = cur.shift(hours=1)
        elif fore_unit == 4:
            cur = cur.shift(minutes=1)
        elif fore_unit == 5:
            cur = cur.shift(seconds=1)
        return cur
