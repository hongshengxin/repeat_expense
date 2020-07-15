import regex as re
import os

_ROOTPATH = os.path.dirname(os.path.abspath(__file__))
REGEX_PATH = _ROOTPATH + '/resource/re111.txt'

# 获取正则表达式
def get_pattern():
    chinese_num_pattern = '([零一二三四五六七八九十百千万])'
    year_pattern = '([0-9]?[0-9]?[0-9]{2})|' + chinese_num_pattern + '+'
    month_pattern = '((10)|(11)|(12)|(0?[1-9]))|' + chinese_num_pattern + '+'
    day_pattern = '([12][0-9]|3[01]|0?[1-9])|' + chinese_num_pattern + '+'
    week_pattern = '([一二三四五六七天日末]|[1-7])'
    hour_pattern = '[0-2]?[0-9]|' + chinese_num_pattern + '+'
    minute_pattern = '[0-5]?[0-9]|' + chinese_num_pattern + '+'
    second_pattern = '[0-5]?[0-9]|' + chinese_num_pattern + '+'

    with open(REGEX_PATH, 'r', encoding='utf-8') as fp:
        content = str(fp.read())

    # YEAR=年 MONTH=月 DAY=日 CN=中文数字
    content = content.replace('\n', '')
    content = content.replace('YEAR', year_pattern)
    content = content.replace('MONTH', month_pattern)
    content = content.replace('DAY', day_pattern)
    content = content.replace('CN', chinese_num_pattern)
    content = content.replace('WK', week_pattern)
    content = content.replace('HOUR', hour_pattern)
    content = content.replace('MINUTE', minute_pattern)
    content = content.replace('SEC', second_pattern)

    return content




# 测试正则表达式
def test_regular(sent):
    temp = []
    rpointer = 0
    endline = -1
    pattern = re.compile(get_pattern())
    match = pattern.finditer(sent)
    for m in match:
        the_data = m.group()
        print(the_data)
        mstart = m.start()
        mend = m.end()

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
        else:
            temp.append(the_data)
        endline = mend
        rpointer += 1
    print(temp)

if __name__ == '__main__':
    sent = '''过去三个月提交的单据'''
    test_regular(sent)