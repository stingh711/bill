# -*- coding: utf-8 -*-
from bill import parser
from datetime import date

def test_parse_date():
    assert parser.parse_date('today') == date.today()


def test_get_category():
    assert parser.parse_category_from_description('supper').name == 'food'


def test_parse_shortcut():
    i = parser.parse_shortcut('today supper 10')
    assert i.date == date.today()
    assert i.category.name == 'food'
    assert i.is_expense == True
    assert i.description == 'supper'
    assert i.amount == 10
