# -*- coding: utf-8 -*-
__author__ = 'jsz'
__version__ = 0.1


import web
import json

from search_engine import SearchService
from search_engine import FacetEncoder
from models import BookEncoder

# APIs exposed to front end
urls = (
            "/keyWordsSearch","KeyWordsSearch",
            "/facetSearch","FacetSearch",
            "/expandSearch","ExpandSearch",
            "/defineSearch","DefineSearch",
            "/historySummary","HistorySummary",
            "/(.*)", "Index"
        )


app = web.application(urls, globals())


class Index:

    def GET(self, url):
        u"""
        :param url: needs, or will throw exception
        """
        raise web.redirect('/static/web-angular/app/index.html')


def json_encoder(search_result):
    result = {
        'facets': json.loads(json.dumps(search_result.facets, cls=FacetEncoder)),
        'content': json.loads(json.dumps(search_result.content, cls=BookEncoder))
    }
    return json.dumps(result)


class KeyWordsSearch:

    def GET(self):
        u"""
        关键词搜索后台接口
        :param key_word: String 从前台获取关键词进行搜索
        :return: SearchResult 关键词搜索结果集
        """
        
        key_words_str = web.input()['key_words']
        key_words = key_words_str.split()
        
        ip = web.ctx.ip
        service = SearchService.get_service_by_ip(ip)
        search_result = service.key_words_search(key_words)
        return json_encoder(search_result)

class FacetSearch:

    def GET(self):
        u"""
        分面搜索接口
        :param new_attr: int 新增分面属性
        :return SearchResult 分面搜索结果集
        """
        new_attr = int(web.input()['new_attr'])

        ip = web.ctx.ip
        service = SearchService.get_service_by_ip(ip)
        search_result = service.facet_search(new_attr)
        return json_encoder(search_result)

class ExpandSearch:

    def GET(self):
        u"""
        根据当前查询节点进行泛化
        :param degree: float 泛化程度 取值0~1 
        :return: SearchResult 泛化搜索结果集
        """
        return "ExpandSearch"


class DefineSearch:

    def GET(self):
        u"""
        根据当前查询节点进行细化
        :param degree: float 细化程度 取值0~1 
        :return: SearchResult 细化搜索结果集
        """
        return "DefineSearch"


class HistorySummary:

    def GET(self):
        u"""
        根据查询历史推荐结果
        :return: SearchResult 历史查询推荐结果集
        """
        return "HistorySummary"
    
    
if __name__ == '__main__':
    app.run()
