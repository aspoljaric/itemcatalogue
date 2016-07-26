from flask import Flask
app = Flask(__name__)

# Catalogue operations


@app.route('/')
@app.route('/catalogue')
def showCatalogues():
    return 'this page will show all my catalogues'


@app.route('/catalogue/new')
def newCatalogue():
    return 'this page will be for making a new catalogue'


@app.route('/catalogue/<int:catalogue_id>/edit')
def editCatalogue(catalogue_id):
    return 'this page will be for editing catalogue %s' % catalogue_id


@app.route('/catalogue/<int:catalogue_id>/delete')
def deleteCatalogue(catalogue_id):
    return 'this page will be for deleting catalogue %s' % catalogue_id
# Catalogue operations END

# Item operations


@app.route('/catalogue/<int:catalogue_id>')
@app.route('/catalogue/<int:catalogue_id>/items')
def showItems(catalogue_id):
    return 'this page will show the items for the catalogue %s' % catalogue_id


@app.route('/catalogue/<int:catalogue_id>/item/new')
def newItem(catalogue_id):
    return 'this page is for making a new item for catalogue %s' % catalogue_id


@app.route('/catalogue/<int:catalogue_id>/item/<int:item_id>/edit')
def editItem(catalogue_id, item_id):
    return 'this page is for making a editing item %s' % item_id


@app.route('/catalogue/<int:catalogue_id>/item/<int:item_id>/delete')
def deleteItem(catalogue_id, item_id):
    return 'this page is for making a deleting item %s' % item_id
# Item operations END

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
