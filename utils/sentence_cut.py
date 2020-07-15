# -*- coding:utf-8 -*-

import threading
import jieba
import codecs
from calfnlp.const import ResourceFile


class SentenceCut():
    cut_tool = None

    def __init__(self):
        self.jieba = jieba
        self._lock = threading.Lock()
        self.stop_words = self.load_stop_words(ResourceFile.StopWords)

    def sentence_cut(self, question):
        with self._lock:
            wordList = self.jieba.cut(question)
        return wordList

    @classmethod
    def get_sentence_cut(cls):
        if cls.cut_tool:
            return cls.cut_tool
        cls.cut_tool = cls()
        return cls.cut_tool

    def sentence_cut_filter(self, sentence):

        if not sentence:
            return []
        word_list = self.sentence_cut(sentence)

        result = []

        for w in word_list:
            if w not in self.stop_words:
                result.append(w)

        return result

    def load_stop_words(self, file_path):
        f = codecs.open(file_path, 'r', encoding="utf-8")
        stop_words = [i.strip() for i in f.readlines()]
        stop_words.append(' ')
        stop_words.append('')
        return stop_words


if __name__ == '__main__':
    sen = SentenceCut()
    sen.load_stop_words()
