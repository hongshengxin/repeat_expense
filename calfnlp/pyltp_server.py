import os
from pyltp import SentenceSplitter
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import SementicRoleLabeller
from pyltp import NamedEntityRecognizer
from pyltp import Parser

from calfnlp.const import ResourceFile

class PyLtp:
    '''
    代号：
        分词 - cws
        词性标注 - pos
        命名实体识别 - ners
        依存句法 - pars
        角色语义标注 - roles
    '''
    pyltp_server = None

    def __init__(self):
        self.segmentor = Segmentor()
        self.postagger = Postagger()
        self.recognizer = NamedEntityRecognizer()
        self.parser = Parser()
        self.labeller = SementicRoleLabeller()

    def load_model_and_lexicon(self, ltp_type_list):
        for ltp_type in ltp_type_list:
            if ltp_type == 'CWS':
                self.segmentor.load_with_lexicon(ResourceFile.cws_model_path, ResourceFile.cws_lexicon_path)  # 加载模型
            elif ltp_type == 'POS':
                self.postagger.load_with_lexicon(ResourceFile.pos_model_path, ResourceFile.pos_lexicon_path)  # 加载模型
            elif ltp_type == 'NER':
                self.recognizer.load(ResourceFile.ner_model_path)  # 加载模型
            elif ltp_type == 'ALL':
                self.segmentor.load_with_lexicon(ResourceFile.cws_model_path, ResourceFile.cws_lexicon_path)  # 加载模型
                self.postagger.load_with_lexicon(ResourceFile.pos_model_path, ResourceFile.pos_lexicon_path)  # 加载模型
                self.recognizer.load(ResourceFile.ner_model_path)  # 加载模型
                self.parser.load(ResourceFile.par_model_path)
                self.labeller.load(ResourceFile.srl_model_path)

    # 分句，也就是将一片文本分割为独立的句子
    def sentence_splitter(self, sentence):
        sents = SentenceSplitter.split(sentence)  # 分句
        return sents

    # 分词
    def segment(self, sentence):
        words = list(self.segmentor.segment(sentence))  # 分词
        return words

    # 词性标注
    def posttagger(self, words):
        postags = list(self.postagger.postag(words))  # 词性标注
        return postags

    # 命名实体识别
    def ners(self, words, postags):
        netags = list(self.recognizer.recognize(words, postags))  # 命名实体识别
        return netags

    # 依存语义分析
    def parse(self, words, postags):
        arcs = self.parser.parse(words, postags)  # 句法分析
        return arcs

    # 角色标注
    def role_label(self, words, postags, arcs):
        roles = self.labeller.label(words, postags, arcs)  # 语义角色标注
        return roles

    def seg_pos(self, sentence):
        sents = SentenceSplitter.split(sentence)
        ltp_pyload = []

        for sent in sents:
            words = self.segment(sent)  # 分词
            postags = self.posttagger(words)  # 词性标注

            ltp_py = {}
            ltp_py['cws'] = words
            ltp_py['pos'] = postags

            ltp_pyload.append(ltp_py)

        return ltp_pyload

    def seg_pos_ner(self, sentence):
        sents = SentenceSplitter.split(sentence)
        ltp_pyload = []

        for sent in sents:
            words = self.segment(sent)  # 分词
            postags = self.posttagger(words)  # 词性标注
            netags = self.ners(words, postags)  # 命名实体识别

            ltp_py = {}
            ltp_py['cws'] = words
            ltp_py['pos'] = postags
            ltp_py['ners'] = netags

            ltp_py = self._conbine_ner(ltp_py)

            ltp_pyload.append(ltp_py)

        return ltp_pyload

    def _conbine_ner(self, ltp_py):
        '''
        合并实体
        :param ltp_py:
        :return:
        '''
        new_cws = []
        new_pos = []
        new_ner = []
        for word, pos, ner in zip(ltp_py['cws'], ltp_py['pos'], ltp_py['ners']):
            if str(ner).startswith('I-'):
                new_cws[-1] += word
            elif str(ner).startswith('E-'):
                new_cws[-1] += word
                new_pos[-1] = ner[-2:].lower()
                new_ner[-1] = ner.replace('E', 'S')
            else:
                new_cws.append(word)
                new_pos.append(pos)
                new_ner.append(ner)

        # 处理实体标注不是已E标签为结尾
        if new_ner:
            new_ner[-1] = new_ner[-1].replace('B', 'S') if new_ner[-1].startswith('B-') else new_ner[-1]
            new_ner[-1] = new_ner[-1].replace('I', 'S') if new_ner[-1].startswith('I-') else new_ner[-1]

        ltp_py = {}
        ltp_py['cws'] = new_cws
        ltp_py['pos'] = new_pos
        ltp_py['ners'] = new_ner

        return ltp_py

    # ltp pipeline
    def process(self, sentence):
        sents = SentenceSplitter.split(sentence)
        ltp_pyload = []

        for sent in sents:
            words = self.segment(sent)  # 分词
            tags = self.posttagger(words)  # 词性标注
            netags = self.ners(words, tags)  # 命名实体识别
            arcs = self.parse(words, tags)  # 依存句法识别
            roles = self.role_label(words, tags, arcs)  # 角色语义标注

            ltp_result = {}
            ltp_result['cws'] = words
            ltp_result['pos'] = tags
            ltp_result['ners'] = netags
            ltp_result['pars'] = arcs
            ltp_result['roles'] = roles

            ltp_pyload.append(ltp_result)

            # ---------------------------------------------------
            for word, postag, ner in zip(words, tags, netags):
                print(word + "/" + postag + "#" + ner, end='\n')
            print('\n')
            #
            for ind, word in enumerate(words):
                print(str(ind + 1) + ":" + word, end='\t')
            print()
            print('\t'.join("%d:%s:%d" % (ind + 1, arc.relation, arc.head) for ind, arc in enumerate(arcs)))
            print()
            for role in roles:
                print(words[role.index], "".join(
                    ["%s:(%s)" % (arg.name, ''.join(words[arg.range.start:arg.range.end + 1])) for arg in role.arguments]))
            # ---------------------------------------------------

        return ltp_pyload

    def release_model(self):
        self.segmentor.release()
        self.postagger.release()
        self.recognizer.release()
        self.parser.release()
        self.labeller.release()

    @classmethod
    def get_ltp_service(cls):
        if cls.pyltp_server:
            return cls.pyltp_server
        cls.pyltp_server = cls()
        cls.pyltp_server.load_model_and_lexicon(['CWS', 'POS', 'NER'])
        return cls.pyltp_server

if __name__ == '__main__':
    for i in range(10):
        ltp = PyLtp.get_ltp_service()
        ltp_result = ltp.seg_pos_ner('''北京''')
        # ltp.release_model()
        # print('\t'.join("%d:%s:%d" % (i1nd + 1, arc.relation, arc.head) for ind, arc in enumerate(ltp_result[0]['pars'])))
        print(ltp_result)
