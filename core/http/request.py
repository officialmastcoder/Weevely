'''
Created on 03/ott/2011

@author: emilio
'''

import urllib2, socks
from random import choice
from socksipyhandler import SocksiPyHandler
from re import compile, IGNORECASE
from urllib import urlencode
from core.moduleexception import ModuleException

WARN_UNCORRECT_PROXY = 'Incorrect proxy format, set it as \'http|https|socks5|sock4://host:port\''

url_dissector = compile(
    r'^(https?|socks4|socks5)://' # http:// or https://
    r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r':(\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', IGNORECASE)

agent = choice((
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0) Gecko/20100101 Firefox/17.0",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)",
    "Opera/9.20 (Windows NT 6.0; U; en)",
    "Opera/9.00 (Windows NT 5.1; U; en)",
    "Googlebot/2.1 ( http://www.googlebot.com/bot.html)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.95 Safari/537.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:17.0) Gecko/20100101 Firefox/17.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11",
    "Mozilla/5.0 (Linux; U; Android 2.2; fr-fr; Desire_A8181 Build/FRF91)",
))

class Request:

    def __init__(self, url, proxy=''):
        self.url = url
        self.data = {}
        
        proxydata = self.__parse_proxy(proxy)
        
        if proxydata:
            self.opener = urllib2.build_opener(SocksiPyHandler(*proxydata))
        else:
            self.opener = urllib2.build_opener()
            
        self.opener.addheaders = [('User-agent', agent)]
       
    def __parse_proxy(self, proxyurl):

        if proxyurl:
            
            url_dissected = url_dissector.findall(proxyurl)
            if url_dissected and len(url_dissected[0]) == 3:
                protocol, host, port = url_dissected[0]
                if protocol == 'socks5': return (socks.PROXY_TYPE_SOCKS5, host, int(port))
                if protocol == 'socks4': return (socks.PROXY_TYPE_SOCKS4, host, int(port))
                if protocol.startswith('http'): return (socks.PROXY_TYPE_HTTP, host, int(port))
                
            raise ModuleException('request',WARN_UNCORRECT_PROXY)
                    
        return []
            
    def __setitem__(self, key, value):
        self.opener.addheaders.append((key, value))

    def read(self, bytes= -1):

        try:
            if self.data:
                handle = self.opener.open(self.url, data=urlencode(self.data))
            else:
                handle = self.opener.open(self.url)
        except urllib2.HTTPError, handle:
            pass
        

        if bytes > 0:
            return handle.read(bytes)
        else:
            return handle.read()