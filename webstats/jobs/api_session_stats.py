#!/usr/bin/python
# 
# Get api stats from all servers
# Add stats together
# Write sums of stats to file
# Push stats to dashing widgets
#
# TODO: 
#   - fix repeated value in last pair of json string
#   - make sure sums are right, x
#   - do the http post of json string

__version__ = '0.0.1'

import os
import sys
import json
import time
import argparse
import urllib2
import httplib


parser = argparse.ArgumentParser(
    description = 'Process API session statistics and push to dashing server.')
parser.add_argument(
    '-v', '--version', help = 'Print version', 
    required = False, action = 'store_true')
parser.add_argument('-t', '--authtoken', help = 'Authentication token', 
    required = False, dest = 'authtoken', default = "mingle#trip")
parser.add_argument('-r', '--servers', help ='API servers to get stats from',
    required = False, dest = 'servers', 
    default = 'wwwapidev03-sc9 wwwapidev05-sc9')
parser.add_argument('-d', '--dashinghost', help ='Dashing server to push data to',
    required = False, dest = 'dashing_host', default = 'dashing.virginam.com')
parser.add_argument('-w', '--widget', help ='Widget to send data to', 
    required = False, dest = 'widget', default = 'web_api_stats')
parser.add_argument('-f', '--historyfile', help ='File to store stats in', 
    required = False, dest = 'historyfile', default = sys.argv[0].strip('py') + "history")
parser.add_argument('-e', '--environment', help ='Dashing environment', 
    required = False, dest = 'dashing_env', default = "production")
parser.add_argument('-n', '--records', help = 'Number of records to transmit when pushing stats to dashing server. This will be the nuber of values shown on the x-axis of the graph.', required = False, dest = 'num_recs', default = 12)
parser.add_argument('-s', '--stat', help = "API stat to transmit to dashing server.", 
    required = False, dest = 'stat', default = "sum_tx_stats_active_sessions" )

args                 = parser.parse_args()
auth_token           = args.authtoken
echo_version         = args.version
servers              = args.servers.split()
dashing_host         = args.dashing_host.strip('http://')
target_widget        = args.widget
dashing_env          = args.dashing_env
num_recs = args.num_recs
stat_to_graph        = args.stat
dashing_host         = "http://" + dashing_host
server_connection    =  dashing_host + '/widgets/' + target_widget
DATA_VIEW            = "points"
historyfile          = sys.argv[0].strip('py') + "history"

if dashing_env == "production": dashing_http_port = "80" 
if dashing_env == "testing": dashing_http_port = "3030" 

##
print "\nUsing options:"
print "auth_token =>", auth_token
print "servers =>", servers
print "num_recs =>", num_recs
print "stat_to_graph =>", stat_to_graph
print "dashing_http_port =>", dashing_http_port
print "server_connection =>", server_connection
##

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


def get_apipoolstats(servers):
    
    '''
    Cycle through all API servers, retrieve stats, add values together.
    Return sum of stats.
    '''

    # servers = ['wwwapidev03-sc9']
    
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

        request_url = "http://" + server + '/api/v0/config/pool-stats'
        print "\nchecking", request_url

        # sample_json_data = '{"status":{"status":"SUCCESS"},"response":{"transactionalPoolStats":{"createdCount":753,"destroyedCount":753,"closedSessions":753,"activeSessions":0,"idleSessions":0,"borrowedCount":753},"nonTransactionalPoolStats":{"createdCount":79,"destroyedCount":79,"closedSessions":79,"activeSessions":0,"idleSessions":0,"borrowedCount":15646,"returnedCount":15646}}}'
        urldata          = urllib2.urlopen(request_url)
        response         = urldata.read()
        decoded          = json.loads(response)
        response_raw     = json.dumps(decoded, sort_keys=True, indent=4)

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

        # Add values together
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

        # Testing output
        print "\nTransactional:"
        print "tx_stats_active_sessions     ", tx_stats_active_sessions 
        print "tx_stats_borrowed_count      ", tx_stats_borrowed_count
        print "tx_stats_closed_sessions     ", tx_stats_closed_sessions
        print "tx_stats_created_count       ", tx_stats_created_count
        print "tx_stats_destroyed_count     ", tx_stats_destroyed_count
        print "tx_stats_idle_sessions       ", tx_stats_idle_sessions
        print "\nNon Transactional:"
        print "non_tx_stats_active_sessions ",  non_tx_stats_active_sessions 
        print "non_tx_stats_borrowed_count  ",  non_tx_stats_borrowed_count  
        print "non_tx_stats_closed_sessions ",  non_tx_stats_closed_sessions 
        print "non_tx_stats_created_count   ",  non_tx_stats_created_count   
        print "non_tx_stats_destroyed_count ",  non_tx_stats_destroyed_count 
        print "non_tx_stats_idle_sessions   ",  non_tx_stats_idle_sessions   
        print "non_tx_stats_returned_count  ",  non_tx_stats_returned_count  

        urldata.close()

    print "\nSums:"
    print "\nTransactional:"
    print "sum_tx_stats_active_sessions     ", sum_tx_stats_active_sessions
    print "sum_tx_stats_borrowed_count      ", sum_tx_stats_borrowed_count
    print "sum_tx_stats_closed_sessions     ", sum_tx_stats_closed_sessions
    print "sum_tx_stats_created_count       ", sum_tx_stats_created_count
    print "sum_tx_stats_destroyed_count     ", sum_tx_stats_destroyed_count
    print "sum_tx_stats_idle_sessions       ", sum_tx_stats_idle_sessions
    print "\nNon Transactional:"
    print "sum_non_tx_stats_active_sessions ", sum_non_tx_stats_active_sessions
    print "sum_non_tx_stats_borrowed_count  ", sum_non_tx_stats_borrowed_count
    print "sum_non_tx_stats_closed_sessions ", sum_non_tx_stats_closed_sessions
    print "sum_non_tx_stats_created_count   ", sum_non_tx_stats_created_count
    print "sum_non_tx_stats_destroyed_count ", sum_non_tx_stats_destroyed_count
    print "sum_non_tx_stats_idle_sessions   ", sum_non_tx_stats_idle_sessions
    print "sum_non_tx_stats_returned_count  ", sum_non_tx_stats_returned_count

    return sum_tx_stats_active_sessions, sum_tx_stats_borrowed_count, sum_tx_stats_closed_sessions, sum_tx_stats_created_count, sum_tx_stats_destroyed_count, sum_tx_stats_idle_sessions, sum_non_tx_stats_active_sessions, sum_non_tx_stats_borrowed_count, sum_non_tx_stats_closed_sessions, sum_non_tx_stats_created_count, sum_non_tx_stats_destroyed_count, sum_non_tx_stats_idle_sessions, sum_non_tx_stats_returned_count


def save_values(stats):

    '''Write sums of all stats to file.'''

    # Get timestamp
    now_time = time.strftime("%H:%M")
    now_date = time.strftime("%Y-%m-%d")
    time_stamp = now_date + " " + now_time

    stats = str(stats).strip('()') + "\n" # convert integers to string and strip out ()
    line = time_stamp + ", " + stats
    f = open(historyfile, 'a')
    f.write(line)
    print "\nWriting new values: ", line
    f.close


def tail_history(n, target_stat):
    
    '''
    * Load entire file into list
    * Split each line into separate list elements
    * Put tail -n into new list
    * Send to dashboard
    '''

    f = open(historyfile, 'r')
    f.readline() # skip header
    lines = f.read()
    lines = lines.split('\n')
    lines_len = len(lines) - 1
    
    print "\nNumber of lines in file: ", lines_len
    print "Target stat to graph:", target_stat
    # print "\nAll recs:\n", lines

    # rec_slice = lines[1:5]
    lines_start = ( int(lines_len) -1 ) - int(n)
    lines_end = lines_len
    # print lines_start, lines_end
    
    # Make line selection from which to create json string
    lines_selected = lines[lines_start:lines_end] 
    lines_selected_separated = '\n'.join(lines_selected) + '\n' # long listing
    print lines_selected_separated
    line_range = len(lines_selected)

    # Build JSON String
    json_post_data = ''
    for line_no in xrange(1, line_range):
        json_post_segment = lines_selected[line_no].split(', ')[target_stat]
        
        if line_no == 1:
            json_post_data += '[ { "x": ' + str(line_no) + ', "y": ' + json_post_segment + ' }, '
        if line_no > 1 and line_no < len(lines_selected):
            json_post_data += '{ "x": ' + str(line_no) + ', "y": ' + json_post_segment + ' }, '
        if line_no == line_range - 1:
            json_post_data += '{ "x": ' + str(line_no) + ', "y": ' + json_post_segment + ' } ]'

    print "Constructed JSON string containing %s values: \n%s" % (str(n), json_post_data)
    return json_post_data
    f.close()

def transmit_values():
    '''Send data to dashing server via http.'''
    
    json_data = '[ { "x": 1, "y": 121 }, { "x": 2, "y": 104 }, { "x": 3, "y": 104 }, { "x": 4, "y": 104 }, { "x": 5, "y": 104 }, { "x": 6, "y": 161 }, { "x": 7, "y": 161 }, { "x": 8, "y": 161 }, { "x": 9, "y": 161 }, { "x": 10, "y": 161 }, { "x": 11, "y": 161 }, { "x": 12, "y": 161 }, { "x": 12, "y": 1765 } ]'

    post_data = '{ "auth_token": "mingle#trip", "points":' + json_data + '}'

    print post_data
    # exit(0)

    h = httplib.HTTPConnection('dashing.virginam.com:3030')

    u = urllib2.urlopen('http://dashing.virginam.com:3030', post_data)

    h.request('POST', '/widgets/sum_tx_stats_active_sessions', post_data)
    r = h.getresponse()
    print r.read()


def main():

    if echo_version:
        print "%s version: %s " % (sys.argv[0].strip('./'), __version__)
        exit(0)

    # Create/check output file for header and write it if needed
    f = open(historyfile, 'r+')
    line = f.readline()
    if not line.startswith('#'):
        f.write(HEADER + "\n")
    f.close

    ##
    ## Call functions
    ##
    
    sum_stats = get_apipoolstats(servers)
    save_values(sum_stats)

    # time to push the to dashing

    # Mapping of status values
    stats_map = {
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

    stat_values = tail_history(num_recs, stats_map[stat_to_graph])
    

if __name__ == '__main__':
    main()
