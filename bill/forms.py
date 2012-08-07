# -*- coding: utf-8 -*-
from flask.ext.wtf import Form, TextField, BooleanField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from bill.models import Category


def get_categories():
    return Category.query.all()

class ItemForm(Form):
    date = DateField(u'Date', format='%Y-%m-%d')
    is_expense = BooleanField(u'Is Expense', default=True)
    amount = TextField(u'Amount')
    description = TextField(u'Description')
    category = QuerySelectField(u'Category', query_factory=get_categories, get_label='name')

    shortcut = TextField(u'Shortcut')
