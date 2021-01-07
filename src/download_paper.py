import os
import requests
import traceback
from proxy import Proxy

if __name__ == "__main__":
    nber_id = os.environ['NBER_ID']
    proxy = Proxy().get_proxy()
    status_code = None
    while status_code != 200:
        try:
            url = f'https://www.nber.org/system/files/working_papers/w{nber_id}/w{nber_id}.pdf'
            response = requests.get(url, proxies={'https': proxy})
            status_code = response.status_code
            if status_code == 404:
                break
            with open(f'paper/{nber_id}.pdf', 'wb') as file:
                file.write(response.content)
        except Exception as err:
            print(traceback.print_exc())
            print(f'{err}: {nber_id}')
            pass
