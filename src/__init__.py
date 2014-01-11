import logging.config
import sys
from traceback import print_exception

fileconf = "logging.conf"
try:
    logging.config.fileConfig(fileconf)
except:
    print "Could not use %s for configuration because:" % (fileconf,)
    print_exception(*sys.exc_info())