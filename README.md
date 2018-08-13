# aiorequestpool
自用异步请求池，可以将大量请求添加到pool中，调用一次即可发出异步请求，支持传入callback函数用于处理响应结果。可用于爬虫，大量接口提交等场景

## 依赖
* aiohttp
* asyncio(Python3.4及以上)