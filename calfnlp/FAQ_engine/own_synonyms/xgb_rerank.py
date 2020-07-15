#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-02-24 14:35
# @Author  : xinhongsheng

import xgboost as xgb
import os
from calfnlp.FAQ_engine.question_similarity.rankingstrategy import Similarity
from typing import Dict, Text, Any, List, Set
import pandas as pd
from calfnlp.const import DATA_PATH

xgb_model_path = os.path.join(DATA_PATH, 'faqdata/xgb3.model')
print(xgb_model_path)


class XgbRerank(object):

    tar = xgb.Booster(params={'nthread': 4}, model_file=xgb_model_path)
    similarity = Similarity()

    @classmethod
    def get_rerank_score(cls, lcs, diffL, jaccard, edit):
        '''

        :param words1:
        :param words2:
        :param question1:
        :param question2:
        :return:
        '''

        try:

            x_data = pd.Series([lcs, diffL, jaccard, edit],
                               index=["lcs_temp", "diffL_temp", "jaccard_temp", "edit_temp"])
            x_test = xgb.DMatrix(x_data)
            rerank_score = cls.tar.predict(x_test)
            return float(rerank_score[0])
        except Exception as e:

            raise e

    @classmethod
    def get_xgb_feature(cls, words1: List, words2: List) -> List[float]:
        '''
        得到相似度特征
        :param question1:
        :param question2:
        :return:
        '''
        lcs, diffL, jaccard = cls.similarity.get_sub_sim_score(words1, words2)

        return [lcs, diffL, jaccard]

    @classmethod
    def candi_senten_filter(cls, text: Text, similar_texts: Dict):

        res = []
        for index, sub_sens in similar_texts.items():
            edit_score = cls.similarity.comp_edit(text, sub_sens)

            res.append({"score": edit_score,
                        "sen": sub_sens,
                        "index": index})
        filter_dict = sorted(res, key=lambda x: x["score"], reverse=True)[:5]
        return filter_dict


if __name__ == '__main__':
    print(XgbRerank.get_rerank_score("如何申请休假", "如何申请"))
    print("kaish")
    print(XgbRerank.get_rerank_score("如何申请休假", "如何申请"))
    print("kaish")
