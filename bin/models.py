# -*- coding: utf-8 -*-
u"""
ORM Model
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from json import JSONEncoder


Base = declarative_base()


class Book(Base):

    u"""
    :attribute id: 主键
    :attribute isbn: 图书编号
    :attribute book_title: 图书标题
    :attribute book_author: 图书作者
    :attribute year_of_publication: 出版年份
    :attribute publisher: 出版商
    :attribute image_url_s: 图片链接 小
    :attribute image_url_m: 图片链接 中
    :attribute image_url_l: 图片链接 大
    """

    __tablename__ = 'books_20k'

    id = Column(Integer, primary_key=True)
    isbn = Column(String(256))
    book_title = Column(String(256))
    book_author = Column(String(256))
    year_of_publication = Column(String(256))
    publisher = Column(String(256))
    image_url_s = Column(String(256))
    image_url_m = Column(String(256))
    image_url_l = Column(String(256))

    def __str__(self):

        return 'Book, {isbn=%s, book_title=%s, book_author=%s, year_of_publication=%s, publisher=%s,\
                image_url_s=%s, image_url_m=%s, image_url_l=%s}' % (self.isbn, self.book_title,\
                self.book_author, self.year_of_publication, self.publisher, self.image_url_s,\
                self.image_url_m, self.image_url_l)

    def __repr__(self):
        
        return '<Book(isbn=%s, book_title=%s, book_author=%s, year_of_publication=%s, publisher=%s,\
                image_url_s=%s, image_url_m=%s, image_url_l=%s)>' % (self.isbn, self.book_title,\
                self.book_author, self.year_of_publication, self.publisher, self.image_url_s,\
                self.image_url_m, self.image_url_l)

class BookEncoder(JSONEncoder):
    u"""
    JSONEncoder for class: Book
    """

    def default(self, book):
        if isinstance(book, Book):
            return {
                "isbn": book.isbn,
                "book_title": book.book_title,
                "book_author": book.book_author,
                "publisher": book.publisher,
                "year_of_publication": book.year_of_publication,
                "image_url_s": book.image_url_s,
                "image_url_m": book.image_url_m,
                "image_url_l": book.image_url_l
            }
        return JSONEncoder.default(self, book)


class FacetCode(Base):

    u"""
    :attribute id: 主键
    :attribute facet: 分面
    :attribute facet_value: 分面值
    """

    __tablename__ = 'facet_codes_20k'

    id = Column(Integer, primary_key=True)
    facet = Column(String(64))
    facet_value = Column(String(256))

    def __str__(self):

        return 'FacetCode, {facet=%s, facet_value=%s}' % (self.facet, self.facet_value)

    def __repr__(self):

        return '<FacetCode(facet=%s, facet_value=%s)' % (self.facet, self.facet_value)
