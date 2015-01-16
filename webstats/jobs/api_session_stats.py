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
# from datetime import date
# from datetime import datetime

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

API_SERVER_LIST = ['wwwapidev03-sc9', 'wwwapidev05-sc9']
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

    # Get datestamp
    now_time = time.strftime("%H:%M")
    now_date = time.strftime("%Y-%m-%d")
    time_stamp = now_date + " " + now_time

    stats = str(stats).strip('()') + "\n" # convert integers to string and strip out ()
    line = time_stamp + ", " + stats
    f = open(SESSION_HISTORY_FILE, 'a')
    f.write(line)
    print "\nWriting values:\n", line
    f.close


def update_widget():


  # echo "Sending ${#} values to ${TARGET_WIDGET} widget:  ${*}"
  # # Data points to post must match $value_len ##
  # post_data="[ { \"x\": 1, \"y\":  ${1} }, \
  #   { \"x\": 2, \"y\":  ${2} }, \
  #   { \"x\": 3, \"y\":  ${3} }, \
  #   { \"x\": 4, \"y\":  ${4} }, \
  #   { \"x\": 5, \"y\":  ${5} }, \
  #   { \"x\": 6, \"y\":  ${6} }, \
  #   { \"x\": 7, \"y\":  ${7} }, \
  #   { \"x\": 8, \"y\":  ${8} }, \
  #   { \"x\": 9, \"y\":  ${9} }, \
  #   { \"x\": 10, \"y\": ${10} }, \
  #   { \"x\": 11, \"y\": ${11} }, \
  #   { \"x\": 12, \"y\": ${12} }, \
  #   { \"x\": 13, \"y\": ${13} }, \
  #   { \"x\": 14, \"y\": ${14} }, \
  #   { \"x\": 15, \"y\": ${15} }, \
  #   { \"x\": 16, \"y\": ${16} }, \
  #   { \"x\": 17, \"y\": ${17} }, \
  #   { \"x\": 18, \"y\": ${18} }, \
  #   { \"x\": 19, \"y\": ${19} }, \
  #   { \"x\": 20, \"y\": ${20} }, \
  #   { \"x\": 21, \"y\": ${21} }, \
  #   { \"x\": 22, \"y\": ${22} }, \
  #   { \"x\": 23, \"y\": ${23} }, \
  #   { \"x\": 24, \"y\": ${24} } ]"
  # curl -d "{ \"auth_token\": \"${AUTH_TOKEN}\", \"${DATA_VIEW}\": ${post_data} }" ${SERVER_CONNECTION}

  pass

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

    sum_stats = get_apipoolstats(API_SERVER_LIST)
    save_values(sum_stats)


if __name__ == '__main__':
    main()
