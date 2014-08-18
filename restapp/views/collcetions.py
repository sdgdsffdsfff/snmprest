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

        if collections_list is None:
            return json.dumps({'data': [], 'error': 'true'})

        return json.dumps({'data': collections_list, 'error': 'true'})

    def get(self, collection_name):
        collection_items = mongo.db[collection_name].find().limit(20)

        collection_data = []

        if collection_items is not None:
            for item in collection_items:
                item['_id'] = str(item['_id'])
                collection_data.append(item)

            return json.dumps({'data': collection_data, 'error': 'false'})
        else:
            return json.dumps({'data': [], 'error': 'true'})