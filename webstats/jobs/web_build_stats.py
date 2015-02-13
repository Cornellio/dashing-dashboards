#!/usr/bin/python

'''
Dashing job for listing website build stamps, including
UI, API and CMS build numbers.
'''

import urllib
import httplib
import re
import argparse

__version__ = '1.0.0'
__author__  = 'Pete Cornell'


def return_args():
    '''Parse command line args'''

    parser = argparse.ArgumentParser(
        description='Retrieve website build stamps and send to Dashing '
        'server for display')
    parser.add_argument('-d', help='Dashing server to push data to',
                        required=False, dest='dashing_host',
                        default='dashing.virginam.com')
    parser.add_argument('-p', help='Port - defaults to 80',
                        required=False, default='80', dest='dashing_port')
    parser.add_argument('-w', help='Widget to send data to',
                        required=True, dest='widget')
    parser.add_argument('-a', help='Authentication token '
                        'used by Dashing server',
                        required=True, dest='authtoken')

    args          = parser.parse_args()
    auth_token    = args.authtoken
    dashing_host  = args.dashing_host.strip('http://')
    dashing_port  = args.dashing_port
    target_widget = args.widget
    DATA_VIEW     = "points"

    return (auth_token,
            dashing_host,
            dashing_port,
            target_widget,
            DATA_VIEW)


def get_ui_build():
    '''Return UI Build'''

    site = 'https://www.virginamerica.com/status'
    url = urllib.urlopen(site)
    page_source = url.read()
    ui_build = re.findall('\w+-build-\d\d\d', page_source)
    return ''.join(ui_build)


def get_api_build():
    '''Return API Build'''

    site = 'https://www.virginamerica.com/api/v0/release/build-stamp'
    url = urllib.urlopen(site)
    page_source = url.read()
    api_build = re.findall('\d+', page_source)
    return ''.join(api_build)


def get_cms_build():
    '''Return CMS Build'''

    site = 'https://www.virginamerica.com/cms/version.json'
    url = urllib.urlopen(site)
    page_source = url.read()
    cms_build = re.findall('\d+\.\d+\.\d+', page_source)
    return ''.join(cms_build)


def transmit_values(host, port, widget, token, ui_build, api_build, cms_build):
    '''Construct string for list item widget and send to Dashing server'''

    items = ('{"label": "UI Build", "value": "'
             + ui_build + '"}, {"label": "CMS Build", "value": "'
             + cms_build + '"}, {"label": "API Build", "value": "'
             + api_build + '"}')

    post_data = '{ "auth_token": "' + token + '", "items": [ ' + items + '] }'

    http = httplib.HTTPConnection(host, port)
    http.request('POST', '/widgets/' + widget, post_data)

    response = http.getresponse()
    print response.read()

    return None


def main():

    (auth_token,
        dashing_host,
        dashing_port,
        target_widget,
        DATA_VIEW) = return_args()

    transmit_values(dashing_host,
                    dashing_port,
                    target_widget,
                    auth_token,
                    get_ui_build(),
                    get_api_build(),
                    get_cms_build())

if __name__ == '__main__':
    main()
