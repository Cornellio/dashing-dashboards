#!/usr/bin/python

'''
Lookup current TAM pool usage from Sabre.
Save results to file.
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

__version__ = '0.0.1'
__author__  = 'Pete Cornell'


def return_args():

    parser = argparse.ArgumentParser(
        description='Retrieve and process Sabre TAM usage '
        'and send to Dashing server for display')
    parser.add_argument('-d', help='Dashing server to push data to',
                        required=False, dest='dashing_host',
                        default='dashing.virginam.com')
    parser.add_argument('-w', help='Widget to send data to',
                        required=False, dest='widget',
                        default='sabresessions')
    parser.add_argument('-a', help='Authentication token '
                        'used by Dashing server',
                        required=False, dest='authtoken',
                        default="mingle#trip")
    parser.add_argument('-l', help='Sabre Login Key',
                        required=False, dest='loginkey', default='tst_key')
    parser.add_argument('-n', help='Number of data points to '
                        'send to Dashing server, This will be the nuber of '
                        'values shown on the x-axis of the graph',
                        required=False, dest='num_recs', default=12)
    parser.add_argument('-i', help='Interval of data points to '
                        'plot, where this number represents how many records '
                        'in history file to skip when plotting data points, '
                        'Allows plotting intervals other than default 5 '
                        'minute interval',
                        required=False, dest='num_interval', default=1)
    parser.add_argument('-f', help='Name of file to write stats to',
                        required=False, dest='historyfile',
                        default=sys.argv[0].strip('py') + "history_dev")
    parser.add_argument('-e', '--environment', help='Dashing environment '
                        'to use, either "production" or "development", '
                        'Defaults to production which uses port 80, '
                        'Development uses port 3030',
                        required=False, dest='dashing_env',
                        default="production")
    parser.add_argument('--version', help='Print version and exit',
                        required=False, action='store_true')

    args          = parser.parse_args()
    auth_token    = args.authtoken
    login_key     = args.loginkey
    dashing_host  = args.dashing_host.strip('http://')
    target_widget = args.widget
    dashing_env   = args.dashing_env
    num_recs      = args.num_recs
    num_interval  = args.num_interval
    dashing_host  = "http://" + dashing_host
    DATA_VIEW     = "points"
    historyfile   = args.historyfile
    echo_version  = args.version

    return (auth_token,
            login_key,
            dashing_host,
            target_widget,
            dashing_env,
            num_recs,
            num_interval,
            DATA_VIEW,
            historyfile,
            echo_version)


def get_tam_usage(servers):
    pass


def save_tam_usage(stats):
    pass


def tail_history(file, num, skip_interval):

    '''
    * Load entire file into list
    * Split each line into separate list elements
    * Put tail -n into new list
    '''

    with open(file) as f:
        f.readline()
        values = []
        for line in f:
            if line.strip():
                value = line.split()
                value = int(value[1])
                values.append(value)
    values = values[-num:]

    # Select values based on skip_interval
    i = 0
    selected_values = []
    for value in values:
        i += 1
        if (i % skip_interval) == 0:
            selected_values.append(value)

    return selected_values


def transmit_values(stat_values, target_widget):
    '''Send data to Dashing server via http'''
    pass


def set_environment(environment):
    if environment == "production":
        dashing_http_port = "80"
    elif environment == "development":
        dashing_http_port = "3030"
    else:
        environment = None
        dashing_http_port = None
    return environment, dashing_http_port


def check_file(file, header):
    '''Create/check output file for header and write it if needed'''
    try:
        f = open(file, 'r')
    except:
        f = open(file, 'w+')
        line = f.readline()
        if not line.startswith('#'):
            f.write(header + "\n")
        f.close


def main():

    (auth_token,
        login_key,
        dashing_host,
        target_widget,
        dashing_env,
        num_recs,
        num_interval,
        DATA_VIEW,
        historyfile,
        echo_version) = return_args()

    if echo_version:
        print "%s version: %s " % (sys.argv[0].strip('./'), __version__)
        exit(0)

    environment, dashing_http_port = set_environment(dashing_env)
    if environment is None:
        print "Bad environment setting:\nTry " + sys.argv[0] + " -h"
        exit(1)

    server_connection = (dashing_host + ':' + dashing_http_port +
                         '/widgets/' + target_widget)

    HEADER = '# Time, TAM Sessions'

    check_file(historyfile, HEADER)

    ##
    print "\nUsing options:"
    print "auth_token =>", auth_token
    print "login_key =>", login_key
    print "num_recs =>", num_recs
    print "num_interval =>", num_interval
    print "dashing_http_port =>", dashing_http_port
    print "server_connection =>", server_connection
    print "historyfile =>", historyfile
    print "header", HEADER
    # exit(0)
    ##

    ##
    ## Call functions
    ##

    # get_tam_usage
    # save_tam_usage
    selected_values = tail_history(historyfile, num_recs, num_interval)
    print selected_values
    # transmit_values(stat_values, target_widget)

    # time to push to dashing


if __name__ == '__main__':
    main()
