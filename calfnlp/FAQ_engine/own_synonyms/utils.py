#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import re
import subprocess
from contextlib import contextmanager
import numpy as np
import numbers
import pickle
from typing import Dict, Text, Any, List, Set

if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")

else:
    unicode = str

PAT_ALPHABETIC = re.compile(r'(((?![\d])\w)+)', re.UNICODE)
RE_HTML_ENTITY = re.compile(r'&(#?)([xX]?)(\w{1,8});', re.UNICODE)


def get_random_state(seed):
    """
    Turn seed into a np.random.RandomState instance.
    Method originally from maciejkula/glove-python, and written by @joshloyal.
    """
    if seed is None or seed is np.random:
        return np.random.mtrand._rand
    if isinstance(seed, (numbers.Integral, np.integer)):
        return np.random.RandomState(seed)
    if isinstance(seed, np.random.RandomState):
        return seed
    raise ValueError(
        '%r cannot be used to seed a np.random.RandomState instance' %
        seed)

def any2utf8(text, errors='strict', encoding='utf8'):
    """Convert a string (unicode or bytestring in `encoding`), to bytestring in utf8."""
    if isinstance(text, unicode):
        return text.encode('utf8')
    # do bytestring -> unicode -> utf8 full circle, to ensure valid utf8
    return unicode(text, encoding, errors=errors).encode('utf8')


to_utf8 = any2utf8


def any2unicode(text, encoding='utf8', errors='strict'):
    """Convert a string (bytestring in `encoding` or unicode), to unicode."""
    if isinstance(text, unicode):
        return text
    return unicode(text, encoding, errors=errors)


to_unicode = any2unicode

# cosine distance
# https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.linalg.norm.html
from numpy import dot
from numpy.linalg import norm
cosine = lambda a, b: dot(a, b)/(norm(a)*norm(b))

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def call_on_class_only(*args, **kwargs):
    """Raise exception when load methods are called on instance"""
    raise AttributeError('This method should be called on a class object.')

def is_digit(obj):
    '''
    Check if an object is Number
    '''
    return isinstance(obj, (numbers.Integral, numbers.Complex, numbers.Real))


def save_obj(obj: Dict, path: Text, name: Text):
    with open(os.path.join(path, name + '.pkl'), 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(path: Text, name: Text) -> Dict[str,int]:
    with open(os.path.join(path, name + '.pkl'), 'rb') as f:
        return pickle.load(f)

def load_stopwords(file_path):
    '''
    load stop words
    '''
    _stopwords = set()
    if sys.version_info[0] < 3:
        words = open(file_path, 'r')
    else:
        words = open(file_path, 'r', encoding='utf-8')
    stopwords = words.readlines()
    for w in stopwords:
        _stopwords.add(any2unicode(w).strip())

    return _stopwords