#!/usr/bin/python

'''
Dashing job for graphing Sabre TAM pool usage.
Lookup current TAM pool usage from Sabre, save results to a file,
then read historical values from file and post to a Dashing graph.
'''
# TODO: Fix repeated last value

import sys
import time
import argparse
import urllib2
import httplib


def return_args():
    '''Parse command line arguments'''

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
    parser.add_argument('--http_endpoint', help='HTTP endpoint from which to '
                        'lookup stats', required=True)
    parser.add_argument('-k', help='Sabre Login Key',
                        required=False, dest='loginkey', default='tst_key')
    parser.add_argument('-n', help='Number of data points to '
                        'send to Dashing server, This will be the nuber of '
                        'values shown on the x-axis of the graph',
                        required=False, type=int, dest='num_recs', default=12)
    parser.add_argument('-i', help='Interval of data points to '
                        'plot, where this number represents how many records '
                        'in history file to skip when plotting data points, '
                        'Allows plotting intervals other than default 5 '
                        'minute interval', required=False, type=int,
                        dest='num_interval', default=1)
    parser.add_argument('-x', '--skip_tam_lookup', help='Do not lookup '
                        'current TAM usage from Sabre, just graph historical '
                        'values', dest='skip_tam_lookup', required=False,
                        action='store_true')
    parser.add_argument('-f', help='Name of file to write stats to',
                        required=False, dest='historyfile',
                        default=sys.argv[0].strip('py') + "history")
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
    DATA_VIEW     = "graph"
    historyfile   = args.historyfile
    http_endpoint = args.http_endpoint
    skip_lookup   = args.skip_tam_lookup

    return (auth_token,
            login_key,
            dashing_host,
            target_widget,
            dashing_env,
            num_recs,
            num_interval,
            DATA_VIEW,
            historyfile,
            http_endpoint,
            skip_lookup)


def check_file(file, header):
    '''Create output file and write heater'''

    try:
        f = open(file, 'r')
    except:
        f = open(file, 'w+')
        line = f.readline()
        if not line.startswith('#'):
            f.write(header)
        f.close


def set_environment(environment):
    if environment == "production":
        dashing_http_port = "80"
    elif environment == "development":
        dashing_http_port = "3030"
    else:
        environment = None
        dashing_http_port = None
    return environment, dashing_http_port


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
                value = line.split(", ")
                value = value[1]
                values.append(value)
    values = values[-num:]

    # Select every n'th occurance in list, where n is the skip_interval
    i = 0
    selected_values = []
    for value in values:
        i += 1
        if (i % skip_interval) == 0:
            selected_values.append(value)

    return selected_values


def get_tam_usage(server, key):
    '''Lookup TAM usage via HTTP and return it'''

    tam_usage_field_num = 53

    request_url = server + '?loginKey=' + key
    urldata = urllib2.urlopen(request_url)
    response = urldata.read()
    tam_usage = response.split()[tam_usage_field_num]

    return tam_usage


def save_tam_usage(file_out, value):

    now_time = time.strftime("%H:%M")
    now_date = time.strftime("%Y-%m-%d")
    time_stamp = now_date + " " + now_time

    with open(file_out, 'a') as f:
        line = time_stamp + ", " + value
        f.write(line + "\n")


def graph_points(values):
    '''Construct a formatted string of points from list of values'''

    points = ''
    for record_num in range(0, len(values)):
        data_segment = values[record_num]
        x_value = str(record_num + 1)

        if record_num == 0:
            points += '[{ "x": ' + x_value + ', "y": ' + str(data_segment) + ' }, '
        if record_num > 0 and record_num < len(values)-1:
            points += '{ "x": ' + x_value + ', "y": ' + str(data_segment) + ' }, '
        if record_num == len(values)-1:
            points += '{ "x": ' + x_value + ', "y": ' + str(data_segment) + ' }]'

    return points


def transmit_values(host, port, widget, token, data):
    '''Send data to Dashing server via http'''

    post_data = '{ "auth_token": "' + token + '", "points": ' + data + '} '
    print "Transmitting to", host + ':' + port + '/widgets/' + widget
    print "Data: ", data

    http = httplib.HTTPConnection(host, port)
    http.request('POST', '/widgets/' + widget, post_data)

    response = http.getresponse()
    print response.read()


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
        http_endpoint,
        skip_lookup) = return_args()

    environment, dashing_http_port = set_environment(dashing_env)

    if environment is None:
        print "Bad environment setting:\nTry " + sys.argv[0] + " -h"
        exit(1)

    HEADER = '# Time, TAM Sessions\n'

    check_file(historyfile, HEADER)

    ##
    print "\nUsing options:"
    print "auth_token =>", auth_token
    print "login_key =>", login_key
    print "num_recs =>", num_recs
    print "num_interval =>", num_interval
    print "dashing_http_port =>", dashing_http_port
    print "server_connection =>", (dashing_host + ':' + dashing_http_port +
                                   '/widgets/' + target_widget)
    print "historyfile =>", historyfile
    print "header", HEADER

    #
    # Call functions
    #

    # To just graph historical values, don't lookup current value
    if skip_lookup is False:
        tam_usage = get_tam_usage(http_endpoint, login_key)
        save_tam_usage(historyfile, tam_usage)

    selected_values = tail_history(historyfile, num_recs, num_interval)
    points = graph_points(selected_values)
    transmit_values(dashing_host, dashing_http_port,
                    target_widget, auth_token, points)


if __name__ == '__main__':
    main()
