#! /usr/lib/python3/


import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/ubuntu/Item-Catalog/')
from spelllist import app as application
application.secret_key = '...'

