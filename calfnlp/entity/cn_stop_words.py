# _*_ coding: UTF-8 _*_
'''
停止词, 停止词符号类. 从字典文件中加载

'''
import io

from calfnlp.const import ResourceFile


class CNStopWords():
    with io.open(ResourceFile.StopWords, encoding='utf-8') as fin:
        _data = set([line.strip() for line in fin])

    @staticmethod
    def get():
        return CNStopWords._data


class CNStopwordPunctuation():
    with io.open(ResourceFile.StopwordPunctuation, encoding='utf-8') as fin:
        _data = set([line.strip() for line in fin])
        # _data = " ".join(_data).encode('utf8').split()

    @staticmethod
    def get():
        return CNStopwordPunctuation._data


if __name__ == '__main__':
    print('CNStopWords len:', len(CNStopWords._data))
    print('CNStopwordPunctuation len:', len(CNStopwordPunctuation._data), type(CNStopwordPunctuation._data))
    CNStopWords._data.update(CNStopwordPunctuation._data)
    print('CNStopWords len:', len(CNStopWords._data), type(CNStopWords._data))

    # from calf.util.punctuations import Punctuations
    # for s in Punctuations.AllPunc:
    #     if s not in CNStopWords._data:
    #         print s

    for s in CNStopWords._data:
        print(s, type(s))
        # if s not in CNStopwordPunctuation._data:
        #     print s, 'not in CNStopwordPunctuation'
    #
    # for s in CNStopwordPunctuation._data:
    #     if s not in CNStopWords._data:
    #         print s, 'not in CNStopWords'
