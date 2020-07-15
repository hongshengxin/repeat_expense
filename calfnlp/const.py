# _*_ coding: UTF-8 _*_
'''
nlu/nlp相关常量定义

'''

import os

DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../calfdata/")

DICT_PATH = os.path.join(DATA_PATH, "dic/")
LTP_DATA_DIR = os.path.join(DATA_PATH, "pyltp/")
ENTITY_PATH = os.path.join(DATA_PATH, "dic/")

class ResourceFile(object):
    StopWords = os.path.join(DICT_PATH, "stopwords.dict")
    StopwordPunctuation = os.path.join(DICT_PATH, "stopwords_punct.dict")
    WordIDF = os.path.join(DICT_PATH, "jieba_idf.dict")
    GeneralSynonym = os.path.join(DICT_PATH, "synonym_general.dict")
    WordNetLemma = os.path.join(DICT_PATH, "wordnet_lemma_names.dict")

    cws_lexicon_path = os.path.join(ENTITY_PATH, 'pyltp_seg_dict.txt')
    pos_lexicon_path = os.path.join(ENTITY_PATH, 'pyltp_pos_dict.txt')

    cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
    pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
    ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`pos.model`
    par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
    srl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl.model')  # 语义角色标注模型目录路径，模型名称为'pisrl.model'。

    companey_file_path = os.path.join(DICT_PATH, "companey.txt")
    organization_file_path = os.path.join(DICT_PATH, "Organization-Names-Corpus.txt")

    POS_TABLE = {
        'ns': ['ns'],
        'nr': ['nr', 'nrfg', 'nrt']
    }




