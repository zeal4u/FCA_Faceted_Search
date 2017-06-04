# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import sessionmaker

# important
Base = declarative_base()


"""
ORM manager module
"""


class DBHelper(object):
    """
    Tool class for ORM
    """
    engine = None
    session = None
    __cache = {}

    @staticmethod
    def get_connect(user='zeal4u', passwd='123456', db='faceted_search_dataset', host='localhost'):
        """
        this is a static method
        :param str user:
        :param str passwd:
        :param str db:
        :param str host:
        :return: the sqlalchemy engine
        """
        # Lazy Connecting
        if not DBHelper.engine:
            DBHelper.engine = create_engine('mysql+mysqlconnector://%s:%s@%s/%s' %
                                            (user, passwd, host, db), echo=True)
        return DBHelper.engine

    @staticmethod
    def get_session():

        if not DBHelper.session:
            Session = sessionmaker(bind=DBHelper.get_connect())  # this is likely a factory
            DBHelper.session = Session()
        return DBHelper.session

    @staticmethod
    def _get_by_codes(model, codes):
        u"""
        """
        if model.__tablename__ not in DBHelper.__cache:
            session = DBHelper.get_session()
            result = session.query(model).all()
            DBHelper.__cache[model.__tablename__] = result
        else:
            result = DBHelper.__cache[model.__tablename__]
        if not codes:
            return result

        filter_result = []
        for r in result:
            if r.id in codes:
                filter_result.append(r)
        return filter_result

    @staticmethod
    def get_objs_by_codes(model, codes):
        u"""
        根据对象代码获取对象数据
        :param model: sqlalchemy model 
        :param codes: List[int] 对象代码列表
        """
        return DBHelper._get_by_codes(model, codes)

    @staticmethod
    def get_attrs_by_codes(model, codes):
        u"""
        根据属性代码获取属性数据
        :param model: sqlalchemy model 
        :param codes: List[int] 对象代码列表
        """
        return DBHelper._get_by_codes(model, codes)
   
    @staticmethod
    def get_data(model, num):
        u"""
        获取源数据用于构建概念格
        :param model: sqlalchemy model 
        :param num: int 设定获取对象的数目
        """
        pass
 
# # if tables have not been created then create them
# Base.metadata.create_all(DBHelper.get_connect())
