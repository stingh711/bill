# -*- coding: utf-8 -*-

from bill import app, parser
from bill.forms import ItemForm
from bill.models import db, Item, Category, SubCategory
from flask import render_template, redirect, url_for, request, jsonify
from sqlalchemy import func
from datetime import datetime

import simplejson


@app.route('/')
@app.route('/add', methods=['POST', 'GET'])
def add():
    form = ItemForm(csrf_enabled=False)
    if request.method == 'POST' and form.validate_on_submit():
        date = form.date.data
        is_expense = form.is_expense.data
        category = form.category.data
        amount = form.amount.data
        description = form.description.data
        item = Item(date=date, is_expense=is_expense, category=category, amount=amount, description=description)

        db.session.add(item)
        db.session.commit()
        return redirect(url_for('add'))
    else:
        return render_template('index.html', form=form)


@app.route('/quickadd', methods=['GET', 'POST'])
def quickadd():
    if request.method == 'GET':
        return render_template('quickadd.html')
    else:
        date_str = request.form['date']
        date = parse_date(date_str)
        content = request.form['content']
        item = parse_content(content)
        item.date = date

        db.session.add(item)
        db.session.commit()
        return redirect(url_for('quickadd'))


def parse_date(token):
    return datetime.strptime(token, '%Y-%m-%d').date()


def parse_content(content):
    if ':' in content:
        tokens = content.split(':')
        description = tokens[-1].strip()
        (subcategory_str, amount) = parse_subcategory_and_amount(tokens[0].split())
    else:
        tokens = content.split()
        (subcategory_str, amount) = parse_subcategory_and_amount(tokens)
        description = subcategory_str
    
    is_expense = not subcategory_str in ['salary', 'bonus']

    subcategory = SubCategory.query.filter(SubCategory.name == subcategory_str).first()
    return Item(amount, subcategory, description, is_expense)


def parse_subcategory_and_amount(tokens):
    amount = int(tokens[-1])
    subcategory_str = ' '.join(tokens[:-1])
    return (subcategory_str, amount)


@app.route('/import', methods=['POST', 'GET'])
def batchadd():
    if request.method == 'GET':
        return render_template('import.html')

    lines = request.form['lines']
    for line in lines.split('\n'):
        item = parser.parse_full(line)
        db.session.add(item)

    db.session.commit()
    return redirect(url_for('add'))


@app.route('/report')
def report():
    year = func.strftime('%Y', Item.date)
    years = db.session.query(year).group_by(year).all()

    month = func.strftime('%Y-%m', Item.date)
    months = db.session.query(month).group_by(month).all()
    results = []
    for m in months:
        tokens = m[0].split('-')
        results.append((tokens[0], tokens[1]))
    return render_template('report.html', years=years, months=results)


@app.route('/report_by_category/<year>/<category>')
def report_by_category(year, category):
    by_year = func.strftime('%Y', Item.date) == year
    items = db.session.query(func.sum(Item.amount), SubCategory.name).filter(Item.category_id == SubCategory.id).filter(SubCategory.parent_id == Category.id).filter(Category.name == category).filter(by_year).group_by(SubCategory.id).all()
    return render_template('year_report_by_category.html', items=items, year=year, category=category)

@app.route('/report/<year>/<month>')
def report_by_month(year, month):
    by_month = func.strftime('%Y-%m', Item.date) == '%s-%s' % (year, month)
    expense = db.session.query(func.sum(Item.amount)).filter(Item.is_expense == True).filter(by_month).first()[0]
    income = db.session.query(func.sum(Item.amount)).filter(Item.is_expense == False).filter(by_month).first()[0]

    items = Item.query.filter(by_month).filter(Item.is_expense == True).all()

    return render_template('report_month.html', expense=expense, income=income, total=income - expense, year=year, month=month, items=items)


@app.route('/report/<year>')
def report_by_year(year):
    by_year = func.strftime('%Y', Item.date) == year

    expense = db.session.query(func.sum(Item.amount)).filter(Item.is_expense == True).filter(by_year).first()[0]
    income = db.session.query(func.sum(Item.amount)).filter(Item.is_expense == False).filter(by_year).first()[0]

    expenses_by_category = db.session.query(func.sum(Item.amount), Category.name).filter(Item.category_id == SubCategory.id).filter(SubCategory.parent_id == Category.id).filter(by_year).filter(Item.is_expense == True).group_by(SubCategory.parent_id).all()
    return render_template('report_year.html', expense=expense, income=income, total=income - expense, year=year, expenses_by_category=expenses_by_category)


@app.route('/report/<year>/<month>/<category>')
def monthly_list_by_category(year, month, category):
    c = Category.query.filter_by(name=category).first()
    by_month = func.strftime('%Y-%m', Item.date) == '%s-%s' % (year, month)
    items = db.session.query(Item).filter(Item.is_expense == True).filter(by_month).filter_by(category=c).all()
    expense = db.session.query(func.sum(Item.amount)).filter(Item.is_expense == True).filter(by_month).first()[0]

    return render_template('monthly_list_by_category.html', items=items, year=year, month=month, category=category, total=expense)


@app.route('/items/<year>/<category>')
def items_list_by_category(year, category):
    by_year = func.strftime('%Y', Item.date) == year
    items = Item.query.filter(Item.category_id == SubCategory.id).filter(SubCategory.name == category).filter(by_year).all()
    return render_template('items_by_year_and_category.html', year=year, category=category, items=items)


@app.route('/_report/bymonth/<year>')
def year_report_by_month_json(year):
    by_year = func.strftime('%Y', Item.date) == year
    expenses = db.session.query(func.sum(Item.amount), func.strftime('%Y-%m', Item.date)).filter(by_year).filter(Item.is_expense == True).group_by(func.strftime('%Y-%m', Item.date)).all()
    cols = [{'id':'', 'label':'Month', 'type':'string'}, {'id':'', 'label':'Expense', 'type':'number'}]
    rows = []
    for (expense, month) in expenses:
        rows.append({'c': [{'v': month}, {'v': expense}]})
    return jsonify(cols=cols, rows=rows)


@app.route('/_report/bycategory/<year>')
def year_report_by_category_json(year):
    by_year = func.strftime('%Y', Item.date) == year
    expenses = db.session.query(func.sum(Item.amount), Category.name).filter(Item.category_id == SubCategory.id).filter(SubCategory.parent_id == Category.id).filter(by_year).filter(Item.is_expense == True).group_by(SubCategory.parent_id).all()
    cols = [{'id':'', 'label':'Category', 'type':'string'}, {'id':'', 'label':'Expense', 'type':'number'}]
    rows = []
    for (expense, category) in expenses:
        rows.append({'c': [{'v': category}, {'v': expense}]})
    return jsonify(cols=cols, rows=rows)


@app.route('/category')
def list_category():
    categories = Category.query.all()
    return render_template('list_category.html', categories=categories)


@app.route('/category/<int:category_id>')
def list_sub_category_of(category_id):
    category = Category.query.get(category_id)
    return render_template('list_subcategory.html', category=category)


@app.route('/category/<int:category_id>/add', methods=['POST'])
def add_subcategory(category_id):
    name = request.form['name']
    category = Category.query.get(category_id)
    sub = SubCategory(name=name)
    category.subcategories.append(sub)
    db.session.add(category)
    db.session.commit()
    return redirect(url_for('list_sub_category_of', category_id=category_id))


@app.route('/subcategory/delete/<int:id>')
def delete_subcategory(id):
    sub = SubCategory.query.get(id)
    db.session.delete(sub)
    db.session.commit()
    return redirect(url_for('list_sub_category_of', category_id=sub.parent.id))


@app.route('/_subcategory')
def get_subcategories_json():
    term = request.args.get('term', '')
    subcategories = SubCategory.query.filter(SubCategory.name.like('%%%s%%' % term)).all()
    names = []
    for sub in subcategories:
        names.append({"label":sub.name, "value":sub.name})

    return simplejson.dumps(names)

