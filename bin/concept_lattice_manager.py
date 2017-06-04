# -*- coding: utf-8 -*-
__author__ = 'jsz'
__version__ = 0.1

import networkx as nx
import hashlib
import base64 
from networkx.exception import NetworkXError
from db_stuff import DBHelper

def intersect(l, i):
    u"""
    :param l:
    :param i:
    :return:
    """
    t = [index for index in xrange(i)]
    return [val for val in l if val in t]


def difference(a, b):
    u"""
    比较两个数组的差别
    :param a:
    :param b:
    :return:
    """
    return list(set(a) - set(b))


class Background(object):

    def __init__(self, u, m, r=None, triple=None):
        u"""
        :param u: list  对象列表
        :param m: list  属性列表
        :param r: list[list]  对象与属性的关系矩阵
        """
        self.u = u
        self.m = m
        self.u_dict = {val:i for i, val in enumerate(self.u)}
        self.m_dict = {val:i for i, val in enumerate(self.m)}
        if r:
            self.r_triple = self._construct_triple_tuple(r)
        if triple:
            self.r_triple = triple

    def _construct_triple_tuple(self, r):
        res = {}
        for i in xrange(0, len(r)):
            for j in xrange(0, len(self.m)):
                if r[i][j]:
                    res[i*len(self.m) + j] = True
        return res

    ##TODO Need Much Improvement
    @staticmethod
    def build_bg_from_db(trans_table, facet_codes_table):
        sql1 = u"""
           select book_id, author_id, publisher_id, year_id from %s; 
        """ % trans_table
        sql2 = u"""
           select id from %s order by id;
        """ % facet_codes_table
        session = DBHelper.get_session()
        books = session.execute(sql1).fetchall()
        codes = session.execute(sql2).fetchall()

        codes_len = len(codes)

        triple = {}
        u = [book_id for book_id, author_id, publisher_id, year_id in books]
        m = [code.id for code in codes]

        bg = Background(u, m)

        for i, book in enumerate(books):
            for j in xrange(1, len(book)):
                mark = i * codes_len + bg.get_attr_index(book[j])
                triple[mark] = True
        bg.r_triple = triple
        return bg


    def is_in_background(self, i, j):
        return True if i*len(self.m)+j in self.r_triple else False

    def get_obj_index(self, obj):
        u"""

        :param obj:
        :return: index of attr
        """
        if obj in self.u_dict:
            return self.u_dict[obj]
        else:
            return None

    def get_attr_index(self, attr):
        u"""

        :param attr:
        :return: index of attr
        """
        if attr in self.m_dict:
            return self.m_dict[attr]
        else:
            return None

    def get_obj(self, i):
        u"""
        :param i:  index of obj in u
        :return: the ith obj of u
        """
        assert 0 <= i < len(self.u), "Index out of range!"
        return self.u[i]

    def get_attr(self, i):
        u"""
        :param i:  index of attr in m
        :return: the ith attr of m
        """
        assert 0 <= i < len(self.m), "Index out of range!"
        return self.m[i]


class BaseFCL(object):

    def __init__(self, background):
        u"""
        :param background: Background obj
        """
        self.bg = background

    def g(self, attrs):
        u"""
        输入属性列表，输出对应的对象列表
        最坏情况下时间复杂度 为 O（n^2）
        :param attrs:  list of attrs
        :return: list of objs
        """
        res = []
        for obj in xrange(len(self.bg.u)):
            for attr in attrs:
                if not self.bg.is_in_background(obj, attr):
                    break
            else:
                res.append(obj)
        return res

    def f(self, objs):
        u"""
        输入对象列表，输出对应的属性列表
        最坏情况下时间复杂度 为 O（n^2）
        :param attrs:  list of objs
        :return: list of attrs
        """
        res = []
        for attr in xrange(len(self.bg.m)):
            for obj in objs:
                if not self.bg.is_in_background(obj, attr):
                    break
            else:
                res.append(attr)
        return res


class Node(object):

    def __init__(self, attr_set, ref_seq=None, obj_set=None, supp=None):
        u"""
        每一个节点都是一个概念
        :param attr_set: list 用于查询的 属性集
        :param supp: int 支持度，其实就是这个概念对应的外延大小
        :param ref_seq: list[list[2]]  key：属性差值k   value：attr_set+k 对应的外延
        :param parents: list 该节点的父节点
        :param children: list 该节点的孩子节点
        """
        if attr_set:
            self.attr_set = attr_set
        else:
            self.attr_set = set()

        if obj_set:
            self.obj_set = obj_set
        else:
            self.obj_set = set()

        if supp:
            self.supp = supp
        else:
            self.supp = len(self.obj_set)

        self.ref_seq = ref_seq

    @staticmethod
    def stringizer(node):
        def set_to_str(set):
            res = ''
            for i in set:
                res += '%s ' % i
            return res

        attr_set_str = 'attr_set:%s;' % set_to_str(node.attr_set)
        obj_set_str = 'obj_set:%s;' % set_to_str(node.obj_set)
        supp_str = 'supp:%d' % node.supp
        return "%s%s%s" %(attr_set_str, obj_set_str, supp_str)

    @staticmethod
    def destringizer(string):
        def str_to_set(str):
            nums = str.split()
            res = set()
            for n in nums:
                res.add(int(n))
            return res
        properties = string.split(';')
        attr_set = str_to_set(properties[0].split(':')[1])
        obj_set = str_to_set(properties[1].split(':')[1])
        supp = int(properties[2].split(':')[1])
        return Node(attr_set=attr_set, obj_set=obj_set, supp=supp)

    def __hash__(self):
        result = 17
        for attr in self.attr_set:
            result = 1001 * result + attr
        return result

    def __eq__(self, other):
        if self.attr_set == other.attr_set:
            return True
        return False


class ConceptLattice(object):

    ROOT_NODE = 0
    LEAF_NODE = 1
    NORMAL_NODE = 2
    BOTTOM_NODE = 3

    def __init__(self, graph, root=None, leaf_nodes=None, bottom=None):
        self.graph = graph
        self.root = root
        if leaf_nodes:
            self.leaf_nodes = leaf_nodes
        else:
            self.leaf_nodes = []
        self.bottom = bottom

    def _get_root(self):
        u"""
        获取格的根节点
        """
        if self.root:
            return self.root

        res = None
        for node, data in self.graph.nodes_iter(data=True):
            if data['type'] == ConceptLattice.ROOT_NODE:
                res = node
                break
        self.root = res
        return res

    def _get_leaf(self):
        u"""
        获取格的叶子节点
        """
        if self.leaf_nodes:
            return self.leaf_nodes

        res = []
        for node, data in self.graph.nodes_iter(data=True):
            if data['type'] == ConceptLattice.LEAF_NODE:
                res.append(node)
        self.leaf_nodes = res
        return res

    def print_lattice(self):
        for node in self.graph.nodes():
            print node.obj_set, ';',
            print 'Predecessors:',
            for nr in self.graph.predecessors(node):
                print nr.obj_set,
            print 'Successors:',
            for nr in self.graph.successors(node):
                print nr.obj_set,
            print

    def __getattr__(self, name):
        if name == 'depth':
            return self._get_depth()

    def _get_depth(self):
        u"""
        获取格的深度
        """
        if not hasattr(self, 'depth'):
            self.depth = 0
        def _travel(g, cur_node, cur_depth):
            cur_depth += 1
            if self.depth < cur_depth:
                self.depth = cur_depth
            for node in g.successors(cur_node):
                _travel(g, node, cur_depth)

        _travel(self.graph, self.root, 0)
        return self.depth

    @staticmethod
    def parse_lattice(path):
        g = nx.read_gml(path, destringizer=Node.destringizer)
        cl = ConceptLattice(g)
        cl._get_root()
        cl._get_leaf()
        return cl

    def save_lattice(self, path):
        nx.write_gml(self.graph, path, Node.stringizer)


    def locate_by_extent(self, query_obj_set):
        u"""
        """
        target = self.root
        node = self.root
        while self.graph.successors(node):
            for child_node in self.graph.successors(node):
                if query_obj_set.issubset(child_node.obj_set):
                    flag = True
                    node = child_node
                    target = node
                    break
            else:
                #针对当前节点的父节点，没有找到属性包含query_attr_set的节点，则当前节点为一个极大节点
                break
        return target

    def locate(self, query_attr_set):
        u"""
        根据一个查询属性集定位某个最匹配的格节点
        :param query_attr_set:
        :return:
        """
        # 如果父节点目前还没有后继，则说明新生成的子节点对父节点的后继毫无影响，子节点的后继也尚未产生
        if not self.leaf_nodes:
            return None
        target = None
        for node in self.leaf_nodes:
            if query_attr_set.issubset(node.attr_set):
                target = node
                while self.graph.predecessors(node):
                    for parent_node in self.graph.predecessors(node):
                        if query_attr_set.issubset(parent_node.attr_set):
                            flag = True
                            node = parent_node
                            target = node
                            break
                    else:
                        #针对当前节点的父节点，没有找到属性包含query_attr_set的节点，则当前节点为一个极大节点
                        break
                break
        return target

    def locate_from(self, query_attr_set, start_node):
        u"""
        根据一个查询属性集定位某个最匹配的格节点
        :param query_attr_set:
        :param start_node: node 查询的起点节点
        
        :return:
        """
        target = start_node 
        while self.graph.predecessors(start_node):
            #print start_node.__hash__()
            for parent_node in self.graph.predecessors(start_node):
                if query_attr_set.issubset(parent_node.attr_set):
                    start_node = parent_node
                    target = start_node
                    break
            else:
                break
        return target

    def locate_from_versa(self, query_attr_set, start_node):
        u"""
        根据一个查询属性集定位某个最匹配的格节点
        :param query_attr_set:
        :param start_node: node 查询的起点节点
        
        :return:
        """
        target = start_node 
        while self.graph.successors(start_node):
            for child_node in self.graph.successors(start_node):
                if query_attr_set.issubset(child_node.attr_set):
                    start_node = child_node 
                    target = start_node
                    break
            else:
                break
        return target

    def get_average_supp(self, nodes):
        u"""
        分析目标节点集的平均支持度
        """
        sum_supp = 0
        for node in nodes:
            sum_supp += node.supp
        return sum_supp*1.0/len(nodes)

    def get_partion_max(self, nodes):
        u"""
        从某一节点集合中选取极大值集合
        :param nodes: 某一节点集合
        """
        res = []
        flags = [True for i in nodes]
        nodes_len = len(nodes)
        for i in xrange(0, nodes_len):
            for j in xrange(i+1, nodes_len):
                if flags[j]:
                    intersection = nodes[i].attr_set & nodes[j].attr_set
                    inter_len = len(intersection)
                    # 如果有j比i更高，则他们attr_set的交集等于j的attr_set,这说明i并非极大格节点
                    if inter_len == len(nodes[j].attr_set):
                        flags[i] = False
                        break
                    # 如果有j比i更低，则他们attr_set的交集等于i的attr_set,这说明j并非极大格节点
                    if inter_len == len(nodes[i].attr_set):
                        flags[j] = False
                    # 如果i和j无法比较，说明i和j都有可能为极大格节点
        for i in xrange(0, nodes_len):
            if flags[i]:
                res.append(nodes[i])
        return res

    def count_attr_supp(self, cur_node):
        u"""
        计算以当前节点为上确界的子形式概念格中各属性的支持度
        :param cur_node: 当前节点
        :return: dict {attr: supp}
        """
        res = {}
        cur_nodes_set = set([cur_node])
        while cur_nodes_set:
            next_nodes_set = []
            for node in cur_nodes_set:
                next_nodes_set.extend(self.graph.successors(node))
                for attr in node.attr_set.difference(cur_node.attr_set):
                    if attr not in res:
                        res[attr] = node.supp
            cur_nodes_set = set(next_nodes_set)
        return res

    def _distance_match(self, cur_node, k, direction_method, limit=5):
        u"""
        其中 k = 1-|X1.obj_set intersect X2.obj_set|/|X1.obj_set union X2.obj_set|
        :param cur_node: 当前查询节点
        :param direction_method: 方向函数，向上遍历还是向下遍历
        :param limit: int 个数限制
        :return: nodes 符合条件的节点集
        """
        def match(node):
            # 找到了范围内的极远点
            flag = True
            # 距离还在范围内的节点
            in_range_nodes = []
            for parent in direction_method(node): 
                # 求 Jaccard距离
                distance = 1 - 1.0 * len(cur_node.obj_set & parent.obj_set)/len(cur_node.obj_set | parent.obj_set)
                if distance <= k:
                    flag = False
                    in_range_nodes.append(parent)
            return flag, in_range_nodes

        result = set()
        cur_loop_nodes = direction_method(cur_node)
        while cur_loop_nodes:
            next_loop_nodes = []
            for parent in cur_loop_nodes:
                flag, in_range_nodes = match(parent)  
                if flag:
                    result.add(parent)
                    if len(result) == limit:
                        return result
                else:
                    next_loop_nodes.extend(in_range_nodes)
            cur_loop_nodes = next_loop_nodes
        return result

    def expand(self, cur_node, k):
        u"""
        泛化，返回距离节点node为k的祖先节点
        其中 k = 1-|X1.obj_set intersect X2.obj_set|/|X1.obj_set union X2.obj_set|
        :param cur_node: 当前查询节点
        :return: nodes 符合条件的节点集
        """
        return self._distance_match(cur_node, k, self.graph.predecessors)
       

    def refine(self, cur_node, k):
        u"""
        细化，返回距离节点node为k的后代节点
        其中 k = 1-|X1.obj_set intersect X2.obj_set|/|X1.obj_set union X2.obj_set|
        :param cur_node: 当前查询节点
        :return: nodes 符合条件的节点集
        """
        return self._distance_match(cur_node, k, self.graph.successors)

    def meet(self, nodes):
        u"""
        返回节点集nodes的下确界
        :param nodes: 节点的集合
        :return node:
        """
        meet_attr_set = set()
        for node in nodes:
            meet_attr_set |= node.attr_set
        return self.locate(meet_attr_set)

    def join(self, nodes):
        u"""
        返回节点集nodes的上确界
        :param nodes: 节点的集合
        :return node:
        """
        join_attr_set = set()
        for node in nodes:
            join_attr_set &= node.attr_set
        return self.locate_from(join_attr_set, nodes[0])

class FCLMiner(BaseFCL):

    def __init__(self, background):
        # 当前生成的所有节点
        self.all_extent_dict = {}
        BaseFCL.__init__(self, background)

    def gen_lattice(self):
        leaf_nodes = []
        self.graph = nx.DiGraph()

        start_obj_set = self.g([])
        start_attr_set = self.f(start_obj_set)
        # 属性/对象 用下标代指
        start_ref_attr_set = difference(range(0, len(self.bg.m)), start_attr_set)
        ref_seq = []
        for ref_attr in start_ref_attr_set:
            ref_seq.append([ref_attr, set(self.g([ref_attr] + start_attr_set))])

        # 生成root节点
        root = Node(set(start_attr_set), ref_seq, set(start_obj_set))
        # 将根节点添加到图中，并进行标注
        self.graph.add_node(root, type=ConceptLattice.ROOT_NODE)
        self.lattice = ConceptLattice(self.graph, root, leaf_nodes)

        self._create_children(root)
        return self.lattice

    def print_value(self, node):
        print '[',
        for attr_index in node.attr_set:
            print self.bg.get_attr(attr_index),
        print '],[',
        for ref_pair in node.ref_seq:
            print '[', self.bg.get_attr(ref_pair[0]), ',', ref_pair[1], '],',
        print ']'

    def print_tree(self, root):
        if not root:
            return
        for child in root.children:
            self.print_value(child)
            self.print_tree(child)

    def _create_children(self, parent_node):
        u"""
        递归方法，根据root节点生成一颗类别集枚举树
        :param parent_node: 父节点
        :return:
        """
        self.all_extent_dict[hash(str(parent_node.obj_set))] = 0

        for i in range(0, len(parent_node.ref_seq)):
            cur_ref_pair = parent_node.ref_seq[i]
            # 如果 在当前 收缩对 之前没有包含 其trans的其他收缩对，则针对该收缩对有子节点
            for cmp_ref_pair in parent_node.ref_seq[0:i]:
                if cur_ref_pair[1].issubset(cmp_ref_pair[1]):
                    break
            else:
                if hash(str(cur_ref_pair[1])) not in self.all_extent_dict:
                    child = self._create_child(parent_node, cur_ref_pair)
                    self.graph.add_node(child, type=ConceptLattice.NORMAL_NODE)
                    ## 边更新代码
                    # step1 更新子节点的后继，前驱
                    targets = []
                    for c in self.graph.successors(parent_node):
                        cur_attr_set = c.attr_set | set([cur_ref_pair[0]])
                        target = self.lattice.locate(cur_attr_set)
                        if target:
                            targets.append(target)
                    for real_target in self.lattice.get_partion_max(targets):
                        # 将边添加到图中
                        self.graph.add_edge(child, real_target)

                    # step2 更新父节点的后继，前驱
                    delete_edge_to_nodes = []
                    for node in self.graph[parent_node]:
                        if node in self.graph[child]:
                            delete_edge_to_nodes.append(node)
                    for node in delete_edge_to_nodes:
                        self.graph.remove_edge(parent_node, node)

                    # 建立父子关系
                    self.graph.add_edge(parent_node, child)

                    # 如果 child的收缩序列为空且没有孩子，则将其添加到叶子节点集当中
                    if not child.ref_seq and not self.graph.successors(child):
                        self.lattice.leaf_nodes.append(child)
                        self.graph.node[child]['type'] = ConceptLattice.LEAF_NODE

                    self._create_children(child)

    def _create_child(self, parent_node, cur_ref_pair):
        u"""
        构建当前父节点对应收缩对的子节点
        :param parent_node: 当前父节点
        :param cur_ref_pair: 当前收缩对
        :return:
        """
        # 子节点属性集
        attr_set = parent_node.attr_set | set([cur_ref_pair[0]])
        # 子节点收缩对
        ref_seq = []
        # 收缩对的trans是 当前收缩对的超集，且排在当前收缩对之后
        # 那么就将它的属性集添加到子节点的属性集中（内涵）
        for i, ref_pair in enumerate(parent_node.ref_seq):
            if ref_pair[0] == cur_ref_pair[0]:
                for j in range(i+1, len(parent_node.ref_seq)):
                    ref_pair_j = parent_node.ref_seq[j]
                    # 计算子节点的内涵
                    attr_set |= set([ref_pair_j[0]]) if cur_ref_pair[1].issubset(ref_pair_j[1]) \
                            else set([])
                    # 计算子节点的收缩对
                    intersect_set = cur_ref_pair[1] & ref_pair_j[1]
                    if 0 < len(intersect_set) < len(cur_ref_pair[1]):
                        ref_seq.append([ref_pair_j[0], intersect_set])
                break
        node = Node(attr_set, ref_seq, cur_ref_pair[1])
        return node


class ConceptLatticeFactory(object):

    def __init__(self, objs):
        u"""
        :param objs: list[list[2]] [0] the obj id, [1] the attr_set
        :param attr_set_m: set all attributes
        """
        self.objs = objs
        self.node_dict = {}
        self.md5 = hashlib.md5()
        self.total_steps = 0
        self.skip_steps = 0

    def intent_hash(self, attr_set):
        attr_list = list(attr_set)
        attr_list.sort()
        md5 = hashlib.md5()
        for attr in attr_list:
            md5.update(str(attr)+',')
        return md5.hexdigest()

    def create_lattice_incrementally(self):
        u"""
        渐增式概念生成算法
        """
        bottom = Node(attr_set=set([-1]), obj_set=set())
        self.graph = nx.DiGraph()
        self.graph.add_node(bottom, type=ConceptLattice.BOTTOM_NODE)
        self.lattice = ConceptLattice(self.graph, bottom=bottom)
        for obj in self.objs:
            bottom.attr_set.union(obj[1])
            concept = self.add_intent(obj[1], bottom)
            self.update_extent(concept, obj[0])
            hash_code = self.intent_hash(concept.attr_set)
        self.lattice.graph.remove_node(bottom)
        for node in self.lattice.graph.nodes():
            if not self.graph.predecessors(node):
                self.graph.node[node]['type'] = ConceptLattice.ROOT_NODE
                self.lattice.root = node
                continue
            if not self.graph.successors(node):
                self.graph.node[node]['type'] = ConceptLattice.LEAF_NODE
                self.lattice.leaf_nodes.append(node)
        return self.lattice

    def add_intent(self, attr_set, generator):
        u"""
        生成概念格的关键方法
        :param attr_set: set 准备用来构造概念的属性集
        :param genrator: Node 当前的生成器
        """
        # 记录该函数调用总数
        self.total_steps += 1

        hash_code = self.intent_hash(attr_set)
        if hash_code in self.node_dict:
            # 记录Skip数
            self.skip_steps += 1
            return self.node_dict[hash_code]
        # 获取标准生成器
        generator = self.lattice.locate_from(attr_set, generator)
        #if generator.attr_set == attr_set:
        #    return generator

        # 计算候选直接父概念
        generator_parents = self.graph.predecessors(generator)
        new_parents = set()
        for candidate in generator_parents:
            if not candidate.attr_set.issubset(attr_set):
                candidate = self.add_intent(candidate.attr_set & attr_set, candidate)
            new_parents.add(candidate)

        # 构造新概念，并添加到哈希表中
        new_concept = Node(attr_set=attr_set, obj_set=set(generator.obj_set))
        if hash_code not in self.node_dict:
            self.node_dict[hash_code] = new_concept

        self.graph.add_node(new_concept, type=ConceptLattice.NORMAL_NODE)

        for parent_node in new_parents:
            is_true_parent = True
            for child in self.graph.successors(parent_node):
                if child.attr_set.issubset(attr_set):
                    is_true_parent = False
                    break
            if is_true_parent:
                try:
                    self.graph.remove_edge(parent_node, generator)
                except NetworkXError:
                    pass
                self.graph.add_edge(parent_node, new_concept)
        # 设置父子关系
        self.graph.add_edge(new_concept, generator)        
        return new_concept

    def update_extent(self, concept, obj_mark):
        u"""
        更新当前concept以及其上所有概念的外延，将obj添加到其中 
        :param concept: Node 一个概念
        :param obj_mark: integer obj 的标识符
        """
        concept.obj_set.add(obj_mark)
        concept.supp = len(concept.obj_set)
        #print concept.obj_set, concept.attr_set
        for parent_node in self.graph.predecessors(concept):
            self.update_extent(parent_node, obj_mark)

if __name__ == "__main__":
    u = [i for i in range(1, 9)]
    m = [chr(97 + i) for i in range(9)]
    r = [
        [True, False, False, False, True, False, True, False, True],
        [True, True, True, True, False, False, False, False, False],
        [True, False, False, True, False, True, False, False, False],
        [True, False, False, True, True, False, False, False, False],
        [True, False, False, False, True, True, True, True, False],
        [True, True, True, False, False, False, True, False, False],
        [True, False, False, True, False, True, False, False, False],
        [True, False, False, False, True, True, True, True, True]
    ]
    u1 = range(1, 5)
    m1 = [chr(97 + i) for i in range(5)]
    r1 = [
            [True, False, True, False, False],
            [True, True, True, False, True],
            [False, True, False, False, True],
            [False, False, True, True, True],
            ]
    
    u2 = range(1, 6)
    m2 = [chr(97 + i) for i in range(6)]
    r2 = [
            [True, True, False, False, True, True],
            [False, True, True, False, False, True],
            [False, False, True, True, False, True],
            [True, True, True, True, False, True],
            [False, False, True, True, False, False]
            ]
    bg = Background(u, m, r)
    #baseFCL = BaseFCL(bg)
    #fcl_miner = FCLMiner(bg)
    #lattice = fcl_miner.gen_lattice()
    #print lattice.count_attr_supp(lattice.root)

    objs_r = [
            (0,set([0, 4, 6, 8])),
            (1,set([0, 1, 2, 3])),
            (2,set([0, 3, 5])),
            (3,set([0, 3, 4])),
            (4,set([0, 4, 5, 6, 7])),
            (5,set([0, 1, 2, 6])),
            (6,set([0, 3, 5])),
            (7,set([0, 4, 5, 6, 7, 8]))
            ]

    add_intent_algo = ConceptLatticeFactory(objs_r)
    add_intent_algo.create_lattice_incrementally().save_lattice('test.gml')
