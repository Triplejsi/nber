import os

class Proxy:
    '''
    This class returns a string of proxy when making a request.
    '''

    def __init__(self):
        self.proxy_user = os.environ['PROXY_USER']
        self.proxy_password = os.environ['PROXY_PASSWORD']
        self.proxy_host = os.environ['PROXY_HOST']
        self.proxy_port = os.environ['PROXY_PORT']
        self.proxy_server = os.environ['PROXY_SERVER']

    def get_proxy(self):
        '''
        Returns a proxy
        '''

        proxy = f'socks5h://{self.proxy_user}:{self.proxy_password}@{self.proxy_server}.{self.proxy_host}:{self.proxy_port}'

        return proxy