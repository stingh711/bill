# -*- coding: utf-8 -*-
from datetime import date, timedelta, datetime
from bill.models import Category, Item, db

description_to_category = {
        'supper':'food', 'lunch':'food',
        'groceries':'food','salary':'salary',
        'morgage':'house'
        }

def parse_date(token):
    if token == 'today':
        return date.today()

    if token == 'yesterday':
        t = date.today()
        oneday = timedelta(days=1)
        return t - oneday

    return datetime.strptime(token, '%Y-%m-%d').date()


def parse_category_from_description(description):
    category_name = description_to_category[description]
    category = Category.query.filter_by(name=category_name).first()
    return category


def decide_is_expense(category):
    if category.name == 'salary':
        return False

    return True


def parse_shortcut(shortcut):
    tokens = shortcut.split()
    date = parse_date(tokens[0])
    category = parse_category_from_description(tokens[1])
    is_expense = decide_is_expense(category)
    amount = int(tokens[2])
    description = tokens[1]
    return Item(date=date, category=category, is_expense=is_expense, amount=amount, description=description)


def parse_full(line):
    tokens = line.split(',')
    date = parse_date(tokens[0])
    category = Category.query.filter_by(name=tokens[1]).first()
    if category == None:
        category = Category(name=tokens[1])
        db.session.add(category)
        db.session.commit()

    is_expense = decide_is_expense(category)
    amount = int(tokens[2])
    description = tokens[3]
    return Item(date=date, category=category, is_expense=is_expense, amount=amount, description=description)
