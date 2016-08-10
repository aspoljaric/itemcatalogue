from flask import Flask, render_template, url_for, request, redirect, jsonify
app = Flask(__name__)

from database import Base, Category, Item
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy_imageattach import store


def connect():
    """Connect to the SQLite database.  Returns a database session."""
    try:
        engine = create_engine('sqlite:///categories.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        return session
    except:
        print("Connection failed.")


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = connect()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# Category operations


@app.route('/')
@app.route('/catalogue')
def showCatagories():
    with session_scope() as session:
        categories = session.query(Category).all()
        return render_template('categories.html', categories=categories)


@app.route('/catalogue/new', methods=['GET', 'POST'])
def newCategory():
    with session_scope() as session:
        if request.method == 'POST':
            newCategory = Category(name=request.form['name'])
            session.add(newCategory)
            return redirect(url_for('showCatagories'))
        else:
            return render_template('new-category.html')


@app.route('/catalogue/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    with session_scope() as session:
        category = session.query(Category).filter_by(id=category_id).one()
        if request.method == 'POST':
            category.name = request.form['name']
            session.add(category)
            return redirect(url_for('showCatagories'))
        else:
            return render_template('edit-category.html', category=category)


@app.route('/catalogue/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    with session_scope() as session:
        category = session.query(Category).filter_by(id=category_id).one()
        if request.method == 'POST':
            if category is not None:
                session.delete(category)
                return redirect(url_for('showCatagories'))
        else:
            return render_template('delete-category.html', category=category)
# Category operations END

# Item operations


@app.route('/catalogue/<int:category_id>')
@app.route('/catalogue/<int:category_id>/items')
def showItems(category_id):
    with session_scope() as session:
        category = session.query(Category).filter_by(id=category_id).one()
        items = session.query(Item).filter_by(category_id=category_id).all()
        return render_template('items.html', items=items,
                               category_id=category_id)


@app.route('/catalogue/<int:category_id>/item/new', methods=['GET', 'POST'])
def newItem(category_id):
    with session_scope() as session:
        if request.method == 'POST':
            newItem = Item(name=request.form['name'],
                           description=request.form['description'],
                           category_id=category_id)
            #picture_url = request.values['picture']
            # newItem.picture.from_file(urlopen(picture_url))
            session.add(newItem)
            return redirect(url_for('showItems', category_id=category_id))
        else:
            category = session.query(Category).filter_by(id=category_id).one()
            return render_template('new-item.html', category=category)


@app.route('/catalogue/<int:category_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    with session_scope() as session:
        item = session.query(Item).filter_by(id=item_id).one()
        category = session.query(Category).filter_by(id=category_id).one()
        if request.method == 'POST':
            item.name = request.form['name']
            item.description = request.form['description']
            item.picture = request.form['picture']
            session.add(item)
            return redirect(url_for('showItems', category_id=category_id))
        else:
            return render_template('edit-item.html', category=category,
                                   item=item)


@app.route('/catalogue/<int:category_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    with session_scope() as session:
        if request.method == 'POST':
            session.query(Item).filter_by(id=item_id).delete()
            return redirect(url_for('showItems', category_id=category_id))
        else:
            item = session.query(Item).filter_by(id=item_id).one()
            return render_template('delete-item.html', item=item)
# Item operations END


# JSON API Endpoints
@app.route('/catalogue/JSON')
def catagoriesJSON():
    with session_scope() as session:
        categories = session.query(Category).all()
        return jsonify(Categories=[category.serialize
                                   for category in categories])


@app.route('/catalogue/<int:category_id>/items/JSON')
def categoryItemsJSON(category_id):
    with session_scope() as session:
        items = session.query(Item).filter_by(category_id=category_id).all()
        return jsonify(Items=[item.serialize for item in items])


@app.route('/catalogue/<int:category_id>/item/<int:item_id>/JSON')
def itemInCategoryJSON(category_id, item_id):
    with session_scope() as session:
        item = session.query(Item).filter_by(
            category_id=category_id).filter_by(id=item_id).one()
        return jsonify(Item=[item.serialize])
# JSON API Endpoints END

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
