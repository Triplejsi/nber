import os
from random import randint

class Proxy:
    '''
    This class returns a string of proxy when making a request.
    '''

    def __init__(self):
        self.proxy_user = os.environ['PROXY_USER']
        self.proxy_password = os.environ['PROXY_PASSWORD']
        self.proxy_host = os.environ['PROXY_HOST']
        self.proxy_port = os.environ['PROXY_PORT']

    def get_server(self):
        '''
        Returns a  server
        '''
        server = os.environ['SERVER']
        server = server.split('\n')
        server = [x for x in server if x != '']

        return server

    def get_proxy(self):
        '''
        Returns a proxy
        '''
        server = self.get_server()
        index = randint(0, len(server) - 1)
        proxy = f'socks5h://{self.proxy_user}:{self.proxy_password}@{server[index]}.{self.proxy_host}:{self.proxy_port}'

        return proxy