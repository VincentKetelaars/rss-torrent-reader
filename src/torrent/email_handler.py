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

    def __init__(self, matches, email_to=None, email_from=None, smtp_host=None, smtp_port=None, username=None, password=None):
        MatchHandler.__init__(self, matches, name="EmailHandler")
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
            txt += m.torrent.url() + " \n"
        msg = MIMEText(txt)
        
        msg['Subject'] = 'Torrent URLs'
        msg['From'] = self.email_from
        msg['To'] = ", ".join(self.email_to)
        
        logger.info("Sending %d torrents from %s to %s", len(matches), self.email_from, self.email_to)
        
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
            smtp.quit()
        return matches        
        