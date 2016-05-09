#!/usr/bin/env python3

import pystache
import os
from os.path import join, basename
import json


SITE_PATH = os.path.dirname(os.path.realpath(__file__))

NEWS_FILE       = join(SITE_PATH, 'data', 'news.json')
PAPERS_FILE     = join(SITE_PATH, 'data', 'papers.json')
TOOLS_FILE      = join(SITE_PATH, 'data', 'tools.json')
BENCHMARKS_FILE = join(SITE_PATH, 'data', 'benchmarks.json')
ANALYTICS_FILE  = join(SITE_PATH, 'analytics.txt')
META_FILE       = join(SITE_PATH, 'meta.txt')

HOME_TEMPLATE         = join(SITE_PATH, 'templates', 'index.html')
BIBLIOGRAPHY_TEMPLATE = join(SITE_PATH, 'templates', 'bibliography.html')
TOOLS_TEMPLATE        = join(SITE_PATH, 'templates', 'tools.html')
BENCHMARKS_TEMPLATE   = join(SITE_PATH, 'templates', 'benchmarks.html')

HOME_OUTPUT         = join(SITE_PATH, 'index.html')
BIBLIOGRAPHY_OUTPUT = join(SITE_PATH, 'bibliography.html')
TOOLS_OUTPUT        = join(SITE_PATH, 'tools.html')
BENCHMARKS_OUTPUT   = join(SITE_PATH, 'benchmarks.html')

print('Rendering {}'.format(basename(HOME_OUTPUT)))

with open(HOME_TEMPLATE, 'r') as file:
    home_template = file.read()
with open(NEWS_FILE, 'r') as file:
    home_data = json.load(file)
with open(META_FILE, 'r') as file:
    home_data['meta'] = file.read()
with open(ANALYTICS_FILE, 'r') as file:
    home_data['analytics'] = file.read()
with open(HOME_OUTPUT, 'w') as file:
    file.write(pystache.render(home_template, home_data))

print('Rendering {}'.format(basename(BIBLIOGRAPHY_OUTPUT)))

with open(BIBLIOGRAPHY_TEMPLATE, 'r') as file:
    bibliography_template = file.read()
with open(PAPERS_FILE, 'r') as file:
    papers_data = json.load(file)
with open(BIBLIOGRAPHY_OUTPUT, 'w') as file:
    file.write(pystache.render(bibliography_template, papers_data))

print('Rendering {}'.format(basename(TOOLS_OUTPUT)))

with open(TOOLS_TEMPLATE, 'r') as file:
    tools_template = file.read()
with open(TOOLS_FILE, 'r') as file:
    tools_data = json.load(file)
with open(TOOLS_OUTPUT, 'w') as file:
    file.write(pystache.render(tools_template, tools_data))

print('Rendering {}'.format(basename(BENCHMARKS_OUTPUT)))

with open(BENCHMARKS_TEMPLATE, 'r') as file:
    benchmarks_template = file.read()
with open(BENCHMARKS_FILE, 'r') as file:
    benchmarks_data = json.load(file)
with open(BENCHMARKS_OUTPUT, 'w') as file:
    file.write(pystache.render(benchmarks_template, benchmarks_data))


print('DONE')
