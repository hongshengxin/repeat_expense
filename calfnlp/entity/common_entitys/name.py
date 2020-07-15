#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/7/15 下午5:18
# @Author  : fugang_le
# @Software: PyCharm

import re

from calfnlp.const import ResourceFile
from calfnlp.entity.common_entitys.entitys_template import entitys_template

NAME_POS = ResourceFile.POS_TABLE['nr']
NAME_FLAG = 'nr'


class CommonName:
    '''
    jieba分出nr、@人名
    '''
    AT_PATTERN = re.compile('(?<=@)([\\u4e00-\\u9fa5]{2,4})(?=([^\\u4e00-\\u9fa5]|$))')

    @classmethod
    def parse(cls, pyloads, text):
        real_ppl = cls.AT_PATTERN.findall(text)
        names = [i[0] for i in real_ppl]

        for pyload in pyloads:
            words = pyload['cws']
            posstagers = pyload['pos']
            ners = pyload['ners']
            for i, ner in enumerate(ners):
                if (ner == "S-Nh" or posstagers[i] == "nh") and len(words[i]) > 1:
                    if i > 0 and len(posstagers[i]) <= 2 and posstagers[i - 1] == "nh" and len(words[i - 1]) == 1:
                        names.append(words[i - 1] + words[i])
                        continue

                    names.append(words[i].replace("@", ''))

        name_entitys = []
        for person in names:
            name_entitys.append(entitys_template(person, text, NAME_FLAG))

        return name_entitys


if __name__ == '__main__':
    from calfnlp.pyltp_server import PyLtp

    pyltp = PyLtp()
    pyltp.load_model_and_lexicon(['CWS', 'POS', "NER"])

    text = '给吴粤敏发个消息'
    pyloads = pyltp.seg_pos_ner(text)
    print(CommonName.parse(pyloads, text))
