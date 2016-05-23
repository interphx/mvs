#!/home/m/muvesol/.local/bin/python3.4
# -*- coding: utf-8 -*-
activate_this = '/home/m/muvesol/muvesol.bget.ru/env/bin/activate_this.py'
exec(compile(open(activate_this, "rb").read(), activate_this, 'exec'), dict(__file__=activate_this))

import os
import sys
import logging

#logging.basicConfig(stream=sys.stderr)

path = os.path.join(os.path.dirname(__file__), os.pardir)
if path not in sys.path:
    sys.path.append(path)

import project
from project import app as application
from project import config
from werkzeug.debug import DebuggedApplication

application.debug = True
application.wsgi_app = DebuggedApplication(application.wsgi_app, True)
