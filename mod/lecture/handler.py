#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-10-26 12:46:36
# @Author  : yml_bright@163.com

from config import *
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from BeautifulSoup import BeautifulSoup
import tornado.web
import tornado.gen
import json
import urllib, re

class LectureHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('Herald Web Service')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        data = {
            'Login.Token1':self.get_argument('cardnum'),
            'Login.Token2':self.get_argument('password'),
        }
        try:
            client = AsyncHTTPClient()
            request = HTTPRequest(
                CHECK_URL,
                method='POST',
                body=urllib.urlencode(data),
                request_timeout=TIME_OUT)
            response = yield tornado.gen.Task(client.fetch, request)
            if response.body and response.body.find('Successed')>0:
                cookie = response.headers['Set-Cookie'].split(';')[0]
                client = AsyncHTTPClient()
                request = HTTPRequest(
                    LOGIN_URL,
                    method='GET',
                    headers={'Cookie':cookie},
                    request_timeout=TIME_OUT)
                response = yield tornado.gen.Task(client.fetch, request)

                cookie += ';' + response.headers['Set-Cookie'].split(';')[0]
                request = HTTPRequest(
                    USERID_URL,
                    method='GET',
                    headers={'Cookie':cookie},
                    request_timeout=TIME_OUT)
                response = yield tornado.gen.Task(client.fetch, request)
                soup = BeautifulSoup(response.body)
                userid = soup.findAll(attrs={"align": "left"})[2].text

                page = 1
                data = {
                    'account':userid,
                    'startDate':'',
                    'endDate':'',
                    'pageno':0
                }
                fliter = ['九龙湖', '手持考', '行政楼', '网络中', '机电大']
                lecture = []
                count = 0
                while 1:
                    data['pageno'] = page
                    request = HTTPRequest(
                        DATA_URL,
                        method='POST', 
                        body=urllib.urlencode(data),
                        headers={'Cookie':cookie},
                        request_timeout=TIME_OUT)
                    response = yield tornado.gen.Task(client.fetch, request)
                    soup = BeautifulSoup(response.body)
                    tr = soup.findAll('tr',{"class": re.compile("listbg")})
                    if not tr:
                        break
                    for td in tr:
                        td = td.findChildren()
                        if not td[4].text[:3].encode('utf-8') in fliter:
                            tmp = {}
                            tmp['date'] = td[0].text
                            tmp['place'] = td[4].text
                            lecture.append(tmp)
                            count += 1
                    page += 1
                self.write(json.dumps({'count':count, 'detial':lecture}, ensure_ascii=False, indent=2))
            else:
                self.write('wrong card number or password')
        except:
            self.write('error')
        self.finish()