import os
import logging

APP_ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
# If we're debugging, turn the cache off, etc.
# Set to true if we want to have our webapp print stack traces, etc
DEBUG = os.environ['SERVER_SOFTWARE'].startswith('Dev')
logging.info("Starting application in DEBUG mode: %s", DEBUG)

DICT = {
    "dict_version": "0.1",
    "html_type": "text/html",
    "charset": "utf-8",
    "title": "Investcpedia",
    "author": "Ping Chen",
    # This must be the email address of a registered administrator for the
    # application due to mail api restrictions.
    "email": "cpedia@gmail.com",
    "root_url": "http://invest.cpedia.com",
    "master_atom_url": "/feeds/atom.xml",
    # You can override this default for each page through a handler's call to
    #  view.ViewPage(cache_time=...)
    "cache_time": 0 if DEBUG else 3600,
}
