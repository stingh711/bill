# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from bill import app
from datetime import date as d

db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(10))
    subcategories = db.relationship('SubCategory', backref='parent')

    def __init__(self, name):
        self.name = name


    def __repr__(self):
        return "<Category> %s" % self.name


class SubCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(10))

    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    
    def __init__(self, name):
        self.name = name


    def __repr__(self):
        return '<SubCategory> %s' % self.name


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    date = db.Column(db.Date)
    is_expense = db.Column(db.Boolean)
    amount = db.Column(db.Integer)
    description = db.Column(db.String)
    
    category_id = db.Column(db.Integer, db.ForeignKey('sub_category.id'))
    category = db.relationship('SubCategory')

    def __init__(self, amount, category, description, is_expense=True, date=None):
        self.amount = amount
        self.category = category
        self.is_expense = is_expense
        if date is None:
            date = d.today()
        self.date = date
        self.description = description

    def __repr__(self):
        return "<Item %r>" % self.description
