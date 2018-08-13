# -*- coding:utf-8 -*-

import asyncio
import aiohttp
import time

def log(ins, s):
    if ins.debug:
        print(s)


class AioResponse():
    """
    响应结果，包含url, 响应码, 响应头以及响应内容
    """
    def __init__(self, url, status, headers, text):
        self.status = status
        self.url = url
        self.headers = headers
        self.text = text


class AioRequest():
    """
    异步请求类，用于发送请求，参照requests用法
    """
    def __init__(self, debug = False):
        self.debug = debug

    async def request(self, method, url, **kwargs):
        try:
            log(self, "Getting page from %s..." % url)
            if kwargs['proxy_auth']:
                kwargs['proxy_auth'] = aiohttp.BasicAuth(kwargs['proxy_auth']['user'], kwargs['proxy_auth']['password'])
            else:
                del kwargs['proxy_auth']
            start = time.time()
            async with method(url, **kwargs) as response:
                end = time.time()
                log(self, "Get page %s done, used %.3f seconds" % (url, end - start))
                start = time.time()
                text = await response.text()
                end = time.time()
                log(self, "Get text of %s used %.3f seconds" % (url, end - start))
                res = AioResponse(response.url, response.status, response.headers, text)
        except Exception as e:
            log(self, "Exception has occured: %s" % str(e))
            res = AioResponse(url, 'cannot connect to server %s' % url, None, str(e))
        return res

    async def get(self, url, headers = None, cookies = None, proxy = None, proxy_auth = None, **kwargs):
        async with aiohttp.ClientSession(cookies = cookies) as session:
            return await self.request(session.get, url, headers = headers, proxy = proxy, proxy_auth = proxy_auth)

    async def post(self, url, headers = None, data = None, cookies = None, proxy = None, proxy_auth = None, **kwargs):
        async with aiohttp.ClientSession(cookies = cookies) as session:
            return await self.request(session.post, url, headers = headers, data = data, proxy = proxy, proxy_auth = proxy_auth)

    async def put(self, url, headers = None, data = None, cookies = None, proxy = None, proxy_auth = None, **kwargs):
        async with aiohttp.ClientSession(cookies = cookies) as session:
            return await self.request(session.put, url, headers = headers, data = data, proxy = proxy, proxy_auth = proxy_auth)
    
    async def delete(self, url, headers = None, cookies = None, proxy = None, proxy_auth = None, **kwargs):
        async with aiohttp.ClientSession(cookies = cookies) as session:
            return await self.request(session.delete, url, headers = headers, proxy = proxy, proxy_auth = proxy_auth)


class AioRequestPool:
    def __init__(self, max_req = 256, callback = None, debug = False):
        """
        callback用于处理每一个异步请求收到的响应，并将返回值添加在result列表里
        接受两个参数，request和response
        max_req是协程数量上限，防止同时打开的socket过多
        """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.sem = asyncio.Semaphore(max_req)
        self.requests = []  # 每个请求的参数的列表
        self.result = []
        self.pairs = []    # request, response和response的处理结果的字典
        self.callback_func = callback
        self.debug = debug

    def append(self, request):
        """
        request的格式，可以通过在request里面附加参数传入callback
        必填项:method,url;headers和data、cookies等根据需求自行填写
        {
            'method': 'GET',
            'url':'https://www.github.com',
            'headers':{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        } or 
        {
            'method': 'POST',
            'url':'http://httpbin.org/post',
            'headers':{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'},
            'data':b'data',
            'args':{
                'a':1,
                'b':2
            }
        }
        'args' means external argument of callback, this class will add it to callback if it
        exists in request dict
        """
        if isinstance(request, dict):
            self.requests.append(request)
        elif isinstance(request, list):
            for r in request:
                self.requests.append(r)
        else:
            print("Invalid request type")

    def callback(self, request, response):
        """
        调用传入的callback，没传入callback则不处理
        """
        if self.callback_func:
            return self.callback_func(request, response)
        return response

    async def send(self, request):
        browser = AioRequest(debug = self.debug)
        async with self.sem:
            if request['method'].lower() == 'get':
                response = await browser.get(**request)
            elif request['method'].lower() == 'post':
                response = await browser.post(**request)
            elif request['method'].lower() == 'put':
                response = await browser.put(**request)
            elif request['method'].lower() == 'delete':
                response = await browser.delete(**request)
            data = self.callback(request, response)
            self.result.append(data)
            self.pairs.append({
                'request':request,
                'response':response,
                'data':data
            })
            
    def run(self):
        """
        在创建好pool，添加完请求后需要调用这个函数用于发出请求，调用完成后result就是处理好的请求结果
        """
        start = time.time()
        self.loop.run_until_complete(asyncio.wait(map(self.send, self.requests)))
        end = time.time()
        log(self, "AioRequestPool total run %.5f seconds" % (end - start))

