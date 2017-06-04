# -*- coding: utf-8 -*-
from nose.tools import *
from stuff import *

@istest
def test_get_session():
    session = DBHelper.get_session()

