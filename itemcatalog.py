from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import session, flash, make_response
from werkzeug.contrib.cache import SimpleCache

from db.database import User, Category, Item, get, getOne, getTable

import login
import os
import sys


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'db/img'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
cache = SimpleCache()



@app.route('/login/')
def showlogin():
    return login.login()


@app.route('/gconnect', methods=['POST'])
def gconnect():
    return login.gconnect(session)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    return login.fbconnect(session)


@app.route('/logout/')
def logout():
    print login.logout(session)
    return redirect(url_for('index'))



def render(template, **kw):
    loggedIn = 'provider' in session
    return render_template(template, categories=cache.get('categories'),
                            loggedIn=loggedIn, **kw)


@app.route('/')
@app.route('/index/')
def index():
    items = get(Item, "categoryId", 1) #need to update
    return render('index.html', title="Home page", items=items)


@app.route('/category/<int:categoryId>')
def category(categoryId):
    items = get(Item, "categoryId", categoryId)
    category = getOne(Category, "id", categoryId).name
    return render('category.html', title=category, items=items)


@app.route('/item/<int:itemId>')
def item(itemId):
    item = get(Item, "id", itemId)[0]
    return render('item.html', title=item.category.name,
                  titleUrl=url_for('category', categoryId=item.category.id),
                  item=item)


@app.route('/item/new/', methods=['GET', 'POST'])
def newItem():
    item=Item()
    if request.method == 'POST':
        if Item.save(item, request.form, request.files['picfile']):
            return render('item.html', title=item.category.name,
                          titleUrl=url_for('category', categoryId=item.category.id),
                          item=item)

    return render('saveitem.html', title="New Item", item=item,
                   formAction=url_for('newItem'), cancel=url_for('index'))


@app.route('/item/<int:itemId>/edit/', methods=['GET', 'POST'])
def editItem(itemId):
    item = getOne(Item, 'id', itemId)
    if request.method == 'POST':
        if Item.save(item, request.form, request.files['picfile']):
            return render('item.html', title=item.category.name,
                          titleUrl=url_for('category', categoryId=item.category.id),
                          item=item)

    return render('saveitem.html', title="Edit Item",
                   categoryId=item.categoryId, item=item,
                   formAction=url_for('editItem', itemId=item.id),
                   cancel=url_for('item', itemId=itemId))



@app.route('/item/<int:itemId>/delete/', methods=['GET', 'POST'])
def deleteItem(itemId):
    try:
        item = getOne(Item, 'id', itemId)
        categoryId = item.category.id
        if request.method == 'POST':
            Item.delete(item)
            return redirect(url_for('category', categoryId=categoryId))

        return render('deleteitem.html', title="Delete Item", item=item)
    except:
        pass


def startServer():

    app.secret_key = 'super_secret_key'
    app.debug = True
    cache.set('categories', getTable(Category), 3600)
    app.run(host='0.0.0.0', port=8000)

if __name__ == '__main__':
    startServer()
