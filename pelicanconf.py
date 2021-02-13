#!/usr/bin/env python3

SITENAME = 'Notonlyowner'
SITEURL = 'https://notonlyowner.com'

# Path to content directory to be processed by Pelican
PATH = 'content'

# A list of directories and files to look at for pages, relative to `PATH`
PAGE_PATHS = ['pages']

RELATIVE_URLS = True

THEME = 'theme'

DEFAULT_LANG = 'en'
LOCALE = 'en_US'

CATEGORY_SAVE_AS = False

DIRECT_TEMPLATES = ['index']

USE_FOLDER_AS_CATEGORY = True
CATEGORY_URL = '{slug}.html'
CATEGORY_SAVE_AS = '{slug}.html'

AUTHOR_SAVE_AS = False
TAG_SAVE_AS = False
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

ARTICLE_URL = '{category}/{slug}/'
ARTICLE_SAVE_AS = '{category}/{slug}/index.html'
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.toc': {},
    },
    'output_format': 'html5'
}

STATIC_PATHS = [
    'extra/robots.txt',
    'extra/favicon.ico'
]

IGNORE_FILES = ['.track']

EXTRA_PATH_METADATA = {
    'extra/robots.txt': {'path': 'robots.txt'},
    'extra/favicon.ico': {'path': 'favicon.ico'}
}

PLUGINS = ['pelican_webassets']
