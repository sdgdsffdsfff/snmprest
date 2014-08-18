from flask.ext.classy import FlaskView
import json
from restapp import mongo
from restapp.portbilling import portBilling
from flask import request
import logging

class billingView(FlaskView):
    route_base = '/billing'

    request_args = {
        'dev_name': 'must',
        'port_name': 'must',
        'month': 'must',
        'datetype': 'must',
        'billing_method': 'optional',
    }

    def index(self):
        return json.dumps({'error':'false', 'data':self.request_args})

    def get(self):

        if not self.parseGetArgs():
            return self.error_str

        return self.calculatePort()

    def parseGetArgs(self):

        where_args = request.args.get('where')

        if where_args is None:
            self.error_str = json.dumps({'error':'true','errormsg':'request not contain "where" keyword !'})
            return False

        try:
            args_dict = json.loads(where_args.replace("'", "\""))
        except:
            self.error_str = json.dumps({'error':'true','errormsg':'request string ' + where_args + ' is not json string'})
            return False

        try:
            self.dev_name = args_dict['dev_name']
            self.port_name = args_dict['port_name']
            self.month = args_dict['month']
            self.datetype = args_dict['datetype']
        except:
            self.error_str = json.dumps({'error':'true','errormsg':'request string keys error'})
            return False

        if 'billling_method' in args_dict:
            self.billing_method = args_dict['billling_method']
        else:
            self.billing_method = None

        return True

    def calculatePort(self):
        collection_name = self.month + '_' + self.dev_name
        port_data_list = mongo.db[collection_name].find({'ifDescr': self.port_name})

        if port_data_list.count() == 0:
            logging.error("Cannot get data from {} with port {}".format(collection_name,self.port_name ))
            return json.dumps({'data':[],'length':0})

        self.port_billing = portBilling(port_data_list, self.datetype, self.billing_method)

        if self.datetype == 'month':
            result = self.port_billing.getPortDataPerMonth()

        elif self.datetype == 'allday':
            result = self.port_billing.getPortDataPerDay()

        else:
            result = self.port_billing.getPortDataPerDay(self.datetype)

        if result is not None:
            return json.dumps({'data': result, 'error': 'false'})
        else:
            return json.dumps({'error': 'true', 'data': []})
