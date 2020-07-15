#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/23 13:22
# @Author  : zhm
# @File    : __init__.py
# @Software: PyCharm

# gunicorn -w 4  restful_api:app -b 0.0.0.0:6002 -k gevent --timeout=90  &