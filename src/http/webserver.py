'''
Created on Jan 9, 2014

@author: Vincent Ketelaars
'''

import BaseHTTPServer
import urlparse
from threading import Thread, Event, Lock

from src.logger import get_logger
import os
from src.conf.configuration import Configuration
from src.constants.constants import CONF_FILE, DEFAULT_PORT, DEFAULT_HOST,\
    NEWLINE
from src.content.movie_parser import MovieParser
import cgi
logger = get_logger(__name__)

class HTMLCreator(object):
    
    def __init__(self):
        pass
    
    def _element(self, tag, attr={}, text="", single=False, input=False):
        """
        @param tag: tag name
        @param attr: dictionary of attributes
        @param text: inner text value
        """
        e = "<" 
        if single:
            e += "/"
        e += tag
        for k, v in attr.iteritems():
            e += " " + k
            if v is not None:
                e += "=" + v
        e += ">"
        if not input:
            e += text + "</" + tag + ">"
        return e
    
    def td(self, text, attr={}):
        return self._element("td", attr=attr, text=text)
    
    def tr(self, text, attr={}):
        return self._element("tr", attr=attr, text=text)
    
    def input(self, attr):
        return self._element("input", attr=attr, input=True)

class WebHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    DIRECTORIES = "src/http/html"
    MAIN_PAGE = "/index.html"
    MOVIES_PAGE = "/movies.html"
    SERIES_PAGE = "/series.html"
    SET_URL = "/set"
    SAVE_MOVIES = "movie-save"
    SAVE_SERIES = "series-save"
    INVALID_RESPONSE = "This is not the page you are looking for"
    
    def __init__(self, movies_file, series_file, *args):
        self.movies_file = movies_file
        self.series_file = series_file
        self.movies = {}
        self.series = {}
        self.lock = Lock()
        self.read_files()
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args)
        
    def read_files(self):
        self.lock.acquire()
        try:
            mf = open(self.movies_file, "r")
            sf = open(self.series_file, "r")
            
            self.movies = MovieParser(None).parse(mf.read())
            self.series = MovieParser(None).parse(sf.read())
            logger.debug("Read %s and %s", self.movies_file, self.series_file)
        except:
            logger.exception("Reading of %s and %s failed", self.movies_file, self.series_file)
        finally:
            try:
                mf.close()
                sf.close()
            except:
                pass
            self.lock.release()
            
    def do_POST(self):
        
        if self.path != self.SET_URL:
            self.send_error(404)
        
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        form = {}
        if ctype == 'multipart/form-data':
            form = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            form = urlparse.parse_qs(self.rfile.read(length))
        
        logger.debug(form)
        do = form.get("do", None)
        if do is None:
            self.send_error(404)
        do = do[0]
            
        if do == self.SAVE_MOVIES:
            self.save_movies(form)
        elif do == self.SAVE_SERIES:
            self.save_series(form)
        else:
            logger.debug("Don't know what to do with %s", do)
            
    def save_movies(self, form):
        for m in self.movies.itervalues():
            v = form.get(m.id, None)
            if v is not None: # Value is only sent if checked!
                m.download = True
            else:
                m.download = False
        
        self.write_to_file(self.movies, self.movies_file)
        
    def save_series(self, series):
        pass
        
    def write_to_file(self, movies, file_):
        self.lock.acquire()
        try:
            f = open(file_, "w")
            
            sorted_movies = sorted(movies.values(), key=lambda x: x.modified, reverse=True)
            for m in sorted_movies:
                f.write(m.to_line() + NEWLINE)
        except:
            logger.exception("Could not write to file")
        finally:
            try:
                f.close()
            except:
                pass
            self.lock.release()
        
    def redirect_to_main(self):
        logger.debug("Redirect %s", self.MAIN_PAGE)
        self.send_response(301)
        self.send_header("Location", self.MAIN_PAGE)
        self.end_headers()
    
    def do_GET(self):
        logger.debug("GET %s", self.path)
        
        url_parsed = urlparse.urlparse(self.path)
        query = self._parse_query(url_parsed.query)
        logger.debug("Query %s", query)
        path = url_parsed.path
        if url_parsed.path == self.MAIN_PAGE:
            page = query.get("page", None)
            if page is not None:
                path = "/" + page + ".html"
        body, success = self.content_from_file(path)
        
        if not success:
            self.redirect_to_main()
            
        if path == self.MOVIES_PAGE:
            body = self.fill_movies(body)
        if path == self.SERIES_PAGE:
            body = self.fill_series(body)
            
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    
    def fill_movies(self, body):
        c = HTMLCreator()
        trs = ""
        movies = sorted(self.movies.values(), key=lambda x: x.modified, reverse=True)
        for m in movies:
            added = m.modified.strftime("%Y-%m-%d %H:%M:%S")
            input_attr = {"type" : 'checkbox', "name" : m.id, "value" : "1", "class" : "checkbox"}
            if m.should_download():
                input_attr["checked"] = None
            tr = c.tr(c.td(c.input(input_attr)) + c.td(m.title) + c.td(str(m.year if m.year != -1 else "????")) + c.td(added))
            trs += tr + NEWLINE
        index = body.find("</table>")
        body = body[0:index] + trs + body[index:]
        return body
        
    def fill_series(self, body):
        
        return body
    
    def content_from_file(self, path):
        f = self.get_file(path)
        logger.debug("Get file %s", f)
        body = self.INVALID_RESPONSE
        if f is not None:
            body = open(f, "r").read()
        return (body, f is not None)
        
    def get_file(self, path):
        f = os.path.join(os.path.curdir, self.DIRECTORIES, path[1:])
        
        if os.path.exists(f) and os.path.isfile(f):
            return f
        return None
    
    def _parse_query(self, query):
        """
        parse query string for arguments and values        
        @return: dictionary of arguments and values
        """
        pairs = query.split("&")
        d = {}
        for pair in pairs:
            args = pair.split("=")
            if (len(args) == 2):
                d[args[0]] = args[1]
        return d

class WebServer(Thread):
    '''
    Web server.
    '''

    def __init__(self, web_handler, movies_file, series_file, host=DEFAULT_HOST, port=DEFAULT_PORT):
        Thread.__init__(self)
        self.port = port
        
        def handler(*args):
            return WebHandler(movies_file, series_file, *args)
        
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
    cfg = Configuration(CONF_FILE)
    params = cfg.get_webgui_params()
    m, s = cfg.get_imdb_paths()
    ws = WebServer(WebHandler, m, s, params.get("host", DEFAULT_HOST), int(params.get("port", DEFAULT_PORT)))
    ws.start()
    
    try:
        raw_input("Press enter to stop\r\n")
    finally:
        ws.stop()
    
        