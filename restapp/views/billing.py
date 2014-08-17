from flask.ext.classy import FlaskView
import json
from restapp import mongo
from restapp.portbilling import portBilling
from flask import request
import logging

class billingView(FlaskView):
    route_base = '/billing'

    methods = [
        '95th',
        'top30',
    ]

    request_args = [
        'dev_name',
        'port_name',
        'date',
    ]

    def index(self):
        return json.dumps({'methods': self.methods})

    def get(self, method):

        if not self.parseGetArgs(method):
            return self.error_str

        return self.calculatePort(method)

    def parseGetArgs(self, method):

        if method not in self.methods:
            self.error_str = json.dumps({'error':'method error!'})
            return False

        where_args = request.args.get('where')

        if where_args is None:
            self.error_str = json.dumps({'error':'request not contain "where" keyword !'})
            return False

        try:
            args_dict = json.loads(where_args.replace("'", "\""))
        except:
            self.error_str = json.dumps({'error':'request string ' + where_args + ' is not json string'})
            return False


        try:
            self.dev_name = args_dict['dev_name']
            self.port_name = args_dict['port_name']
            self.month = args_dict['month']
        except:
            self.error_str = json.dumps({'error':'request string keys error'})
            return False

        return True

    def calculatePort(self,method):
        collection_name = self.month + '_' + self.dev_name
        port_data_list = mongo.db[collection_name].find({'ifDescr': self.port_name})

        if port_data_list.count() == 0:
            logging.error("Cannot get data from {} with port {}".format(collection_name,self.port_name ))
            return json.dumps({'data':[],'length':0})

        self.port_billing = portBilling(port_data_list, method)

        port_result_list = self.port_billing.getPortDataPerDay()
        for item in port_result_list:
            print(item)

        port_result_month = self.port_billing.getPortDataPerMonth()
        print(port_result_month)

        return 'ok'

