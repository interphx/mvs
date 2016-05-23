import os
import os.path
import glob
from project.util import getImmediateSubdirectories

MODULES_DIR = os.path.join(os.path.dirname(__file__), 'modules')

modules = getImmediateSubdirectories(MODULES_DIR)
for module in modules:
    if module.startswith('_'): continue
    if not os.path.isfile(os.path.join(MODULES_DIR, module, '__init__.py')):
        print('Missing __init__.py in module {}'.format(module))
        continue
    __import__('project.modules.' + module, globals())