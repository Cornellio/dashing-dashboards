#!/usr/bin/python 

'''
Lookup current TAM pool usage from Sabre.
Save results to file at 5 minute intervals.
Push stats to dashing.

TODO: refactor from bash script
'''

import os
import sys
import json
import time
import argparse
import urllib2
import httplib

parser = argparse.ArgumentParser(
                    description = 'Retrieve and process Sabre TAM usage '
                    'and send to Dashing server for display')
parser.add_argument('-d', help ='Dashing server to push data to', 
                    required = False, dest = 'dashing_host', 
                    default = 'dashing.virginam.com')
parser.add_argument('-w', help ='Widget to send data to',
                    required = False, dest = 'widget', 
                    default = 'sabresessions')
parser.add_argument('-a', help = 'Authentication token '
                    'used by Dashing server',
                    required = False, dest = 'authtoken', 
                    default = "mingle#trip")
parser.add_argument('-l', help = 'Sabre Login Key',
                    required = True, dest = 'loginkey')
parser.add_argument('-n', help = 'Number of data points to '
                    'send to Dashing server, This will be the nuber of '
                    'values shown on the x-axis of the graph', 
                    required = False, dest = 'num_recs', default = 12)
parser.add_argument('-i', help = 'Interval of data points to '
                    'plot, where this number represents how many records '
                    'in history file to skip in order to plot data points '
                    'beyond the default 5 minute interval',
                    required = False, dest = 'num_interval', default = 1)
parser.add_argument('-f', help ='Name of file to write stats to', 
                    required = False, dest = 'historyfile', 
                    default = sys.argv[0].strip('py') + "history_dev")
parser.add_argument('-e', '--environment', help ='Dashing environment to use, '
                    'either "production" or "development", '
                    'Defaults to production which uses port 80, '
                    'Development uses port 3030',
                    required = False, dest = 'dashing_env', 
                    default = "production")
parser.add_argument('--version', help = 'Print version and exit', 
                    required = False, action = 'store_true')

__version__          = '0.0.1'
__author__           = 'Pete Cornell'

args                 = parser.parse_args()
auth_token           = args.authtoken
login_key            = args.loginkey
dashing_host         = args.dashing_host.strip('http://')
target_widget        = args.widget
dashing_env          = args.dashing_env
num_recs             = args.num_recs
num_interval         = args.num_interval
dashing_host         = "http://" + dashing_host
DATA_VIEW            = "points"
historyfile          = args.historyfile
echo_version         = args.version


try:
    dashing_env == "production": dashing_http_port = "80" 
    dashing_env == "development": dashing_http_port = "3030" 
except Exception:
    exit(0)

server_connection    =  dashing_host + ':' + dashing_http_port + '/widgets/' + target_widget

HEADER = "# Time", "TAM Sessions"


def get_tam_usage(servers):
    pass


def save_tam_usage(stats):
    pass


def tail_history(num_recs, num_interval):
    
    '''
    * Load entire file into list
    * Split each line into separate list elements
    * Put tail -n into new list
    '''
    pass


def transmit_values(stat_values, target_widget):
    '''Send data to Dashing server via http.'''
    pass


def main():

    if echo_version:
        print "%s version: %s " % (sys.argv[0].strip('./'), __version__)
        exit(0)

    ##
    print "\nUsing options:"
    print "auth_token =>", auth_token
    print "login_key =>", login_key
    print "num_recs =>", num_recs
    print "num_interval =>", num_interval
    print "dashing_http_port =>", dashing_http_port
    print "server_connection =>", server_connection
    exit(0)
    ##

    # Create/check output file for header and write it if needed
    f = open(historyfile, 'r+')
    line = f.readline()
    if not line.startswith('#'):
        f.write(HEADER + "\n")
    f.close

    ##
    ## Call functions
    ##
    
    get_tam_usage
    save_tam_usage
    tail_history(num_recs, num_interval)
    transmit_values(stat_values, target_widget)

    # time to push to dashing



if __name__ == '__main__':
    main()
