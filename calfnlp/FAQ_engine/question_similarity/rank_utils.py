
import math

def find_lcs_len(s1, s2):
    if len(s1) == 0 or len(s2) == 0:  # 如果有一个list全是空的，说明里面全是停止词,直接返回0相似度
        return 0

    # s1 = unicode(s1, "utf-8")
    # s2 = unicode(s2, "utf-8")
    m = [[0 for x in s2] for y in s1]
    for p1 in range(len(s1)):
        for p2 in range(len(s2)):
            if s1[p1] == s2[p2]:
                if p1 == 0 or p2 == 0:
                    m[p1][p2] = 1
                else:
                    m[p1][p2] = m[p1 - 1][p2 - 1] + 1
            elif m[p1 - 1][p2] < m[p1][p2 - 1]:
                m[p1][p2] = m[p1][p2 - 1]
            else:  # m[p1][p2-1] < m[p1-1][p2]
                m[p1][p2] = m[p1 - 1][p2]
    # return round(m[-1][-1]/(max(len(s1),len(s2))),2)
    a = m[-1][-1]
    b = max(len(s1), len(s2))
    return a / float(b)


def diff_len(s1, s2):
    # print "different s1 is: ", s1
    # print "different s2 is: ", s2
    len_s1 = len(s1)
    len_s2 = len(s2)

    # print len_s2
    # print len_s2

    if len_s2 == 0 or len_s1 == 0:
        return 0

    return 1 - abs(len_s1 - len_s2) / float(max(len_s1, len_s2))


# -------------------------------------------------------------------------------------------
# 输入q和a，分词后通过idf得到权重，导入CompCosine中

def comp_cosine_main(w1, w2, dicList = None, dic_if = None):

    w1 = list(set(w1))
    w2 = list(set(w2))

    l1 = []
    l2 = []

    for x in w1:
        # print x
        if x in dic_if:
            l1.append((x, dic_if[x]))
        elif x in dicList:
            l1.append((x, 20))
        else:
            l1.append((x, 1))

    for y in w2:
        # print y
        if y in dic_if:
            l2.append((y, dic_if[y]))
        elif y in dicList:
            l2.append((y, 20))
        else:
            l2.append((y, 1))

    return comp_cosine(l1, l2)


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


def remove_dup(w):
    set = {}


# -------------------------------------------------------------------------------------------

def comp_jaccard(w1, w2):
    if len(w1) == 0 or len(w2) == 0:
        return 0

    cross = 0.0
    union_dict = {}
    w1 = list(set(w1))
    w2 = list(set(w2))

    for aitem in w1:
        if type(aitem) == tuple:
            aitem = aitem[0]
        union_dict[aitem] = 1

    for aitem in w2:
        if type(aitem) == tuple:
            aitem = aitem[0]
        if aitem in union_dict:
            cross += 1
        else:
            union_dict[aitem] = 1

    return cross / len(union_dict)


def comp_edit(first, second):
    if len(first) == 0 or len(second) == 0:
        return 0

    # if not isinstance(first, unicode):
    #     first = first.decode('utf-8', 'ignore')
    # if not isinstance(second, unicode):
    #     second = second.decode('utf-8', 'ignore')

    # print"**********"
    # print"调试编辑距离"
    # print len(first)
    # print len(second)
    # print"**********"

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


def linear(x):
    return 1 / float(30) * x


def wmd_sim(a, b, model):
    # a = map(lambda a: a.decode("utf-8"), a)
    # b = map(lambda b: b.decode("utf-8"), b)
    
    # print a
    # print b
    
    return linear(model.wmdistance(a, b))
