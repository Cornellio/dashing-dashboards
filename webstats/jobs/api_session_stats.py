#!/usr/bin/python
# 
# Get api stats from all servers
# Add stats together
# Write sums of stats to file
# Push stats to dashing widgets

import os
import sys
import urllib
import json
import time

API_SERVER_LIST = ['wwwapidev03-sc9', 'wwwapidev05-sc9']

DASHING_SERVER = "http://dashing.virginam.com"
AUTH_TOKEN = "mingle#trip"
TARGET_WIDGET="tbd" # Need to add
SERVER_CONNECTION = "${DASHING_SERVER}/widgets/${TARGET_WIDGET}"
DATA_VIEW = "points"
SESSION_HISTORY_FILE = sys.argv[0].strip('py') + "history"
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

DASHING_HTTP_PORT_DEV = "3030"
DASHING_HTTP_PORT_PROD = "80"


def get_apipoolstats(api_server_list):
    
    '''
    Cycle through all API servers, retrieve stats, add values together.
    Return sum of stats.
    '''

    # api_server_list = ['wwwapidev03-sc9']
    
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

    for server in api_server_list:

        request_url = "http://" + server + '/api/v0/config/pool-stats'
        print "\nchecking", request_url

        # sample_json_data = '{"status":{"status":"SUCCESS"},"response":{"transactionalPoolStats":{"createdCount":753,"destroyedCount":753,"closedSessions":753,"activeSessions":0,"idleSessions":0,"borrowedCount":753},"nonTransactionalPoolStats":{"createdCount":79,"destroyedCount":79,"closedSessions":79,"activeSessions":0,"idleSessions":0,"borrowedCount":15646,"returnedCount":15646}}}'
        urldata          = urllib.urlopen(request_url)
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
        print "nonTransactionalPoolStats:"
        print "non_tx_stats_active_sessions ",  non_tx_stats_active_sessions 
        print "non_tx_stats_borrowed_count  ",  non_tx_stats_borrowed_count  
        print "non_tx_stats_closed_sessions ",  non_tx_stats_closed_sessions 
        print "non_tx_stats_created_count   ",  non_tx_stats_created_count   
        print "non_tx_stats_destroyed_count ",  non_tx_stats_destroyed_count 
        print "non_tx_stats_idle_sessions   ",  non_tx_stats_idle_sessions   
        print "non_tx_stats_returned_count  ",  non_tx_stats_returned_count  

        print "transactionalPoolStats:"
        print "tx_stats_active_sessions     ", tx_stats_active_sessions 
        print "tx_stats_borrowed_count      ", tx_stats_borrowed_count
        print "tx_stats_closed_sessions     ", tx_stats_closed_sessions
        print "tx_stats_created_count       ", tx_stats_created_count
        print "tx_stats_destroyed_count     ", tx_stats_destroyed_count
        print "tx_stats_idle_sessions       ", tx_stats_idle_sessions

        urldata.close()

    print "\nSums:"
    print "sum_tx_stats_active_sessions", sum_tx_stats_active_sessions
    print "sum_tx_stats_borrowed_count", sum_tx_stats_borrowed_count
    print "sum_tx_stats_closed_sessions", sum_tx_stats_closed_sessions
    print "sum_tx_stats_created_count", sum_tx_stats_created_count
    print "sum_tx_stats_destroyed_count", sum_tx_stats_destroyed_count
    print "sum_tx_stats_idle_sessions", sum_tx_stats_idle_sessions
    print "sum_non_tx_stats_active_sessions", sum_non_tx_stats_active_sessions
    print "sum_non_tx_stats_borrowed_count", sum_non_tx_stats_borrowed_count
    print "sum_non_tx_stats_closed_sessions", sum_non_tx_stats_closed_sessions
    print "sum_non_tx_stats_created_count", sum_non_tx_stats_created_count
    print "sum_non_tx_stats_destroyed_count", sum_non_tx_stats_destroyed_count
    print "sum_non_tx_stats_idle_sessions", sum_non_tx_stats_idle_sessions
    print "sum_non_tx_stats_returned_count", sum_non_tx_stats_returned_count

    return sum_tx_stats_active_sessions, sum_tx_stats_borrowed_count, sum_tx_stats_closed_sessions, sum_tx_stats_created_count, sum_tx_stats_destroyed_count, sum_tx_stats_idle_sessions, sum_non_tx_stats_active_sessions, sum_non_tx_stats_borrowed_count, sum_non_tx_stats_closed_sessions, sum_non_tx_stats_created_count, sum_non_tx_stats_destroyed_count, sum_non_tx_stats_idle_sessions, sum_non_tx_stats_returned_count


def save_values(stats):

    '''Write sums of all stats to file.'''

    # Get timestamp
    now_time = time.strftime("%H:%M")
    now_date = time.strftime("%Y-%m-%d")
    time_stamp = now_date + " " + now_time

    stats = str(stats).strip('()') + "\n" # convert integers to string and strip out ()
    line = time_stamp + ", " + stats
    f = open(SESSION_HISTORY_FILE, 'a')
    f.write(line)
    print "\nWriting new values: ", line
    f.close


def transmit_values(num_of_recs, select_value):
    
    '''
    * Load entire file into list
    * Split each line into separate list elements
    * Put tail -n into new list
    * Send to dashboard
    '''

    f = open(SESSION_HISTORY_FILE, 'r')
    f.readline() # skip header
    lines = f.read()
    lines = lines.split('\n')
    lines_len = len(lines) - 1
    
    print "\nNumber of lines: ", lines_len
    # print "\nAll recs:\n", lines

    # rec_slice = lines[1:5]
    lines_start = ( int(lines_len) -1 ) - int(num_of_recs)
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
        json_post_segment = lines_selected[line_no].split(', ')[select_value]
        
        if line_no == 1:
            json_post_data += '[ { "x": ' + str(line_no) + ', "y": ' + json_post_segment + ' }, '
        if line_no > 1 and line_no < len(lines_selected):
            json_post_data += '{ "x": ' + str(line_no) + ', "y": ' + json_post_segment + ' }, '
        if line_no == line_range - 1:
            json_post_data += '{ "x": ' + str(line_no) + ', "y": ' + json_post_segment + ' } ]'

    print "Sending JSON string, %s values: \n%s" % (str(num_of_recs), json_post_data)
    f.close()


# Lookup recent values in file
def get_recent_values():
    # value_len = "24"
  
    # recent_values = ( tail -n ${value_len} $SESSION_HISTORY_FILE )
    # for value in $recent_values:
    #     i += 1
    #     value[i]=field[i]
    pass


def main():

    # Create/check output file for header and write it if needed
    f = open(SESSION_HISTORY_FILE, 'r+')
    line = f.readline()
    if not line.startswith('#'):
        f.write(HEADER + "\n")
    f.close

    ##
    ## Call functions
    ##
    
    # sum_stats = get_apipoolstats(API_SERVER_LIST)
    # save_values(sum_stats)

    # time to push the bits to dashing

    # Mapping of stat values
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

    # Receive argument here for # of recs to get and target_value
    NUM_OF_RECS = 5
    target_value = "sum_non_tx_stats_returned_count"

    transmit_values(NUM_OF_RECS, stats_map[target_value])

if __name__ == '__main__':
    main()
