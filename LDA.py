# _*_ coding: utf-8 _*_

"""
python_lda.py by xianhu
"""

import os
import numpy
import logging
from collections import defaultdict

class BiDictionary(object):
    """
    定义双向字典,通过key可以得到value,通过value也可以得到key
    """

    def __init__(self):
        """
        :key: 双向字典初始化
        """
        self.dict = {}            # 正向的数据字典,其key为self的key
        self.dict_reversed = {}   # 反向的数据字典,其key为self的value
        return

    def __len__(self):
        """
        :key: 获取双向字典的长度
        """
        return len(self.dict)

    def __str__(self):
        """
        :key: 将双向字典转化为字符串对象
        """
        str_list = ["%s\t%s" % (key, self.dict[key]) for key in self.dict]
        return "\n".join(str_list)

    def clear(self):
        """
        :key: 清空双向字典对象
        """
        self.dict.clear()
        self.dict_reversed.clear()
        return

    def add_key_value(self, key, value):
        """
        :key: 更新双向字典,增加一项
        """
        self.dict[key] = value
        self.dict_reversed[value] = key
        return

    def remove_key_value(self, key, value):
        """
        :key: 更新双向字典,删除一项
        """
        if key in self.dict:
            del self.dict[key]
            del self.dict_reversed[value]
        return

    def get_value(self, key, default=None):
        """
        :key: 通过key获取value,不存在返回default
        """
        return self.dict.get(key, default)

    def get_key(self, value, default=None):
        """
        :key: 通过value获取key,不存在返回default
        """
        return self.dict_reversed.get(value, default)

    def contains_key(self, key):
        """
        :key: 判断是否存在key值
        """
        return key in self.dict

    def contains_value(self, value):
        """
        :key: 判断是否存在value值
        """
        return value in self.dict_reversed

    def keys(self):
        """
        :key: 得到双向字典全部的keys
        """
        return self.dict.keys()

    def values(self):
        """
        :key: 得到双向字典全部的values
        """
        return self.dict_reversed.keys()

    def items(self):
        """
        :key: 得到双向字典全部的items
        """
        return self.dict.items()


class CorpusSet(object):

    def __init__(self):
        """
        :key: 初始化函数
        """
        # 定义关于word的变量
        self.local_bi = BiDictionary()
        self.words_count = 0
        self.V = 0

        # 定义关于article的变量
        self.artids_list = []
        self.arts_Z = []
        self.M = 0

        # 定义推断中用到的变量（可能为空）
        self.global_bi = None
        self.local_2_global = {}
        return

    def init_corpus_with_file(self, file_name):
        """
        :key: 利用数据文件初始化语料集数据。文件每一行的数据格式: id[tab]word1 word2 word3......
        """
        with open(file_name, "r", encoding="utf-8") as file_iter:
            self.init_corpus_with_articles(file_iter)
        return

    def init_corpus_with_articles(self, article_list):
        """
        :key: 利用article的列表初始化语料集。每一篇article的格式为: id[tab]word1 word2 word3......
        """
        # 清理数据--word数据
        self.local_bi.clear()
        self.words_count = 0
        self.V = 0

        # 清理数据--article数据
        self.artids_list.clear()
        self.arts_Z.clear()
        self.M = 0

        # 清理数据--清理local到global的映射关系
        self.local_2_global.clear()

        # 读取article数据
        for line in article_list:
            frags = line.strip().split()
            if len(frags) < 2:
                continue

            # 获取article的id
            art_id = frags[0].strip()

            # 获取word的id
            art_wordid_list = []
            for word in [w.strip() for w in frags[1:] if w.strip()]:
                local_id = self.local_bi.get_key(word) if self.local_bi.contains_value(word) else len(self.local_bi)

                # 这里的self.global_bi为None和为空是有区别的
                if self.global_bi is None:
                    # 更新id信息
                    self.local_bi.add_key_value(local_id, word)
                    art_wordid_list.append(local_id)
                else:
                    if self.global_bi.contains_value(word):
                        # 更新id信息
                        self.local_bi.add_key_value(local_id, word)
                        art_wordid_list.append(local_id)

                        # 更新local_2_global
                        self.local_2_global[local_id] = self.global_bi.get_key(word)

            # 更新类变量: 必须article中word的数量大于0
            if len(art_wordid_list) > 0:
                self.words_count += len(art_wordid_list)
                self.artids_list.append(art_id)
                self.arts_Z.append(art_wordid_list)

        # 做相关初始计算--word相关
        self.V = len(self.local_bi)
        logging.debug("words number: " + str(self.V) + ", " + str(self.words_count))

        # 做相关初始计算--article相关
        self.M = len(self.artids_list)
        logging.debug("articles number: " + str(self.M))
        return

    def save_wordmap(self, file_name):
        """
        :key: 保存word字典,即self.local_bi的数据
        """
        with open(file_name, "w", encoding="utf-8") as f_save:
            f_save.write(str(self.local_bi))
        return

    def load_wordmap(self, file_name):
        """
        :key: 加载word字典,即加载self.local_bi的数据
        """
        self.local_bi.clear()
        with open(file_name, "r", encoding="utf-8") as f_load:
            for _id, _word in [line.strip().split() for line in f_load if line.strip()]:
                self.local_bi.add_key_value(int(_id), _word.strip())
        self.V = len(self.local_bi)
        return



