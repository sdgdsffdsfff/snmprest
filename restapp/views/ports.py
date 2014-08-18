from flask.ext.classy import FlaskView
import json
from restapp import mongo

class portsView(FlaskView):
    route_base = '/ports'

    def index(self):
        ports_rows = mongo.db['ports'].find()

        ports_list = []

        if ports_rows is not None:
            for item in ports_rows:
                ports_list.append(item['dev_name'])

            return json.dumps({'data': ports_list, 'error': 'false'})
        else:
            return json.dumps({'data': [], 'error': 'true'})

    def get(self, dev_name):

        port_info = mongo.db['ports'].find_one({'dev_name': dev_name})

        if port_info is None:
            return json.dumps({'data': [], 'error': 'true'})

        return json.dumps({'data': port_info['port_list'], 'error': 'false'})
