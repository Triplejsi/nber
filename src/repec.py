import argparse
import json
import os
import pandas as pd
import requests
import sys
import traceback
import xml.etree.ElementTree as et
from bs4 import BeautifulSoup
from datetime import datetime
from random import uniform, randint
from time import sleep

class Proxy:

    def __init__(self):
        self.proxy_user = os.environ['PROXY_USER']
        self.proxy_password = os.environ['PROXY_PASSWORD']
        self.proxy_host = os.environ['PROXY_HOST']
        self.proxy_port = os.environ['PROXY_PORT']

    def get_server(self):
        server = [
            'tia',
            'eze',
            'bne',
            'mel',
            'per',
            'syd',
            'vie',
            'bru',
            'gig',
            'gru',
            'sof',
            'yul',
            'tor',
            'yvr',
            'scl',
            'bog',
            'sjo',
            'zag',
            'prg',
            'cph',
            'tll',
            'hel',
            'bod',
            'mrs',
            'par',
            'fra',
            'ath',
            'bud',
            'rkv',
            'bom',
            'del',
            'dub',
            'tlv',
            'lin',
            'nrt',
            'sel',
            'rix',
            'lux',
            'kul',
            'gdl',
            'kiv',
            'ams',
            'akl',
            'los',
            'osl',
            'lim',
            'waw',
            'lis',
            'otp',
            'beg',
            'sin',
            'bts',
            'lju',
            'jnb',
            'mad',
            'vlc',
            'sto',
            'zrh',
            'tpe',
            'iev',
            'dxb',
            'iad',
            'atl',
            'bos',
            'clt',
            'chi',
            'dal',
            'den',
            'hou',
            'las',
            'lax',
            'mia',
            'msy',
            'nyc',
            'phx',
            'sjc',
            'sea'
        ]

        return server

    def get_proxy(self):
        server = self.get_server()
        index = randint(0, len(server) - 1)
        proxy = f'socks5://{self.proxy_user}:{self.proxy_password}@{server[index]}.{self.proxy_host}:{self.proxy_port}'

        return proxy

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

    def citation(self, xml_find):
        '''
        Returns either numbers of citations or numbers of being cited if any, otherwise returns nothing.
        '''
        status_code = None
        while status_code != 200:
            try:
                url = f'{self.url}{self.string_id()}'
                response = requests.get(url, proxies={'http': self.proxy, 'https': self.proxy})
                status_code = response.status_code
                xml = et.fromstring(response.text)
                # either cites or citedBy
                xml = int(xml.find(xml_find).text)
                if status_code == 200:
                    try: return xml
                    except UnboundLocalError: return None
            except et.ParseError: return None
            except AttributeError: sys.exit(0)
            except Exception as err:
                print(traceback.print_exc())
                print(f'{err}: {self.nber_id}')
                sys.exit(1)

    def reference(self):
        '''
        Returns a list of references for the corresponding NBER paper.
        '''
        status_code = None
        while status_code != 200:
            try:
                url = f'http://citec.repec.org/api/amf/RePEc:nbr:nberwo:{self.string_id()}'
                response = requests.get(url, proxies={'http': self.proxy, 'https': self.proxy})
                status_code = response.status_code
                parser = et.XMLParser(encoding='utf-8')
                xml = et.fromstring(response.text, parser=parser)
                text = list(xml)[0]
                reference = [list(x)[0].text for x in text if 'isreferencedby' not in x.tag]
                if status_code == 200:
                    try: return reference
                    except UnboundLocalError: return None
                    except IndexError: return None
            except et.ParseError: return None
            except AttributeError: sys.exit(0)
            except Exception as err:
                print(traceback.print_exc())
                print(f'{err}: {self.nber_id}')
                sys.exit(1)

    def save(self):
        '''
        Save the paper using JSON format.
        '''

        data = {
            'id': self.nber_id,
            'cites': self.citation('cites'),
            'cited_by': self.citation('citedBy'),
            'reference': self.reference()
        }

        with open(f'data/repec/{self.nber_id}.json', 'w') as file:
            json.dump(data, file, indent=4)

class AverageTime:
    '''
    This class calculates the average scraping time per paper.
    '''

    def current_timestamp(self):
        '''
        Returns a timestamp in UTC.
        '''

        return datetime.utcnow()

    def subtract(self, start, end):
        '''
        Subtract the end timestamp with the start timestamp.
        '''

        return (end - start).total_seconds()
    
    def result(self, timestamp):
        '''
        Prints the average scraping time for each paper in second.
        '''

        timestamp = round((sum(timestamp) / len(timestamp)), 3) if timestamp != [] else 0
        print(f'On average, the operation takes {timestamp} second(s).')

def main(start, end, interval):
    avg = AverageTime()
    timestamp = []
    while start < end:
        proxy = Proxy().get_proxy()
        repec = RePEc(start, proxy)
        _interval = round(uniform(interval, interval+1), 3)
        file_check = os.path.exists(f'data/repec/{start}.json')
        if not file_check:
            print(f'[DOWNLOAD \U0001F4BE]: {repec.url}{repec.string_id()}')
            start_timestamp = avg.current_timestamp()
            repec.save()
            print(f'[SUCCEED \U00002705]: {repec.url}{repec.string_id()}.\n[SLEEP \U0001F634]: {_interval} seconds')
            end_timestamp = avg.current_timestamp()
            timestamp.append(avg.subtract(start_timestamp, end_timestamp))
            sleep(_interval)
        else:
            print(f'[IGNORE \U0001F4C1]: {repec.url}{repec.string_id()}')
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
