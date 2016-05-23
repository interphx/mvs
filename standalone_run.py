#! python3.4
# -*- coding: utf-8 -*-
import json
from project import app, config

# Startup
if __name__ == '__main__':
    app.run(
        debug = config['app']['debug'],
        host = config['flask']['HOST'],
        port = config['flask']['PORT']
    )