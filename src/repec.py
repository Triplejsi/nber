import argparse
import json
import os
import pandas as pd
import requests
import sys
import traceback
import xml.etree.ElementTree as et
from average_time import AverageTime
from bs4 import BeautifulSoup
from datetime import datetime
from proxy import Proxy
from random import uniform, randint
from time import sleep

class RePEc:
    '''
    This class processes the XML API into a tabular DataFrame and save the output to .csv format.
    '''

    def __init__(self, nber_id, proxy):
        self.nber_id = nber_id
        self.proxy = proxy
        self.url = 'http://citec.repec.org/api/plain/RePEc:nbr:nberwo:'

    def string_id(self):
        '''
        Returns the string format for the NBER ID. For NBER ID above 1000 it will return itself.
        '''

        if self.nber_id < 10: return f'000{self.nber_id}'
        elif 10 <= self.nber_id < 100: return f'00{self.nber_id}'
        elif 100 <= self.nber_id < 1000: return f'0{self.nber_id}'
        else: return str(self.nber_id)

    def citation(self):
        '''
        Returns either numbers of citations or numbers of being cited if any, otherwise returns nothing.
        '''
        status_code = None
        while status_code != 200:
            url = f'{self.url}{self.string_id()}'
            response = requests.get(url, proxies={'http': self.proxy})
            status_code = response.status_code
            if status_code in [403, 404]:
                break
            try:
                xml = et.fromstring(response.text)
                return xml
            except UnboundLocalError: return None
            except et.ParseError: return None

    def reference(self):
        '''
        Returns a list of references for the corresponding NBER paper.
        '''
        status_code = None
        while status_code != 200:
            url = f'http://citec.repec.org/api/amf/RePEc:nbr:nberwo:{self.string_id()}'
            response = requests.get(url, proxies={'http': self.proxy}, timeout=5)
            status_code = response.status_code
            if status_code in [403, 404]:
                break
            try:
                parser = et.XMLParser(encoding='utf-8')
                xml = et.fromstring(response.text, parser=parser)
                text = list(xml)[0]
                reference = [list(x)[0].text for x in text if 'isreferencedby' not in x.tag]
                return reference
            except UnboundLocalError: return None
            except IndexError: return None
            except et.ParseError: return None

    def save(self):
        '''
        Save the paper using JSON format.
        '''
        # either cites or citedBy
        xml = self.citation()
        data = {
            'id': self.nber_id,
            'cites': int(xml.find('cites').text),
            'cited_by': int(xml.find('citedBy').text),
            'reference': self.reference()
        }

        with open(f'data/repec/{self.nber_id}.json', 'w') as file:
            json.dump(data, file, indent=4)

def main(start, end, interval):
    avg = AverageTime()
    timestamp = []
    while start < end:
        try:
            proxy = Proxy().get_proxy()
            repec = RePEc(start, proxy)
            _interval = round(uniform(interval, interval+1), 3)
            file_check = os.path.exists(f'data/repec/{start}.json')
            if not file_check:
                print(f'[DOWNLOAD \U0001F4BE]: {repec.url}{repec.string_id()}')
                start_timestamp = avg.current_timestamp()
                repec.save()
                print(f'[SUCCEED \U00002705]: {repec.url}{repec.string_id()}\n[SLEEP \U0001F634]: {_interval} seconds')
                end_timestamp = avg.current_timestamp()
                timestamp.append(avg.subtract(start_timestamp, end_timestamp))
                sleep(_interval)
            else:
                print(f'[IGNORE \U0001F4C1]: {repec.url}{repec.string_id()}')
        except Exception as err:
            print(traceback.print_exc())
            print(f'{err}: {start}')
            pass

        # break iteration if it reaches +3 hours
        # because max GitHub Actions for public is 6 hours
        if sum(timestamp) >= 10800:
            break
        
        start += 1
    
    return avg.result(timestamp)

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-s', '--start', type=int, default=0, help='Starting NBER ID', metavar='')
    PARSER.add_argument('-e', '--end', type=int, default=5, help='Ending NBER ID', metavar='')
    PARSER.add_argument('-i', '--interval', type=float, default=1, help='Time interval between iteration (in second)', metavar='')
    ARGS = PARSER.parse_args()
    START = ARGS.start
    END = ARGS.end
    INTERVAL = ARGS.interval
    main(start=START, end=END, interval=INTERVAL)
