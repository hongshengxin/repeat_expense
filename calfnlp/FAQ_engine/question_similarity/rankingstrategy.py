# -*- coding: utf-8 -*-
'''
文本相似性计算工具类
'''

import math

from calfnlp.entity.word_idf import WordIDF
from calfnlp.entity.synonym import Synonym


def comp_cosine(w1, w2):
    w1 = normalize(w1)
    w2 = normalize(w2)
    union_dict = {}
    for item in w1:
        union_dict[item[0]] = 0
    for item in w2:
        if item[0] in union_dict:
            union_dict[item[0]] = item[1]
        else:
            union_dict[item[0]] = 0
    for item in w1:
        if not union_dict[item[0]] == 0:
            union_dict[item[0]] *= item[1]
    return norm_1(union_dict.items())


def normalize(w):
    norm = norm_2(w)
    w_n = []
    for item in w:
        item_n = (item[0], item[1] / norm)
        w_n.append(item_n)
    return w_n


def norm_1(w):
    norm = 0.0
    for item in w:
        norm += item[1]
    return norm


def norm_2(w):
    norm = 0.0
    for item in w:
        norm += item[1] ** 2
    norm = math.sqrt(norm)
    return norm


def substitute_to_synonyum(word_list, tenant_id=None):
    result = []
    for w in word_list:
        result.append(Synonym.get(tenant_id, w) or w)
    return result


rank_weight = [0.17, 0.07, 0.21, 0.38, 0.15, 0.02, 0.0]
lcs_weight = rank_weight[0]     # 最长公共子串
wmd_weight = rank_weight[1]     # 词移距离wmd，未实现
jaccard_weight = rank_weight[2] # jaccard相似度
cos_weight = rank_weight[3]     # 余弦相似度
edit_weight = rank_weight[4]    # 编辑距离
diffL_weight = rank_weight[5]   # 文本长度差
es_weight = rank_weight[6]      # es计算值


class Similarity:

    def __init__(self, keywords=None):
        if keywords and isinstance(keywords, set):
            self.keywords = keywords
        else:
            if isinstance(keywords, list):
                self.keywords = set(keywords)
            else:
                self.keywords = set()

    # 最长公共子串(the longest common substring)
    def find_lcs_len(self, s1, s2):
        if len(s1) == 0 or len(s2) == 0:  # 如果有一个list全是空的，说明里面全是停止词,直接返回0相似度
            return 0

        m = [[0 for _ in s2] for _ in s1]
        for p1 in range(len(s1)):
            for p2 in range(len(s2)):
                if s1[p1] == s2[p2]:
                    if p1 == 0 or p2 == 0:
                        m[p1][p2] = 1
                    else:
                        m[p1][p2] = m[p1 - 1][p2 - 1] + 1
                elif m[p1 - 1][p2] < m[p1][p2 - 1]:
                    m[p1][p2] = m[p1][p2 - 1]
                else:
                    m[p1][p2] = m[p1 - 1][p2]

        a = m[-1][-1]
        b = max(len(s1), len(s2))
        return a / float(b)

    # 文本长度差（值越大，长度越接近）
    def diff_len(self, s1, s2):
        len_s1 = len(s1)
        len_s2 = len(s2)

        if len_s2 == 0 or len_s1 == 0:
            return 0

        return 1 - abs(len_s1 - len_s2) / float(max(len_s1, len_s2))

    # jaccard系数
    def comp_jaccard(self, w1, w2):
        if len(w1) == 0 or len(w2) == 0:
            return 0

        w1 = set(w1)
        w2 = set(w2)

        return len(w1 & w2) / len(w1 | w2)

    # 编辑距离
    def comp_edit(self, first, second):
        if len(first) == 0 or len(second) == 0:
            return 0

        if len(first) > len(second):
            first, second = second, first
        if len(first) == 0 or len(second) == 0:
            return 0

        first_length = len(first) + 1
        second_length = len(second) + 1
        distance_matrix = [list(range(second_length)) for x in range(first_length)]

        for i in range(1, first_length):
            for j in range(1, second_length):
                deletion = distance_matrix[i - 1][j] + 1
                insertion = distance_matrix[i][j - 1] + 1
                substitution = distance_matrix[i - 1][j - 1]
                if first[i - 1] != second[j - 1]:
                    substitution += 1
                distance_matrix[i][j] = min(insertion, deletion, substitution)
        return 1 - distance_matrix[first_length - 1][second_length - 1] / float(second_length - 1)

    # 余弦距离
    def comp_cosine_main(self, w1, w2, keywords=None, idf_dict=None):
        # 输入q和a，分词后通过idf得到权重，导入CompCosine中

        w1 = list(set(w1))
        w2 = list(set(w2))

        l1 = []
        l2 = []

        for x in w1:
            if x in keywords:
                l1.append((x, 20))
            elif x in idf_dict:
                l1.append((x, idf_dict[x]))
            else:
                l1.append((x, 1))

        for y in w2:
            if y in keywords:
                l2.append((y, 20))
            elif y in idf_dict:
                l2.append((y, idf_dict[y]))
            else:
                l2.append((y, 1))

        return comp_cosine(l1, l2)

    def get_sim_score(self, t1, t2):
        '''

        计算相似度的主函数,t1和t2是以空格分割的字符串，或者已经分割好的list

        :param t1:
        :param t2:
        :return:
        '''

        # text1
        if isinstance(t1, list):
            t1_word_list = t1
        else:
            t1_word_list = t1.split()

        t1_list_syn = substitute_to_synonyum(t1_word_list)
        t1_after_cut_syn = " ".join(t1_list_syn)  # @  #V
        t1_after_cut_syn_no_space = "".join(t1_list_syn)  # V

        # text 2
        if isinstance(t2, list):
            t2_word_list = t2
        else:
            t2_word_list = t2.split()

        t2_list_syn = substitute_to_synonyum(t2_word_list)
        t2_after_cut_syn = " ".join(t2_list_syn)  # @  #V
        t2_after_cut_syn_no_space = "".join(t2_list_syn)  # V

        # 最长公共子串
        lcs_temp = self.find_lcs_len(t1_after_cut_syn, t2_after_cut_syn)
        lcs = round(lcs_temp, 3) * lcs_weight
        # print 'lcs %s: ' % lcs

        # 文本长度差（值越大，长度越接近）
        diffL_temp = self.diff_len(t1_after_cut_syn, t2_after_cut_syn)
        diffL = round(diffL_temp, 3) * diffL_weight
        # print 'diffL %s: ' % diffL

        # jaccard系数
        jaccard_temp = self.comp_jaccard(t1_list_syn, t2_list_syn)
        jaccard = round(jaccard_temp, 3) * jaccard_weight
        # print 'jaccard %s: ' % jaccard

        # 编辑距离
        edit_temp = self.comp_edit(t1_after_cut_syn_no_space, t2_after_cut_syn_no_space)
        edit = round(edit_temp, 3) * edit_weight
        # print 'edit %s: ' % edit

        wmd = 1 * wmd_weight

        # 余弦距离
        cos_temp = self.comp_cosine_main(
            t1_list_syn,
            t2_list_syn,
            self.keywords,
            WordIDF.get())
        cos = round(cos_temp, 3) * cos_weight
        # print 'cos %s: ' % cos

        es = es_weight

        sim_score = round((lcs + wmd + jaccard + cos + edit + diffL + es), 4)
        # print("lcs: [%.6f] jaccard: [%.4f], cos: [%.4f], edit: [%.4f], diffL: [%.4f], score: [%.4f]" \
        #                   % (lcs, jaccard, cos, edit, diffL, sim_score))


        return sim_score


    def get_sub_sim_score(self, t1, t2):
        '''

        计算相似度的主函数,t1和t2是以空格分割的字符串，或者已经分割好的list

        :param t1:
        :param t2:
        :return:返回四种相似度计算结果
        '''
        # text1
        if isinstance(t1, list):
            t1_word_list = t1
        else:
            t1_word_list = t1.split()

        t1_list_syn = substitute_to_synonyum(t1_word_list)
        t1_after_cut_syn = " ".join(t1_list_syn)  # @  #V
        t1_after_cut_syn_no_space = "".join(t1_list_syn)  # V

        # text 2
        if isinstance(t2, list):
            t2_word_list = t2
        else:
            t2_word_list = t2.split()

        t2_list_syn = substitute_to_synonyum(t2_word_list)
        t2_after_cut_syn = " ".join(t2_list_syn)  # @  #V
        t2_after_cut_syn_no_space = "".join(t2_list_syn)  # V

        # 最长公共子串
        lcs_temp = self.find_lcs_len(t1_after_cut_syn, t2_after_cut_syn)
        lcs = round(lcs_temp, 3)
        # print 'lcs %s: ' % lcs

        # 文本长度差（值越大，长度越接近）
        diffL_temp = self.diff_len(t1_after_cut_syn, t2_after_cut_syn)
        diffL = round(diffL_temp, 3)


        # jaccard系数
        jaccard_temp = self.comp_jaccard(t1_list_syn, t2_list_syn)
        jaccard = round(jaccard_temp, 3)


        # 编辑距离
        # edit_temp = self.comp_edit(t1_after_cut_syn_no_space, t2_after_cut_syn_no_space)
        # edit = round(edit_temp, 3)
        # print 'edit %s: ' % edit

        wmd = 1 * wmd_weight

        # 余弦距离
        # cos_temp = self.comp_cosine_main(
        #     t1_list_syn,
        #     t2_list_syn,
        #     self.keywords,
        #     WordIDF.get())
        # cos = round(cos_temp, 3) * cos_weight
        # print 'cos %s: ' % cos

        # es = es_weight

        # sim_score = round((lcs + wmd + jaccard + cos + edit + diffL + es), 4)
        # print("lcs: [%.6f] jaccard: [%.4f], cos: [%.4f], edit: [%.4f], diffL: [%.4f], score: [%.4f]" \
        #                   % (lcs, jaccard, cos, edit, diffL, sim_score))

        return lcs, diffL, jaccard



if __name__ == '__main__':
    text1 = ['我', '讨厌', '阿加班']
    text2 = ['我', '不喜欢', '加班']
    s = Similarity()
    score = s.get_sim_score(text1, text2)
    print("{} & {} similarity score: {}".format(text1, text2, score))

    import Levenshtein
    print(Levenshtein.distance("我讨厌加班", "我不喜欢加班"))
