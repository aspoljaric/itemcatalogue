from flask import Flask, render_template
app = Flask(__name__)

# Mock Categories
category = {'name': 'Soccer', 'id': '1'}
categories = [{'name': 'Soccer', 'id': '1'}, {
    'name': 'Tennis', 'id': '2'}, {'name': 'Football', 'id': '3'}]

# Mock Items
item = {'name': 'Ball', 'description': 'This is blue soccer ball.',
        'picture': 'pic', 'id': '1'}
items = [{'name': 'Ball', 'description': 'This is blue soccer ball.',
          'picture': 'pic', 'id': '1'},
         {'name': 'Tshirt', 'description': 'This is a tshirt.',
             'picture': 'pic', 'id': '2'},
         {'name': 'Shorts', 'description': 'Red shorts.',
          'picture': 'pic', 'id': '3'}]

# Category operations


@app.route('/')
@app.route('/catalogue')
def showCatalogues():
    return render_template('categories.html', categories=categories)


@app.route('/catalogue/new')
def newCategory():
    return render_template('new-category.html')


@app.route('/catalogue/<int:category_id>/edit')
def editCategory(category_id):
    return render_template('edit-category.html', category=category)


@app.route('/catalogue/<int:category_id>/delete')
def deleteCategory(category_id):
    return render_template('delete-category.html', category=category)
# Category operations END

# Item operations


@app.route('/catalogue/<int:category_id>')
@app.route('/catalogue/<int:category_id>/items')
def showItems(category_id):
    return render_template('items.html', items=items)


@app.route('/catalogue/<int:category_id>/item/new')
def newItem(category_id):
    return render_template('new-item.html')


@app.route('/catalogue/<int:category_id>/item/<int:item_id>/edit')
def editItem(category_id, item_id):
    return render_template('edit-item.html', item=item)


@app.route('/catalogue/<int:category_id>/item/<int:item_id>/delete')
def deleteItem(category_id, item_id):
    return render_template('delete-item.html', item=item)
# Item operations END

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
