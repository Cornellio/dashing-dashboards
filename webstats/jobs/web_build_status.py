#!/bin/python

import urllib
import re
from commands import *


def get_ui_build():

    site = 'https://www.virginamerica.com/status'
    url = urllib.urlopen(site)
    page_source = url.read()
    ui_build = re.findall('\w+-build-\d\d\d', page_source)
    return ui_build


def get_api_build():

    site = 'https://www.virginamerica.com/api/v0/release/build-stamp'
    url = urllib.urlopen(site)
    page_source = url.read()
    api_build = re.findall('\d+', page_source)
    return api_build


def get_cms_build():

    site = 'https://www.virginamerica.com/cms/version.json'
    url = urllib.urlopen(site)
    page_source = url.read()
    cms_build = re.findall('\d+\.\d+\.\d+', page_source)
    return cms_build


def main():

    ui_build = get_ui_build()
    print ''.join(ui_build)

    api_build = get_api_build()
    print ''.join(api_build)

    cms_build = get_cms_build()
    print ''.join(cms_build)


if __name__ == '__main__':
    main()
