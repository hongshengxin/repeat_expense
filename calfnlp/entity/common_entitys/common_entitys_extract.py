#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/6/28 下午5:35
# @Author  : fugang_le
# @Software: PyCharm


from calfnlp.entity.common_entitys.name import CommonName
from calfnlp.pyltp_server import PyLtp
from typing import Text

class CommonNameExtract:
    pyltp = PyLtp.get_ltp_service()

    @classmethod
    def common_name_extract(cls,text:Text):
        pyloads = cls.pyltp.seg_pos_ner(text)

        names = CommonName.parse(pyloads, text)
        # locations = CommonLocation.parse(pyloads, text)
        # times = CommonTime.parse(text)

        return names

# def common_entitys_extract(text):
#     '''
#     通用实体识别
#     :param tenant:
#     :param text:
#     :return:
#     '''
#     pyltp = PyLtp.get_ltp_service()
#     pyloads = pyltp.seg_pos_ner(text)
#
#     names = CommonName.parse(pyloads, text)
#     # locations = CommonLocation.parse(pyloads, text)
#     # times = CommonTime.parse(text)
#
#     return names


if __name__ == '__main__':
    # from nlpservice.core.tenantsegmenter import TenantSegmenter
    # segmenter = TenantSegmenter('123', [])
    # poss = segmenter.sentence_cut_pos("张刚明天下午三点去北京出差")
    print(common_entitys_extract("'报销人才招聘服务费：1、严克宇（产品总监），入职起支付百分之50的猎头服务费（转正后支付剩馀部分）；2、熊睿（Java开发工程师），1次性支付全部猎头服务费；3、钱婷婷（行政助理），入职起支付百分之50的猎头服务费（一个月后支付剩馀部分），需支付95900元；【全部人于6月已入职】'"))