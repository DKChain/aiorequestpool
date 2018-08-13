# -*- coding:utf-8 -*-

import aiorequestpool

def get_status(request, resp):
    if resp.status == 200:
        return {'url':resp.url, 'status':resp.status, 'tag':request['args']['tag']}

if __name__ == "__main__":
    pool = aiorequestpool.AioRequestPool(callback = get_status, debug = True)
    request0 = {
        'url':'http://httpbin.org/post',
        'method':'post',
        'headers':{},
        'data':b'data',
        'args':{'tag':'http post'}
    }
    request1 = {
        'url':'http://httpbin.org/get',
        'method':'get',
        'headers':{},
        'args':{'tag':'http get'}
    }
    request2 = {
        'url':'https://www.baidu.com',
        'method':'get',
        'headers':{},
        'args':{'tag':'baidu'}
    }
    request3 = {
        'url':'https://www.google.com',
        'method':'get',
        'headers':{},
        'args':{'tag':'google'}
    }
    request4 = {
        'url':'https://www.github.com',
        'method':'get',
        'headers':{},
        'args':{'tag':'github'}
    }
    request5 = {
        'url':'https://dkchain.github.io',
        'method':'get',
        'headers':{},
        'args':{'tag':'blog'}
    }
    pool.append(request0)
    pool.append(request1)
    pool.append(request2)
    pool.append(request3)
    pool.append(request4)
    pool.append(request5)
    pool.run()

    print(pool.result)