#!/usr/bin/python 

'''
Push tam_usage_max to Meter widget on dashing server
'''

import os
import sys
import json
import time
import argparse
import urllib2
import httplib

parser = argparse.ArgumentParser(
                    description = 'Retrieve and push Sabre TAM usage '
                    'max to Dashing server for display')
parser.add_argument('-d', help ='Dashing server to push data to', 
                    required = False, dest = 'dashing_host', 
                    default = 'dashing.virginam.com')
parser.add_argument('-w', help ='Widget to send data to',
                    required = False, dest = 'widget', 
                    default = 'tam_usage_max')
parser.add_argument('-a', help = 'Authentication token '
                    'used by Dashing server',
                    required = False, dest = 'authtoken', 
                    default = "mingle#trip")
parser.add_argument('-f', help ='Name of file to read stats from', 
                    required = False, dest = 'historyfile', 
                    default = "api_tam_stats.history")
parser.add_argument('--version', help = 'Print version and exit', 
                    required = False, action = 'store_true')

__version__          = '0.0.1'
__author__           = 'Pete Cornell'

args                 = parser.parse_args()
auth_token           = args.authtoken
dashing_host         = args.dashing_host.strip('http://')
target_widget        = args.widget
DATA_VIEW            = "points"
historyfile          = args.historyfile
echo_version         = args.version
dashing_http_port    = "80"
server_connection    =  ( dashing_host + ':' + dashing_http_port + 
                        '/widgets/' + target_widget )


def tam_session_max(file):
    with open(file) as f:
        values = []
        for line in f:
            if line.strip():
                line = int(line)
                values.append(line)

        return max(values)


def transmit_values(stat_values, target_widget):
    '''Send data to Dashing server via http.'''
    pass


def main():

    if echo_version:
        print "%s version: %s " % (sys.argv[0].strip('./'), __version__)
        exit(0)

    ##
    print "\nUsing options:", args
    ##

    ##
    ## Call functions
    ##
    
    max_value = tam_session_max(historyfile)
    print "max reading", max_value
    exit(0)
    transmit_values(max_value, target_widget)

    # time to push to dashing


if __name__ == '__main__':
    main()
