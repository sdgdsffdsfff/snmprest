#condig: utf-8
import logging
import math
from restapp.billingmethod import percentile

class portBilling():
    raw_data = []
    data_list =  []

    def __init__(self, port_data, billing_method):

        if port_data is None or port_data.count() == 0:
            logging.error('portBilling raw data is empty')
        else:
            for data_items in port_data:
                self.raw_data.append(data_items)
                self.billing_method = billing_method


    def getPortDataPerDay(self):
        if self.raw_data is None:
            logging.error('getPortDataPerDay data is empty')
            return None

        data_result_list = []

        for port_data in self.raw_data:
            port_result = self.caculatePort(port_data, self.billing_method)
            data_result_list.append(port_result)

        return data_result_list

    def getPortDataPerMonth(self):
        if self.raw_data is None:
            logging.error('getPortDataPerMonth data is empty')
            return None

        ifHCInOctets_month = []
        ifHCOutOctets_month = []
        timeStamp_month = []

        for port_data in self.raw_data:
            ifHCInOctets_month += port_data['ifHCInOctets']
            ifHCOutOctets_month += port_data['ifHCOutOctets']
            timeStamp_month += port_data['timestamp']

        port_data_month = {
            'ifHCInOctets' : ifHCInOctets_month,
            'ifHCOutOctets' : ifHCOutOctets_month,
            'timestamp': timeStamp_month,
            'date': 'all',
        }

        port_result = self.caculatePort(port_data_month, self.billing_method)
        return port_result


    def caculatePort(self, port_data, billing_method):
        result = {}

        trafficResult = self.parsePortData(port_data)
        ifInList = sorted(trafficResult['ifHCInOctets'])
        ifOutList = sorted(trafficResult['ifHCOutOctets'])

        result =  {
            'ifIn_max': ifInList[-1],
            'ifOut_max' : ifOutList[-1],
            'ifIn_min': ifInList[0],
            'ifOut_min': ifOutList[0],
            'ifIn_avrg' : int(percentile(ifInList, 0.5)),
            'ifOut_avrg' : int(percentile(ifOutList, 0.5)),
            'date': port_data['date']
        }

        if billing_method == '95th':
            result['ifIn_95th'] = int(percentile(ifInList, 0.95))
            result['ifOut_95th'] = int(percentile(ifOutList, 0.95))

        return result

    def parsePortData(self, port_data):
        ifHCInOctets = self.countTraffic(port_data['ifHCInOctets'], port_data['timestamp'])
        ifHCOutOctets = self.countTraffic(port_data['ifHCOutOctets'], port_data['timestamp'])
        timeStamp = port_data['timestamp'][1:]

        result = {
            'ifHCInOctets' : ifHCInOctets,
            'ifHCOutOctets' : ifHCOutOctets,
            'timeStamp': timeStamp
        }

        return result

    def countTraffic(self, trafficData, timeData):

        if len(trafficData) <= 1 or len(trafficData) != len(timeData):
            logging.error('countTraffic params error!')
            return None

        trafficList = []

        for i in range(1, len(trafficData) ):
            trafficNow = int(trafficData[i])
            trafficLast = int(trafficData[i-1])
            diffTime = int(timeData[i]) - int(timeData[i-1])

            if trafficNow - trafficLast >= 0:
                # diffTraffic is in Byte unit so need to * 8 and / time interval
                trafficResult = (trafficNow -  trafficLast) * 8 / diffTime
                trafficList.append(int(trafficResult))
            else:
                # If traffic data is overflow here
                # Check it's 32 bit traffic or 64 bit traffic
                if trafficLast > math.pow(2,32):
                    max_traffic =  math.pow(2, 64)
                else:
                    max_traffic = math.pow(2,32)

                trafficResult = (max_traffic - trafficLast + trafficNow) * 8 / diffTime
                trafficList.append(int(trafficResult))

        return trafficList