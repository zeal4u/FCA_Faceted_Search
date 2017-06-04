# -*- coding: utf-8 -*-
from json import JSONEncoder
from sqlalchemy import Table, MetaData

from db_stuff import DBHelper
from models import Book
from models import FacetCode
from concept_lattice_manager import ConceptLattice
from concept_lattice_manager import ConceptLatticeFactory 


metadata = MetaData()

class SearchService(object):

    STATIC_MODE = 0
    DYNAMIC_MODE = 1
    NO_RESULT = 3
    lattice = None
    collection = {}

    def __init__(self, lattice=None, cur_node=None, history_nodes=None):
        u"""
        :attribute lattice: ConceptLattice 载入已经生成的概念格
        :attribute cur_node: Node 当前查询节点
        :attribute history_nodes: List[Node] 历史查询节点
        """
        if not SearchService.lattice:
            SearchService.lattice = lattice
        self.cur_node = cur_node
        self.history_nodes = history_nodes
    
    @staticmethod
    def get_service_by_ip(ip):
        if ip not in SearchService.collection:
            SearchService.collection[ip] = SearchService()
        return SearchService.collection[ip]

    def _get_facet_map(self, node):
        u"""
        """
        # 准备查询数据
        facets = DBHelper.get_attrs_by_codes(FacetCode, None)
        facets_query_dict = {}
        for facet in facets:
            facets_query_dict[facet.id] = facet

        facet_value_supp = self.lattice.count_attr_supp(node)
        facet_dict = {}
        for facet_code in facet_value_supp:
            facet = facets_query_dict[facet_code]
            if facet.facet not in facet_dict:
                facet_dict[facet.facet] = [(facet_code, facet.facet_value.encode('utf-8', 'repalce'),\
                        facet_value_supp[facet_code])]
            else:
                facet_dict[facet.facet].append((facet_code, facet.facet_value.encode('utf-8', 'replace'),\
                        facet_value_supp[facet_code]))
        facet_map = []
        for facet in facet_dict:
            facet_map.append(Facet(facet, facet_dict[facet]))
        return facet_map

    def trans_origin_data(self, node):
        u"""
        这个函数负责将概念格节点转化成真正的数据
        :param node: Node
        """
        content = DBHelper.get_objs_by_codes(Book, node.obj_set)
        facet_map = self._get_facet_map(node)

        return SearchResult(facet_map, content)

    def _locate_by_extent(self, result):
        u"""
        """
        obj_set = set()
        for r in result:
            obj_set.add(r.id)
        return self.lattice.locate_by_extent(obj_set)

    def key_words_search(self, key_words):
        u"""
        提供关键词查询支持
        多个关键词取交结果
        :param key_word: List[String] 查询关键词
        """
        session = DBHelper.get_session()
        result_query = session.query(Book)
        for word in key_words:
            result_query = result_query.filter(Book.book_title.ilike("%%%s%%" % word))
        result = result_query.all()
        
        # 混合构造模式 
        def compute_mode(x):
            if x == 0:
                return SearchService.NO_RESULT  
            y = x * x * 0.000002
            sec = 5
            if y > 5:
                return SearchService.STATIC_MODE
            else:
                return SearchService.DYNAMIC_MODE

        mode = compute_mode(len(result))
        if mode == SearchService.STATIC_MODE:
            return self._static_key_words_search(result)
        elif mode == SearchService.DYNAMIC_MODE:
            return self._dynamic_key_words_search(result)
        elif mode == SearchService.NO_RESULT:
            return SearchResult(None, None)

    def _dynamic_key_words_search(self, result):
        session = DBHelper.get_session()
        trans_books = Table('trans_books_20k', metadata, autoload=True, autoload_with=DBHelper.get_connect())
        books = session.query(trans_books).filter(trans_books.c.book_id.in_([item.id for item in result])).all()
        objs_r = [(item.book_id ,set([item.author_id,item.publisher_id,item.year_id])) \
                for item in books]
        add_intent_algo = ConceptLatticeFactory(objs_r)
        self.lattice = add_intent_algo.create_lattice_incrementally()
        self.cur_node = self.lattice.root
        facet_map = self._get_facet_map(self.cur_node)
        return SearchResult(facet_map, result)

    def _static_key_words_search(self, result):
        self.lattice = ConceptLattice.parse_lattice('/root/FCA_Facet/data/books_20k.gml')
        self.cur_node = self._locate_by_extent(result)
        facet_map = self._get_facet_map(self.cur_node)

        return SearchResult(facet_map, result)

    def expand_search(self, degree):
        u"""
        提供泛化查询支持
        :param degree: float
        """
        result = []
        nodes = self.lattice.expand(self.cur_node, degree)
        for node in nodes:
            result.append(self.trans_origin_data(node))
        return result

    def refine_search(self, degree):
        u"""
        提供泛化查询支持
        :param degree: float
        """
        result = []
        nodes = self.lattice.refine(self.cur_node, degree)
        for node in nodes:
            result.append(self.trans_origin_data(node))
        return result

    def facet_search(self, new_attr):
        query_attr_set = self.cur_node.attr_set | set([new_attr])
        node = self.lattice.locate(query_attr_set)
        self.cur_node = node
        return self.trans_origin_data(node)

    def history_suggest(self):
        u"""
        提供历史查询推荐支持
        利用attribute history_nodes
        """
        pass


class SearchResult(object):

    def __init__(self, facets=None, content=None):
        u"""
        :attribute facets: 分面导航集合
        :attribute content: 查询结果内容
        """
        self.facets = facets
        self.content = content


class Facet(object):

    MAX_FACET_VALUE_NUM = 50
    MIN_FACET_VALUE_SUPP = 5
 
    def __init__(self, facet_name=None, values=None):
        u"""
        :attribute facet_name: string 分面名称
        :attribute values: (属性代码 int，属性 String,属性支持度 int)
        """
        self.facet_name = facet_name
        self.values = values
        self.sort_values()
        self.clean_meanless()

    def sort_values(self):
        u"""
        根据支持度对属性排序
        """
        def comp(x, y):
            if x[2] < y[2]:
                return 1
            elif x[2] > y[2]:
                return -1
            else:
                return 0
        self.values.sort(comp)

    def clean_meanless(self):
        u"""
        剔除支持度太小的分面值
        需要事先排序
        """
        self.values = self.values[:Facet.MAX_FACET_VALUE_NUM]
        for index, value in enumerate(self.values):
            if value[2] < Facet.MIN_FACET_VALUE_SUPP:
                self.values = self.values[:index]

    def __str__(self):
        values_str = u''
        for value in self.values:
            values_str += u'[%d %s %d], ' % (value[0], value[1], value[2])
        return u'Facet, {facet_name=%s, facet_value=%s}' % (self.facet_name, values_str)

    def __repr__(self):
        values_str = u''
        for value in self.values:
            try:
                values_str += '["{}" "{}" "{}"], '.format(value[0], value[1], value[2]).encode('utf-8')
            except UnicodeDecodeError, e:
                print value[0], value[1]
                #raise e
        return u'<Facet(facet_name=%s, facet_value=%s)>' % (self.facet_name, values_str)


class FacetEncoder(JSONEncoder):
    u"""
    JSONEncoder for class: Facet
    """

    def default(self, facet):
        if isinstance(facet, Facet):
            return {
                u'facet_name': facet.facet_name,
                u'values': [{'id': value[0], 'value_name': value[1], 'supp': value[2]} \
                        for value in facet.values] 
            }
        return JSONEncoder.default(self, facet)

