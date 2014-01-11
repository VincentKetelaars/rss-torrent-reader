'''
Created on Jan 9, 2014

@author: Vincent Ketelaars
'''

import BaseHTTPServer
import urlparse
from threading import Thread, Event

from src.logger import get_logger
import os
from src.conf.configuration import Configuration
logger = get_logger(__name__)

class WebHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    DIRECTORIES = "src/http/html"
    MAIN_PAGE = "/index.html"
    MOVIES_PAGE = "/movies.html"
    SERIES_PAGE = "/series.html"
    INVALID_RESPONSE = "This is not the page you are looking for"
        
    def do_HEAD(self):
        if not self.path.startswith(self.MAIN_PAGE):
            logger.debug("Redirect %s", self.MAIN_PAGE)
            self.send_response(301)
            self.send_header("Location", self.MAIN_PAGE)
            self.end_headers()
    
    def do_GET(self):
        logger.debug("GET %s", self.path)
        self.do_HEAD()
        
        url_parsed = urlparse.urlparse(self.path)
        body = self.INVALID_RESPONSE
        if self.path == self.MAIN_PAGE:
            body = self.create_main()
        elif url_parsed.query == "page=Movies":
            body = self.create_movies()
        elif url_parsed.query == "page=Series":
            body = self.create_series()
            
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        
    def create_main(self):
        body, _ = self.content_from_file(self.MAIN_PAGE)
        return body
    
    def create_movies(self):
        body, _ = self.content_from_file(self.MOVIES_PAGE)
        return body
        
    def create_series(self):
        body, _ = self.content_from_file(self.SERIES_PAGE)
        return body
    
    def content_from_file(self, path):
        f = self.get_file(path)
        body = self.INVALID_RESPONSE
        if f is not None:
            body = open(f, "r").read()
        return (body, f is not None)
        
    def get_file(self, path):        
        f = os.path.join(os.path.curdir, self.DIRECTORIES, path[1:])
        
        if os.path.exists(f):
            return f
        return None

class WebServer(Thread):
    '''
    classdocs
    '''

    def __init__(self, handler, host="127.0.0.1", port=8080):
        Thread.__init__(self)
        self.port = port
        self.server = BaseHTTPServer.HTTPServer((host, port), handler)
        self.stop_event = Event()
        
    def run(self):
        self.server.timeout = 1.0
        while not self.stop_event.is_set():
            try:
                self.server.handle_request() # Use serve_forever() or handle_request()
            except:
                pass
        self.server.socket.close()
        
    def stop(self):
        logger.debug("Stopping")
        self.stop_event.set()
        
if __name__ == "__main__":
    cfg = Configuration("conf/configuration.cfg")
    params = cfg.get_webgui_params()
    ws = WebServer(WebHandler, params.get("host"), int(params.get("port")))
    ws.start()
    
    try:
        raw_input("Press enter to stop\r\n")
    finally:
        ws.stop()
    
        