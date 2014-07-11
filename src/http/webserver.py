'''
Created on Jan 9, 2014

@author: Vincent Ketelaars
'''

import os
import sys
import BaseHTTPServer
import urlparse
import cgi
import json
from threading import Thread, Event, Lock

from src.conf.configuration import Configuration, get_location_from_text_file
from src.general.constants import DEFAULT_PORT, DEFAULT_HOST,\
    NEWLINE, CONF_LOCATION_FILE
from src.content.imdb_read_from_file import IMDBReadFromFile
from src.logger import get_logger
from src.torrent.handler_factory import HANDLER_LOOKUP
from src.general.functions import size_to_string
import webbrowser
import subprocess
from src.http.elementtree import to_html_string, create_tr_with_tds,\
    add_label_input_br, add_configuration_header, onclick_icon, create_input,\
    fromstring, add_break, create_div, add_form, add_div, add_input, add_select,\
    add_button, add_option
logger = get_logger(__name__)

class WebHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    DIRECTORIES = "src/http/html"
    MAIN_PAGE = "/index.html"
    MOVIES_SERIES_TEMPLATE_PAGE = "/films.html"
    MOVIES_PAGE = "/movies.html"
    SERIES_PAGE = "/series.html"
    CONFIGURATION_PAGE = "/configuration.html"
    MISSED_PAGE = "/missedtorrents.html"
    SAVE_MOVIES = "movie-save"
    SAVE_SERIES = "series-save"
    SAVE_CONFIGURATION = "conf-save"
    SAVE_CONFIGURATION_FILE = "configuration-file"
    SHOW_CONFIGURATION_FILE = "configuration-show"
    ADD_HANDLER = "add-handler"
    INVALID_RESPONSE = "This is not the page you are looking for"
    WEB_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    
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
        self.movies = IMDBReadFromFile(self.movies_file).read()
        self.series = IMDBReadFromFile(self.series_file).read()
        self.lock.release()
            
    def do_POST(self):
        # TODO: Check path as well?
                
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        form = {}
        if ctype == 'multipart/form-data':
            form = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            form = urlparse.parse_qs(self.rfile.read(length))
        
        do = form.get("do", None)
        if do is None:
            return self.send_error(404)
        do = do[0]
        
        message = "Something went wrong. Please consult the logs."
        if do == self.SAVE_MOVIES:
            if self.save_movies(form):
                message = "Saved values for movies to file!"
            else:
                message = "Could not save the changes! Please try again or report the problem."
        elif do == self.SAVE_SERIES:
            if self.save_series(form):
                message = "Saved values for series to file!"
            else:
                message = "Could not save the changes! Please try again or report the problem."
        elif do == self.SAVE_CONFIGURATION:
            if self.save_configuration(form):
                message = "Configuration has been saved!"
            else:
                message = "Could not save the changes! Please try again or report the problem."
        elif do == self.SAVE_CONFIGURATION_FILE:
            if self.edit_configuration_file_location(form):
                message = "Successfully set file location!"
            else:
                message = "Could not save the changes! Please try again or report the problem."
        elif do == self.SHOW_CONFIGURATION_FILE:
            div = self.show_configuration_file(form)
            if div is not None:
                return self.wfile.write(json.dumps({"div" : div}))
            else:
                message = "Could not show the configuration form!"
        elif do == self.ADD_HANDLER:
            div = self.add_handler(form)
            if div is not None:
                return self.wfile.write(json.dumps({"div" : div}))
            else:
                message = "Could not return appropriate html"
        else:
            logger.debug("Don't know what to do with %s", do)
        
        self.wfile.write(json.dumps({"message" : message}))
        
    def add_handler(self, form):
        handler_name = form.get("handler_list", [""])[0]
        configuration_file = form.get("configuration-file", [""])[0]
        if handler_name == "" or configuration_file == "":
            return None
        created = self._add_handler(handler_name, cfg)    
        if created is None:
            return None
        return to_html_string(created)
        
    def _add_handler(self, handler_name, cfg):
        handler = HANDLER_LOOKUP.get(handler_name, None)
        if handler is None:
            return None
        handlers = cfg.get_handlers()
        essential = None
        if handler_name in handlers[0]:
            essential = True
        elif handler_name in handlers[1]:
            essential = False
        created = handler.create_html(essential=essential, **cfg.get_handler(handler_name))
        return created
    
    def edit_configuration_file_location(self, form):
        filename = form.get("configuration-file", [""])[0] # It doesn't have to be there
        if os.path.isfile(filename):
            with self.lock:
                with open(CONF_LOCATION_FILE, "w") as f:
                    f.write(filename)
            logger.debug("New file location for the configuration file: %s", filename)
            return True
        return False
    
    def show_configuration_file(self, form):
        filename = form.get("configuration-file", [""])[0] # It doesn't have to be there
        if os.path.isfile(filename):
            div = self._fill_configuration_form(Configuration(filename)) # TODO: Make sure it's an actual configuration file
            return to_html_string(div)
        return None
    
    def _fill_configuration_form(self, cfg):
        div = create_div({"id" : "configuration-content"})
        form = add_form(div, {"method" : "POST", "id" : "save-form"})
        
        # Add torrent feeds
        torrent_feeds_div = add_div(form, {"id" : "torrent-feeds"})
        add_configuration_header(torrent_feeds_div, "Torrent Feeds", "List the RSS feeds that you would like to monitor")
        for f in cfg.get_torrent_rss_feeds():
            onclick_icon(torrent_feeds_div, False, "return remove_input_element(this)")
            add_input(torrent_feeds_div, {"type" : "text", "size" : "50", "name" : "feed", "value" : str(f)})
            add_break(torrent_feeds_div)
        onclick_icon(torrent_feeds_div, True, "return add_input_element(this, '', 'feed')")
        
        # Add IMDB feeds
        imdb_feeds_div = add_div(form, {"id" : "imdb-feeds"})
        add_configuration_header(imdb_feeds_div, "IMDB Feeds", "List the IMDB watchlists that you would like to monitor")
        for f in cfg.get_imdb_csv_urls():
            onclick_icon(imdb_feeds_div, False, "return remove_imdb_input(this)")
            add_break(imdb_feeds_div)
            add_label_input_br(imdb_feeds_div, "URL", 50, "url", f.url)
            add_label_input_br(imdb_feeds_div, "Username", 30, "user", f.username)
            add_label_input_br(imdb_feeds_div, "Password", 30, "pass", f.password)
        onclick_icon(imdb_feeds_div, True, "return add_imdb_input(this)")
        
        # Set information storage parameters
        info_storage_div = add_div(form, {"id" : "info-storage"})
        file_paths = cfg.get_imdb_paths()
        add_configuration_header(info_storage_div, "Information Storage", "Determine where the movies and series information will be stored")
        add_label_input_br(info_storage_div, "Movies file", 50, "movies_file", file_paths[0])
        add_label_input_br(info_storage_div, "Series file", 50, "series_file", file_paths[1])
        add_label_input_br(info_storage_div, "Missed torrents file", 50, "missed_file", file_paths[2])
        
        # Add active feeds
        active_feed_div = add_div(form, {"id" : "active-feeds"})
        asp = cfg.get_active_feeds()
        add_configuration_header(active_feed_div, "Active feeds", "List feeds that can be used for active searches. Also limit the number of these searches for movies and series.")
        add_label_input_br(active_feed_div, "Maximum movies", 10, "max_movies", asp.max_movies)
        add_label_input_br(active_feed_div, "Maximum series", 10, "max_series", asp.max_series)
        for u in asp.urls:
            onclick_icon(active_feed_div, False, "return remove_input_element(this)")
            add_label_input_br(active_feed_div, "Search url", 100, "active_url", u)
        onclick_icon(active_feed_div, True, "return add_input_element(this, 'Search url', 'active_url')")
        
        # Add preferences
        preferences_div = add_div(form, {"id" : "preferences"})
        add_configuration_header(preferences_div, "Preferences", "List your preferences here")
        preference = cfg.get_torrent_preference()
        add_label_input_br(preferences_div, "Not in Title", 50, "title_not", ", ".join(preference.not_list), explanation="Comma separated list of keywords that you do not want in the torrent's title")
        add_label_input_br(preferences_div, "Allowed in Title", 50, "title_allowed", ", ".join(preference.allowed_list), explanation="Comma separated list of keywords that you allow the torrent title to be obfuscated with")
        add_label_input_br(preferences_div, "Preferred in Title", 50, "title_pref", ", ".join(preference.pref_list), explanation="Comma separated list of keywords that indicate preference in torrent's title")
        add_label_input_br(preferences_div, "Not in Description", 50, "not_in_desc", ", ".join(preference.not_in_desc), explanation="Comma separated list of keywords that you do not want in the torrent's description")
        add_label_input_br(preferences_div, "Minimum width", 10, "min_width", preference.min_width, explanation="Minimum width for the movie's resolution (pixels)")
        add_label_input_br(preferences_div, "Minimum height", 10, "min_height", preference.min_height, explanation="Minimum height for the movie's resolution (pixels)")
        add_label_input_br(preferences_div, "Minimum movie size", 10, "min_movie_size", size_to_string(preference.min_movie_size), explanation="Minimum size of the movie (e.g. 700MB or 2GB)")
        add_label_input_br(preferences_div, "Maximum movie size", 10, "max_movie_size", size_to_string(preference.max_movie_size), explanation="Maximum size of the movie (e.g. 5GB)")
        add_label_input_br(preferences_div, "Minimum series size", 10, "min_series_size", size_to_string(preference.min_series_size), explanation="Minimum size of the series (e.g. 100MB)")
        add_label_input_br(preferences_div, "Maximum series size", 10, "max_series_size", size_to_string(preference.max_series_size), explanation="Maximum size of the series (e.g. 5GB)")
        add_label_input_br(preferences_div, "Languages", 50, "languages", ", ".join(preference.languages), explanation="Comma separated list of languages (or acronyms) allowed to be spoken")
        add_label_input_br(preferences_div, "Subtitles", 50, "subtitles", ", ".join(preference.subtitles), explanation="Comma separated list of languages that are preferred for subtitles")
        add_label_input_br(preferences_div, "Excluded extensions", 50, "excluded_extensions", ", ".join(preference.excluded_extensions), explanation="Comma separated list of extensions that are not allowed")
        
        # Add handlers
        handler_div = add_div(form, {"id" : "handlers"})
        add_configuration_header(handler_div,  "Handlers", "List your handlers here. Note that you can use only one of each. Additionally denote it primary or secondary. If you choose neither it will be stored but not used.")
        selector = add_select(handler_div, {"id" : "handler_selector", "name" : "handler_list"})
        add_option(selector, {"value" : "default", "selected" : "selected"})
        add_handler_button = add_button(handler_div, {"type" : "submit", "id" : "handler_adder", 
                                                                          "name" : "do", "value" : "add-handler"})
        add_handler_button.text = "Add"
        for h, v in HANDLER_LOOKUP.iteritems():
            o = add_option(selector, {"value" : h})
            o.text = v.NAME
            handler = self._add_handler(h, cfg)
            if handler is not None:
                handler_div.append(handler)
        
        # WebGUI settings
        gui_div = add_div(form, {"id" : "webgui"})
        add_configuration_header(gui_div,  "WebGUI", "Set the WebGUI parameters. They will take effect the next time you start.")
        webgui = cfg.get_webgui_params()
        add_label_input_br(gui_div, "Host", 50, "host", webgui.get("host", ""))
        add_label_input_br(gui_div, "Port", 10, "port", webgui.get("port", ""))
        
        conf_save_button = add_button(div, {"type" : "submit", "class" : "save-button", 
                                                                          "name" : "do", "value" : "conf-save"})
        conf_save_button.text = "Save"
        return div
            
    def save_movies(self, form):
        for m in self.movies.itervalues():
            v = form.get(m.id, None)
            if v is not None: # Value is only sent if checked!
                m.download = True
            else:
                m.download = False
        
        return self.write_to_file(self.movies, self.movies_file)
        
    def save_series(self, form):
        def to_int(s):
            try:
                return int(s)
            except ValueError:
                logger.debug("Could not cast %s to int", s)
                return 0
        
        for ser in self.series.itervalues():
            if form.get(ser.id, None) is not None:
                ser.download = True
            else:
                ser.download = False
            ser.latest_season = to_int(form.get(ser.id + "_season", [0])[0])
            ser.latest_episode = to_int(form.get(ser.id + "_episode", [0])[0])
            
        return self.write_to_file(self.series, self.series_file)
    
    def save_configuration(self, form):
        configuration_file = form.get("configuration-file", [""])[0]
        if configuration_file == "" or not os.path.isfile(configuration_file):
            return False
        cfg = Configuration(configuration_file)
        i = 0
        for f in form.get("feed", []):
            cfg.set_option("torrents", "feed" + str(i), f)
            i += 1
        i = 0
        for url, user, password in zip(form.get("url", []), form.get("user", []), form.get("pass", [])):
            cfg.set_option("imdb", "url" + str(i), url)
            cfg.set_option("imdb", "user" + str(i), user)
            cfg.set_option("imdb", "pass" + str(i), password)
            i += 1
        self._save_configuration(cfg, "storage", ["movies_file", "series_file"], form)
        self._save_configuration(cfg, "active", ["max_movies", "max_series"], form)
        i = 0
        for au in form.get("active_url", []):
            cfg.set_option("active", "active_url" + str(i), au)
            i += 1
        self._save_configuration(cfg, "match", ["title_not", "title_allowed", "title_pref", "not_in_desc", "min_width", 
                                           "min_height", "min_movie_size", "max_movie_size", "min_series_size", "max_series_size",
                                           "languages", "subtitles", "excluded_extensions"], form)
        self._save_configuration(cfg, "webgui", ["host", "port"], form)
        cfg.set_option("handlers", "primary", "")
        cfg.set_option("handlers", "secondary", "")
        for h, c in HANDLER_LOOKUP.iteritems():
            if c.NAME + "-importance" in form.keys() and not form.get(c.NAME + "-importance", [None])[0] == "inactive":
                cfg.add_to_list("handlers", form.get(c.NAME + "-importance", [None])[0], h)
                self._save_configuration(cfg, "handler_" + h, c.PARAMETERS, form)
        return cfg.write()           
        
    def _save_configuration(self, cfg, section, options, form):
        for o in options:
            cfg.set_option(section, o, form.get(o, [None])[0])
        
    def write_to_file(self, movies, file_):
        self.lock.acquire()
        sorted_movies = sorted(movies.values(), key=lambda x: x.modified, reverse=True)
        text = ""
        for m in sorted_movies:
            text += m.to_line() + NEWLINE
        success = False
        tmp = file_ + ".tmp"
        try:
            with open(tmp, "w") as f:            
                f.write(text)
                f.flush()
        except EnvironmentError:
            logger.exception("Could not write to %s", file_)
        else:
            os.rename(tmp, file_)
            success = True
        self.lock.release()
        return success
        
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
                
        if path == self.MOVIES_PAGE:
            body, success = self.content_from_file(self.MOVIES_SERIES_TEMPLATE_PAGE)
            body = self.fill_movies(body)
        elif path == self.SERIES_PAGE:
            body, success = self.content_from_file(self.MOVIES_SERIES_TEMPLATE_PAGE)
            body = self.fill_series(body)
        elif path == self.CONFIGURATION_PAGE:
            body, success = self.content_from_file(path)
            body = self.fill_configuration(body)
        elif path == self.MISSED_PAGE:
            body, success = self.content_from_file(path)
            body = self.fill_missed(body)
        else:
            body, success = self.content_from_file(path)
        
        if not success:
            self.redirect_to_main()
            
        _, extension =  os.path.splitext(path)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        if extension == ".css":
            self.send_header("Content-type", "text/css")
        elif extension == ".js":
            self.send_header("Content-type", "text/javascript")
        elif any([extension == end for end in [".jpg", ".jpeg", ".png"]]):
            self.send_header("Content-type", "image/" + extension[1:])
        self.send_header("Content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    
    def fill_movies(self, body):
        explanation = "The selected movies will be downloaded"
        trs = [create_tr_with_tds(create_input({"type" : "checkbox", "id" : "check-all", "text" : "Download"}), "Movie", "Year", "Added")]
        movies = sorted(self.movies.values(), key=lambda x: x.modified, reverse=True)
        for m in movies:
            added = m.modified.strftime(self.WEB_DATETIME_FORMAT)
            input_attr = {"type" : 'checkbox', "name" : m.id, "value" : "1", "class" : "checkbox"}
            if m.download:
                input_attr["checked"] = "checked"
            tr = create_tr_with_tds(create_input(input_attr), m.title.decode("utf-8", "ignore"), str(m.year if m.year != -1 else "????"), added)
            trs.append(tr)
        return self.fill_films(body, "Movies", "movie", explanation, trs)
        
    def fill_series(self, body):        
        explanation = "Episodes will be downloaded if they are later than the episode indicated in on this sheet"
        trs = [create_tr_with_tds("Download", "Season", "Episode", "Series", "Year", "Added","Last download")]
        series = sorted(self.series.values(), key=lambda x: x.modified, reverse=True)
        for s in series:
            added = s.modified.strftime(self.WEB_DATETIME_FORMAT)
            downloaded = s.time_downloaded.strftime(self.WEB_DATETIME_FORMAT)
            input_attr = {"type" : 'checkbox', "name" : s.id, "value" : "1", "class" : "checkbox"}
            if s.download:
                input_attr["checked"] = "checked"
            season_attr = {"type" : 'text', "size" : "2", "name" : s.id + "_season", "value" : str(s.latest_season)}
            episode_attr = {"type" : 'text', "size" : "2", "name" : s.id + "_episode", "value" : str(s.latest_episode)}
            tr = create_tr_with_tds(create_input(input_attr), create_input(season_attr), create_input(episode_attr), 
                                    s.title, str(s.year if s.year != -1 else "????"), added, downloaded)
            trs.append(tr)
        return self.fill_films(body, "Series", "series", explanation, trs)
    
    def fill_films(self, body_string, Films, film, explanation, trs):
        root = fromstring(body_string)
        head = root.find("head")
        head.find("title").text = Films
        body = root.find("body")
        body.find("h2").text = Films
        body.find("p").text = explanation
        for button in body.find("form").findall("button"):
            button.set("value", button.get("value").replace("film", film))
        body.find("form").find("table").extend(trs)
        return to_html_string(root)
    
    def fill_configuration(self, body, configuration_file=None):
        if configuration_file is None:
            with self.lock:
                configuration_file = get_location_from_text_file(CONF_LOCATION_FILE)
        if configuration_file is None:
            return body
        cfg = Configuration(configuration_file)
        root = fromstring(body)
        html_body = root.find("body")
        file_form = html_body.find("form")
        input_file = file_form.find("input")
        # Set input file
        input_file.set("value", configuration_file)
        conf_form_div = self._fill_configuration_form(cfg)
        conf_content = html_body.find("div")
        html_body.remove(conf_content)
        html_body.append(conf_form_div)
        return to_html_string(root)
    
    def fill_missed(self, body):
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
    cfg = Configuration(get_location_from_text_file(CONF_LOCATION_FILE))
    params = cfg.get_webgui_params()
    m, s, _ = cfg.get_imdb_paths()
    ws = WebServer(WebHandler, m, s, params.get("host", DEFAULT_HOST), int(params.get("port", DEFAULT_PORT)))
    ws.start()

    if len(sys.argv) > 1: # supplied with browser
        browser = sys.argv[1]
        url = "http://%s:%d%s" % (params.get("host", DEFAULT_HOST), int(params.get("port", DEFAULT_PORT)), WebHandler.MAIN_PAGE)
        if browser == "chromium":
            subprocess.call(["chromium-browser", url])
        elif browser == "firefox":
            subprocess.call(["firefox", url])
        else:
            webbrowser.open(url, new=2)
    
    try:
        raw_input("Press enter to stop\r\n")
    finally:
        ws.stop()
    
        