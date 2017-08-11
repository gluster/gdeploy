#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Nandaja Varma <nvarma@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.



import eventlet, argparse
from eventlet import wsgi
from cStringIO import StringIO
import re, tempfile, subprocess
from ast import literal_eval
from gdeploylib import Helpers

class RecordList():
    record = {}


def get_request_handler(env, start_response):
    uri = re.match(r'/gdeploy/config/(.*)', env['PATH_INFO'])
    if not uri:
        start_response('400 Bad Request', [('Content-Type',
            'application/json')])
        return ['400 Bad Request\r\n']
    data = RecordList.record.get(uri.group(1))
    if not data:
        start_response('404 Not Found', [('Content-Type',
            'application/json')])
        return ['404 Not Found\r\n']
    start_response('200 OK', [('Content-Type', 'application/json')])
    return [data + '\r\n']

def post_request_handler(env, start_response):
    helpers = Helpers()
    add = re.match(r'/gdeploy/config/(.+)', env['PATH_INFO'])
    deploy = re.match(r'/gdeploy/deployconfig/(.+)', env['PATH_INFO'])
    if add:
        if env['CONTENT_TYPE'] != 'application/json':
            start_response('304 Not Modified', [('Content-Type',
                'application/json')])
            return ['304 Not Modified\r\n']
        if add.group(1) not in RecordList.record:
            length = int(env.get('CONTENT_LENGTH', '0'))
            body = StringIO(env['wsgi.input'].read(length))
            content = body.getvalue()
            RecordList.record[add.group(1)] = content
            start_response('201 Created', [('Content-Type', 'application/json')])
            return ['201 Created\r\n']
        start_response('422 Unprocessable Entity', [('Content-Type', 'application/json')])
        return ['422 Unprocessable Entity\r\n']
    elif deploy:
        content = RecordList.record.get(deploy.group(1))
        if not content:
            start_response('404 Not Found', [('Content-Type',
                'application/json')])
            return ['404 Not Found\r\n']
        data = literal_eval(content)
        config_file = tempfile.mkstemp()[1]
        for key, value in data.iteritems():
            helpers.write_config(key, value, config_file)
        command = 'gdeploy -c %s' % config_file
        subprocess.call(command.split(),
                stdin=None, stdout=None, stderr=None, shell=False)
        start_response('200 OK', [('Content-Type', 'application/json')])
        return ['200 OK\r\n']
    else:
        start_response('400 Bad Request', [('Content-Type',
            'application/json')])
        return ['400 Bad Request\r\n']

def put_request_handler(env, start_response):
    d_ret = delete_request_handler(env, start_response)
    if d_ret != ['200 OK\r\n']:
        return d_ret
    a_ret = post_request_handler(env, start_response)
    return d_ret


def delete_request_handler(env, start_response):
    uri = re.match(r'/gdeploy/config/(.*)', env['PATH_INFO'])
    if not uri:
        start_response('400 Bad Request', [('Content-Type',
            'application/json')])
        return ['400 Bad Request\r\n']
    ret = RecordList.record.pop(uri.group(1))
    if not ret:
        start_response('404 Not Found', [('Content-Type',
            'application/json')])
        return ['404 Not Found\r\n']
    start_response('200 OK', [('Content-Type', 'application/json')])
    return ['200 OK\r\n']

def run_api(env, start_response):
    request_handler = { 'GET': get_request_handler,
                        'POST': post_request_handler,
                        'PUT': put_request_handler,
                        'DELETE': delete_request_handler
                        }.get(env['REQUEST_METHOD'])
    if request_handler:
        return request_handler(env, start_response)
    else:
        start_response('405 Method Not Allowed', [('Content-Type',
            'application/json')])
        return ['405 Method Not Allowed\r\n']


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='gdeploy REST API')
    parser.add_argument('port', type=int, help='Listening port for HTTP Server')
    parser.add_argument('ip', help='HTTP Server IP')
    args = parser.parse_args()


    wsgi.server(eventlet.listen((args.ip, args.port)), run_api)
