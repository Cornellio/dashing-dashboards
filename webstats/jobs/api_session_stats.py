#!/usr/bin/python

import os
import sys
import urllib
import json
from pprint import pprint

DASHING_SERVER = "http://dashing.virginam.com"
AUTH_TOKEN = "mingle#trip"
TARGET_WIDGET="tbd" # Need to add
SERVER_CONNECTION = "${DASHING_SERVER}/widgets/${TARGET_WIDGET}"
DATA_VIEW = "points"
SESSION_HISTORY_FILE = "/home/vajobs/bin/sabre_session_history"

# # Lookup TAM usage via api call and append to file
# get_sabresessions () {
#   connections=$( curl -sL https://www.virginamerica.com/api/v0/session/usage?loginKey=${LOGINKEY} | awk '{print $54}'  )
#   echo $connections >> $SESSION_HISTORY_FILE
# }

def parse_json():
    input = '{"status":{"status":"SUCCESS"},"response":{"transactionalPoolStats":{"createdCount":753,"destroyedCount":753,"closedSessions":753,"activeSessions":0,"idleSessions":0,"borrowedCount":753},"nonTransactionalPoolStats":{"createdCount":79,"destroyedCount":79,"closedSessions":79,"activeSessions":0,"idleSessions":0,"borrowedCount":15646,"returnedCount":15646}}}'

    decoded = json.loads(input)

    json_data_raw = json.dumps(decoded, sort_keys=True, indent=4)

    # values from nonTransactionalPoolStats
    non_tx_stats_active_sessions    = decoded['response']['nonTransactionalPoolStats']['activeSessions']
    non_tx_stats_borrowed_count     = decoded['response']['nonTransactionalPoolStats']['borrowedCount']
    non_tx_stats_closed_sessions    = decoded['response']['nonTransactionalPoolStats']['closedSessions']
    non_tx_stats_created_count      = decoded['response']['nonTransactionalPoolStats']['createdCount']
    non_tx_stats_destroyed_count    = decoded['response']['nonTransactionalPoolStats']['destroyedCount']
    non_tx_stats_idle_sessions      = decoded['response']['nonTransactionalPoolStats']['idleSessions']
    non_tx_stats_returned_count     = decoded['response']['nonTransactionalPoolStats']['returnedCount']

    # values from TransactionalPoolStats
    tx_stats_active_sessions    = decoded['response']['transactionalPoolStats']['activeSessions']
    tx_stats_borrowed_count     = decoded['response']['transactionalPoolStats']['borrowedCount']
    tx_stats_closed_sessions    = decoded['response']['transactionalPoolStats']['closedSessions']
    tx_stats_created_count      = decoded['response']['transactionalPoolStats']['createdCount']
    tx_stats_destroyed_count    = decoded['response']['transactionalPoolStats']['destroyedCount']
    tx_stats_idle_sessions      = decoded['response']['transactionalPoolStats']['idleSessions']


def get_apipoolstats():

    api_server_list = ['wwwapidev03-sc9']
    stats_url = '/api/v0/config/pool-stats'
    
    for server in api_server_list:

        request_url = "http://" + server + stats_url
        print "checking", request_url
        url_handle = urllib.urlopen(request_url)
        info = url_handle.info()

        # response_json = {}
        # print 'checking', url_handle.geturl()
        if info.gettype() == 'application/json':
            response_json = url_handle.read()
            
            print "raw json response:\n", response_json + "\n"

            data = json.load(response_json)
            print "pprint json response:"
            pprint(data)
            # closedSessions = data["closedSessions"]


        url_handle.close()


def update_widget():
    pass

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


# Lookup recent values in file
def get_recent_values():
    pass
    # value_len = "24"
  
    # recent_values = ( tail -n ${value_len} $SESSION_HISTORY_FILE )
    # for value in $recent_values:
    #     i += 1
    #     value[i]=field[i]


def main():
    parse_json()
    # get_apipoolstats()
    # get_recent_values
    # print "values: ${values[*]}"
    # update_widget ${value[*]}


if __name__ == '__main__':
    main()
