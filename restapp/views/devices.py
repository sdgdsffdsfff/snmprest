from flask.ext.classy import FlaskView
import json
from restapp import mongo

class devicesView(FlaskView):
    route_base = '/devices'

    def index(self):
        devices_rows = mongo.db['devices'].find()

        devices_list = []

        if devices_rows is not None:
            for item in devices_rows:
                devices_list.append(item['dev_name'])

            return json.dumps({'data': devices_list, 'error': 'false'})
        else:
            return json.dumps({'data': [], 'error': 'true'})

    def get(self, dev_name):

        device_info = mongo.db['devices'].find_one({'dev_name': dev_name})

        if device_info is None:
            return json.dumps({'data': [], 'error': 'true'})

        try:
            del device_info['_id']
            del device_info['community']
        except:
            pass

        return json.dumps({'data': device_info, 'error': 'false'})
