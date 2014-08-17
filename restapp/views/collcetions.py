from flask.ext.classy import FlaskView
import json
from restapp import mongo

class collcetionsView(FlaskView):
    route_base = '/collections'

    def index(self):
        collections_list = mongo.db.collection_names()
        try:
            collections_list.remove('system.indexes')
        except ValueError:
            pass

        return json.dumps({'collections': collections_list})

    def get(self, collection_name):
        collection_items = mongo.db[collection_name].find().limit(20)

        collection_list = []

        if collection_items is not None:
            for item in collection_items:
                item['_id'] = str(item['_id'])
                collection_list.append(item)

            return json.dumps({'_items': collection_list, 'length': len(collection_list)})
        else:
            return json.dumps({'_items': [], 'length': 0})