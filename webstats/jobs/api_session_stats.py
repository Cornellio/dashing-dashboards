#!/usr/bin/env python

'''
Get api stats from all servers.
Add stats together.
Write sums of stats to file.
Push stats to dashing widgets.
'''

import os
import sys
import json
import time
import argparse
import urllib2
import httplib


def get_apipoolstats(servers, api_endpoint):

    '''
    Retrieve web API server stats from all given servers and return their sums.
    '''

    sum_tx_stats_active_sessions      = 0
    sum_tx_stats_borrowed_count       = 0
    sum_tx_stats_closed_sessions      = 0
    sum_tx_stats_created_count        = 0
    sum_tx_stats_destroyed_count      = 0
    sum_tx_stats_idle_sessions        = 0
    sum_non_tx_stats_active_sessions  = 0
    sum_non_tx_stats_borrowed_count   = 0
    sum_non_tx_stats_closed_sessions  = 0
    sum_non_tx_stats_created_count    = 0
    sum_non_tx_stats_destroyed_count  = 0
    sum_non_tx_stats_idle_sessions    = 0
    sum_non_tx_stats_returned_count   = 0

    for server in servers:

        request_url = "http://" + server + api_endpoint

        urldata      = urllib2.urlopen(request_url)
        response     = urldata.read()
        decoded      = json.loads(response)
        response_raw = json.dumps(decoded, sort_keys=True, indent=4)

        # values from TransactionalPoolStats
        tx_stats_active_sessions    = decoded['response']['transactionalPoolStats']['activeSessions']
        tx_stats_borrowed_count     = decoded['response']['transactionalPoolStats']['borrowedCount']
        tx_stats_closed_sessions    = decoded['response']['transactionalPoolStats']['closedSessions']
        tx_stats_created_count      = decoded['response']['transactionalPoolStats']['createdCount']
        tx_stats_destroyed_count    = decoded['response']['transactionalPoolStats']['destroyedCount']
        tx_stats_idle_sessions      = decoded['response']['transactionalPoolStats']['idleSessions']

        # values from nonTransactionalPoolStats
        non_tx_stats_active_sessions    = decoded['response']['nonTransactionalPoolStats']['activeSessions']
        non_tx_stats_borrowed_count     = decoded['response']['nonTransactionalPoolStats']['borrowedCount']
        non_tx_stats_closed_sessions    = decoded['response']['nonTransactionalPoolStats']['closedSessions']
        non_tx_stats_created_count      = decoded['response']['nonTransactionalPoolStats']['createdCount']
        non_tx_stats_destroyed_count    = decoded['response']['nonTransactionalPoolStats']['destroyedCount']
        non_tx_stats_idle_sessions      = decoded['response']['nonTransactionalPoolStats']['idleSessions']
        non_tx_stats_returned_count     = decoded['response']['nonTransactionalPoolStats']['returnedCount']

        # Get sums of each stat
        sum_tx_stats_active_sessions     += tx_stats_active_sessions
        sum_tx_stats_borrowed_count      += tx_stats_borrowed_count
        sum_tx_stats_closed_sessions     += tx_stats_closed_sessions
        sum_tx_stats_created_count       += tx_stats_created_count
        sum_tx_stats_destroyed_count     += tx_stats_destroyed_count
        sum_tx_stats_idle_sessions       += tx_stats_idle_sessions
        sum_non_tx_stats_active_sessions += non_tx_stats_active_sessions
        sum_non_tx_stats_borrowed_count  += non_tx_stats_borrowed_count
        sum_non_tx_stats_closed_sessions += non_tx_stats_closed_sessions
        sum_non_tx_stats_created_count   += non_tx_stats_created_count
        sum_non_tx_stats_destroyed_count += non_tx_stats_destroyed_count
        sum_non_tx_stats_idle_sessions   += non_tx_stats_idle_sessions
        sum_non_tx_stats_returned_count  += non_tx_stats_returned_count

        urldata.close()

    return (sum_tx_stats_active_sessions,
            sum_tx_stats_borrowed_count,
            sum_tx_stats_closed_sessions,
            sum_tx_stats_created_count,
            sum_tx_stats_destroyed_count,
            sum_tx_stats_idle_sessions,
            sum_non_tx_stats_active_sessions,
            sum_non_tx_stats_borrowed_count,
            sum_non_tx_stats_closed_sessions,
            sum_non_tx_stats_created_count,
            sum_non_tx_stats_destroyed_count,
            sum_non_tx_stats_idle_sessions,
            sum_non_tx_stats_returned_count)


def save_values(stats):

    '''Write time and sums of stats to csv file.'''

    now_time = time.strftime("%H:%M")
    now_date = time.strftime("%Y-%m-%d")
    time_stamp = now_date + " " + now_time

    stats = str(stats).strip('()') + "\n"

    line = time_stamp + ", " + stats
    f = open(historyfile, 'a')
    f.write(line)
    f.close


def tail_history(num_recs, selected_stat):

    '''
    Load file into list.
    Split each line by list element.
    Put tail -n into new list.
    '''

    f = open(historyfile, 'r')
    f.readline() # read oine line to skip header
    lines = f.read()
    lines = lines.split('\n')
    lines_len = len(lines) - 1

    lines_start = ( int(lines_len) -1 ) - int(num_recs)
    lines_end = lines_len

    # Make line selection from which to create json string
    lines_selected = lines[lines_start:lines_end]
    lines_selected_separated = '\n'.join(lines_selected) + '\n' # long listing
    line_range = len(lines_selected)

    # Build string of values for dashing server, like jSON but not exaclty
    json_post_data = ''
    for line_no in xrange(1, line_range):
        json_post_segment = lines_selected[line_no].split(', ')[selected_stat]

        if line_no == 1:
            json_post_data += '[ { "x": ' + str(line_no) + ', "y": ' + json_post_segment + ' }, '
        if line_no > 1 and line_no < len(lines_selected):
            json_post_data += '{ "x": ' + str(line_no) + ', "y": ' + json_post_segment + ' }, '
        if line_no == line_range - 1:
            json_post_data += '{ "x": ' + str(line_no) + ', "y": ' + json_post_segment + ' } ]'

    print "Constructed JSON string, %s values: \n%s" % (str(num_recs), json_post_data)
    f.close()
    return json_post_data


def transmit_values(stat_values, target_widget, auth_token, dashing_host):

    '''Send data to Dashing server.'''

    data = '{ "auth_token": "' + auth_token + ", "points":' + stat_values + '}'

    http = httplib.HTTPConnection(dashing_host)
    urlopen = urllib2.urlopen('http://' + dashing_host, data)

    try:
        http.request('POST', '/widgets/' + target_widget, data)
        response = http.getresponse()
        return response.read()
    except IOError:
        return "http connection failure"


def parse_args():
    '''Parse command line arguments.'''
    parser = argparse.ArgumentParser(
                        description = 'Retrieve and process API session stats '
                        'and send to Dashing server for display')
    parser.add_argument('-s', help ='API servers to collect stats from',
                        required = False, dest = 'servers',
                        default = 'wwwapidev03-sc9 wwwapidev04-sc9')
    parser.add_argument('-d', help ='Dashing server to push data to',
                        required = False, dest = 'dashing_host',
                        default = 'dashing.virginam.com')
    parser.add_argument('-w', help ='Widget to send data to',
                        required = False, dest = 'widget',
                        default = 'web_api_stats')
    parser.add_argument('--stat', help = 'stat to send '
                        'to Dashing server',
                        required = False, dest = 'stat',
                        default = "sum_tx_stats_active_sessions" )
    parser.add_argument('-n', help = 'Number of data points to '
                        'send to Dashing server, This will be the nuber of '
                        'values shown on the x-axis of the graph',
                        required = False, dest = 'num_recs', default = 12)
    parser.add_argument('-a', help = 'Authentication token '
                        'used by Dashing server',
                        required = True, dest = 'authtoken')
    parser.add_argument('-f', help ='Name of file to record stats to',
                        required = False, dest = 'historyfile',
                        default = sys.argv[0].strip('py') + "history")
    parser.add_argument('--environment', help ='Dashing environment to use, '
                        'either "production" or "development", '
                        'Defaults to production which uses port 80, '
                        'Development uses port 3030',
                        required = False, dest = 'dashing_env',
                        default = "production")

    args = parser.parse_args()
    return args


def main():

    args = parse_args()

    if args.dashing_env == "production":
        dashing_http_port = "80"
    if args.dashing_env == "development":
        dashing_http_port = "3030"

    historyfile = sys.argv[0].strip('py') + "history"
    dashing_host = args.dashing_host + ":" + dashing_http_port
    api_endpoint = '/api/v0/config/pool-stats'

    HEADER = ( "# Time, "
        "tx Active Sessions, "
        "tx Borrowed Count, "
        "tx Closed Sessions, "
        "tx Created Count, "
        "tx Destroyed Count, "
        "tx Idle Sessions, "
        "non-tx Active Sessions, "
        "non-tx Borrowed Count, "
        "non-tx Closed Sessions, "
        "non-tx Created Count, "
        "non-tx Destroyed Count, "
        "non-tx Idle Sessions, "
        "non-tx Returned Count" )

    # Create output file if needed
    f = open(historyfile, 'r+')
    line = f.readline()
    if not line.startswith('#'):
        f.write(HEADER + "\n")
    f.close

    sum_stats = get_apipoolstats(args.servers.split())
    save_values(sum_stats)

    # Map status names to csv field numbers
    status_map = {
        'timestamp':                         0,
        'sum_tx_stats_active_sessions':      1,
        'sum_tx_stats_borrowed_count':       2,
        'sum_tx_stats_closed_sessions':      3,
        'sum_tx_stats_created_count':        4,
        'sum_tx_stats_destroyed_count':      5,
        'sum_tx_stats_idle_sessions':        6,
        'sum_non_tx_stats_active_sessions':  7,
        'sum_non_tx_stats_borrowed_count':   8,
        'sum_non_tx_stats_closed_sessions':  9,
        'sum_non_tx_stats_created_count':    10,
        'sum_non_tx_stats_destroyed_count':  11,
        'sum_non_tx_stats_idle_sessions':    12,
        'sum_non_tx_stats_returned_count':   13
      }

    stat_values = tail_history(args.num_recs, status_map[args.stat])
    transmit_values(stat_values, args.widget, args.auth_token, dashing_host)


if __name__ == '__main__':
    main()
