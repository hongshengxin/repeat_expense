#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/7/15 下午5:04
# @Author  : fugang_le
# @Software: PyCharm

import re

def template(start=0, end=0, text="", value="", entity='', confidence=1.0):
    entitys = {}
    entitys['start'] = start
    entitys['end'] = end
    entitys['text'] = text
    entitys['value'] = value
    entitys['entity'] = entity
    entitys['confidence'] = confidence
    return entitys

def entitys_template(word, text, flag, value='', confidence=1.0):
    match = re.search(word, text)
    if match:
        span = match.span()
    else:
        span = [0, 0]
    return template(start=span[0], end=span[1], value=value, text=word, entity=flag, confidence=confidence)