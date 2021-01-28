#  coding: utf-8 
import socketserver
import json
import zlib

import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

class MyWebServer(socketserver.BaseRequestHandler):

    def not_accessable(self, file_path):
        print('file path abspath: %s' % os.path.abspath(file_path))
        print('www path abspath: %s' % os.path.abspath('./www'))
        print('within www?: %s\n' % os.path.abspath(file_path).startswith(os.path.abspath('./www')))

        return not os.path.abspath(file_path).startswith(os.path.abspath('./www'))
    
    def html_response(self, response):
        return (
            '<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">'
            '<TITLE>%s</TITLE></HEAD><BODY>'
            '<H1>%s</H1>'
            '</BODY></HTML>' % (response, response)
        )

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print('Got a request of: %s\n' % self.data)

        data = self.data.decode('utf-8')

        if len(data) > 0:
            # Get info from request
            request = data.split('\r\n')[0].split()
            method = request[0]
            requested_path = request[1]

            root_dirs = ['/', '/deep/']
            if requested_path in root_dirs:
                requested_path += 'index.html'
            else:
                requested_path.rstrip('//')
            print('request_path', requested_path)

            file_path = './www%s' % requested_path

            # wrong method
            if (method not in ['GET']):
                header = 'HTTP/1.1 405 Method not allowed\r\n\r\n'
                response = header + self.html_response('405 Method not allowed')
                self.request.sendall(bytearray(response, 'utf-8'))
                return

            # not within /www
            if(self.not_accessable(file_path)):
                header = 'HTTP/1.1 404 Not Found\r\n\r\n'
                response = header + self.html_response('404 Not Found')
                self.request.sendall(bytearray(response, 'utf-8'))
                return
            
            # within /www and file DNE 
            if(not os.path.exists(file_path)):
                header = 'HTTP/1.1 404 Not Found\r\n\r\n'
                response = header + self.html_response('404 Not Found')
                self.request.sendall(bytearray(response, 'utf-8'))
                return

            # within /www and file/dir exists
            if(requested_path == '/deep'):
                header = (
                    'HTTP/1.1 301 Moved Permanently\n'
                    'Location: http://127.0.0.1:8080/deep/\r\n\r\n'
                )
                response = header + self.html_response('301 Moved Permanently')
                self.request.sendall(bytearray(response, 'utf-8'))
            else:
                # refer to this page for mimetypes: 
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
                header = 'HTTP/1.1 200 OK\r\n'
                mimetype = 'text/html'
                if (requested_path.endswith('.css')):
                    mimetype = 'text/css'
                header += 'Content-Type: %s\r\n\r\n' % mimetype

                try:
                    self.request.sendall(bytearray(header, 'utf-8'))
                    
                    # read file as bytes
                    # Stolen from Jeremy: https://stackoverflow.com/users/1114/jeremy
                    # From https://stackoverflow.com/a/6787259
                    file = open(file_path, 'rb')
                    lines = file.read()
                    file.close()
                    self.request.sendall(lines)
                except:
                    header = 'HTTP/1.1 500 Internal Server Error\r\n\r\n'
                    response = header + self.html_response('500 Internal Server Error')
                    self.request.sendall(bytearray(response, 'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
