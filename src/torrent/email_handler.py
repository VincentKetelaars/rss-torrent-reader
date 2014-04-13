'''
Created on Feb 3, 2014

@author: Vincent Ketelaars
'''
import smtplib
from email.mime.text import MIMEText

from src.torrent.match_handler import MatchHandler
from src.logger import get_logger
logger = get_logger(__name__)

SMTP_TIMEOUT = 10.0 # Seconds

class EmailHandler(MatchHandler):
    '''
    This class will notify by email
    '''
    
    NAME = "Email"
    PARAMETERS = ["email_to", "email_from", "smtp_host", "smtp_port", "username", "password"]

    def __init__(self, matches, email_to=None, email_from=None, smtp_host=None, smtp_port=None, username=None, password=None, **kwargs):
        MatchHandler.__init__(self, matches, name=EmailHandler.NAME, **kwargs)
        if isinstance(email_to, list):
            self.email_to = email_to
        elif isinstance(email_to, str):
            self.email_to = [email_to]
        else:
            self.email_to = None
        self.email_from = email_from
        self.host = smtp_host
        self.port = smtp_port if smtp_port is not None else smtplib.SMTP_PORT
        self.username = username
        self.password = password
        
    def handle_matches(self, matches):
        if len(matches) == 0 or self.email_from is None or not self.email_to or self.host is None:
            return []
        
        txt = "These are the torrents that correspond to movies or series in your IMDB Watchlist\n"
        for m in matches:
            txt += self._email_content(m) + " \n"
        msg = MIMEText(txt)
        
        msg['Subject'] = 'Torrent URLs'
        msg['From'] = self.email_from
        msg['To'] = ", ".join(self.email_to)
        
        logger.info("Sending %d torrents from %s to %s with %s and port %d", len(matches), self.email_from, self.email_to, self.host, self.port)
        
        try:
            smtp = smtplib.SMTP(host=self.host, port=self.port, timeout=SMTP_TIMEOUT)
            if self.username is not None:
                smtp.ehlo() # for tls add this line
                smtp.starttls() # for tls add this line
                smtp.ehlo() # for tls add this line
                smtp.login(self.username, self.password)
            smtp.sendmail(self.email_from, self.email_to, msg.as_string())
        except: # So many possible exceptions..
            logger.exception("Failed to send email to %s", self.email_to)
            return []
        finally:
            try:
                smtp.quit()
            except:
                pass
        return matches
    
    def _email_content(self, match):
        text = "Title: %s%s\nIMDB url: %s\nTorrent title: %s\nTorrent url: %s\n" % \
        (match.movie.title, (" S%02dE%02d" % match.torrent.episode() if match.movie.is_series() else ""), 
         match.movie.url, match.torrent.title, match.torrent.url())
        return text
    
    @staticmethod
    def create_html(email_to="", email_from="", smtp_host="", smtp_port=0, username="", password="", **kwargs):
        div = MatchHandler.create_html(name=EmailHandler.NAME, class_name="email_handler", **kwargs)        
        MatchHandler.add_label_input_br(div, "Email to", 50, "email_to", email_to)
        MatchHandler.add_label_input_br(div, "Email from", 50, "email_from", email_from)
        MatchHandler.add_label_input_br(div, "SMTP Host", 50, "smtp_host", smtp_host)
        MatchHandler.add_label_input_br(div, "SMTP Port", 50, "smtp_port", smtp_port)
        MatchHandler.add_label_input_br(div, "Username", 50, "username", username)
        MatchHandler.add_label_input_br(div, "Password", 50, "password", password)
        return div
        