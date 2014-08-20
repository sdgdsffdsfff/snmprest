from flask.ext.classy import FlaskView
import json
from restapp import mongo
from restapp.portbilling import portBilling
from flask import request, make_response
import logging

class reportView(FlaskView):
    route_base = '/report'

    request_args = {
        'dev_name': 'must',
        'port_name': 'must',
        'month': 'must',
        'billing_method': 'must',
    }

    def index(self):
        return json.dumps({'error':'false', 'data':self.request_args})

    def post(self):

        if not self.parseGetArgs():
            return None

        # self.port_list = [
        #     {'dev_name':'s9312-254',
        #      'port_name':'Ethernet2/0/0',
        #      'month': '201408',
        #      'billing_method': '95th',
        #     },
        # ]

        csv_data = self.generatePortReportList()

        if csv_data is not None:
            response = make_response(csv_data)
            response.headers["Content-Disposition"] = "attachment; filename=books.csv"
            return response

        else:
            logging.error("Cannot generate csv file")
            return None

    def parseGetArgs(self):
        try:
            self.port_list = request.form['port_list']
        except:
            logging.error('Request param error!')
            return False

        return True

    def generatePortReportList(self):
        csv_string = ''

        for item in self.port_list:
            csv_string += self.generatePortReport(item)
            csv_string += '\n\n'

        return csv_string


    def generatePortReport(self, port_args, csv_split=','):
        collection_name = port_args['month'] + '_' + port_args['dev_name']
        port_data_list = mongo.db[collection_name].find({'ifDescr': port_args['port_name']})

        if port_data_list.count() == 0:
            logging.error("Cannot get data from {} with port {}".format(collection_name,port_args['port_name'] ))
            return None

        port_billing = portBilling(port_data_list, port_args['billing_method'])

        # 得到当月的每日详细值
        day_result = port_billing.getPortDataPerDay()

        # 得到当月的总计值
        month_result = port_billing.getPortDataPerMonth()

        # CSV报表的基本信息
        csv_string = ''
        csv_string += csv_split.join(['设备名称:',port_args['dev_name']])
        csv_string += '\n'
        csv_string += csv_split.join(['端口名称:',port_args['port_name']])
        csv_string += '\n'
        csv_string += csv_split.join(['计费时间段:', port_args['month']])
        csv_string += '\n'

        # CSV报表的计费信息表示 和 当月统计值
        date_list = ['', '总计']
        billing_list = ['计费 (95th)', month_result['report_billing']]
        avrg_list = ['平均值 (In/Out)', month_result['report_avrg']]
        max_list = ['最大值 (In/Out)', month_result['report_max']]
        min_list = ['最小值 (In/Out)',  month_result['report_min']]

        # CSV报表的每日详细信息
        for port_item in day_result:
            date_list.append(port_item['date_type'])
            billing_list.append(port_item['report_billing'])
            avrg_list.append(port_item['report_avrg'])
            max_list.append(port_item['report_max'])
            min_list.append(port_item['report_min'])


        # CSV的详细计费字段
        csv_string += '\n'
        csv_string += csv_split.join(date_list)
        csv_string += '\n'
        csv_string += csv_split.join(billing_list)
        csv_string += '\n'
        csv_string += csv_split.join(avrg_list)
        csv_string += '\n'
        csv_string += csv_split.join(max_list)
        csv_string += '\n'
        csv_string += csv_split.join(min_list)
        csv_string += '\n'

        return csv_string
