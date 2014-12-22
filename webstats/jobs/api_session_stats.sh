#!/bin/bash
# @version $Id: push_api_session_stats.sh 936 2014-12-22 03:29:18Z pete.cornell $
#
# Push Sabre pool stats to dashboard server http://dashing.virginam.com
#
## Example curl to plot a sequence of data points:
# curl -d '{ "AUTH_TOKEN": "mingle#trip", "points": [{ "x" :1, "y" :250 }, { "x" :2, "y" :1120 }, { "x" :3, "y" :822 } ] }' http://dashing/widgets/webconnections
#
# TODO: make loop for post_data

# New call for pool data
# http://wwwapidev03-sc9.virginam.com/api/v0/config/pool-stats

DASHING_SERVER="http://dashing.virginam.com"
AUTH_TOKEN="mingle#trip"
TARGET_WIDGET=""
SERVER_CONNECTION="${DASHING_SERVER}/widgets/${TARGET_WIDGET}"
DATA_VIEW="points"
SESSION_HISTORY_FILE="/home/vajobs/bin/sabre_session_history"

# Send data points to dashboard server
update_widget () {
  echo "Sending ${#} values to ${TARGET_WIDGET} widget:  ${*}"
  # Data points to post must match $value_len ##
  post_data="[ { \"x\": 1, \"y\":  ${1} }, \
    { \"x\": 2, \"y\":  ${2} }, \
    { \"x\": 3, \"y\":  ${3} }, \
    { \"x\": 4, \"y\":  ${4} }, \
    { \"x\": 5, \"y\":  ${5} }, \
    { \"x\": 6, \"y\":  ${6} }, \
    { \"x\": 7, \"y\":  ${7} }, \
    { \"x\": 8, \"y\":  ${8} }, \
    { \"x\": 9, \"y\":  ${9} }, \
    { \"x\": 10, \"y\": ${10} }, \
    { \"x\": 11, \"y\": ${11} }, \
    { \"x\": 12, \"y\": ${12} }, \
    { \"x\": 13, \"y\": ${13} }, \
    { \"x\": 14, \"y\": ${14} }, \
    { \"x\": 15, \"y\": ${15} }, \
    { \"x\": 16, \"y\": ${16} }, \
    { \"x\": 17, \"y\": ${17} }, \
    { \"x\": 18, \"y\": ${18} }, \
    { \"x\": 19, \"y\": ${19} }, \
    { \"x\": 20, \"y\": ${20} }, \
    { \"x\": 21, \"y\": ${21} }, \
    { \"x\": 22, \"y\": ${22} }, \
    { \"x\": 23, \"y\": ${23} }, \
    { \"x\": 24, \"y\": ${24} } ]"
  curl -d "{ \"auth_token\": \"${AUTH_TOKEN}\", \"${DATA_VIEW}\": ${post_data} }" ${SERVER_CONNECTION}
}

# Pull recent values from file
get_recent_values () {
  value_len="24"
  let i=0
  recent_values=$( tail -n ${value_len} $SESSION_HISTORY_FILE )
  for field in $recent_values; do
    (( i++ ))  
    value[$i]=$field
  done
}

## Main ##

get_sabresessions
get_recent_values

# Call function and pass in array of values
echo "values: ${values[*]}"
update_widget ${value[*]}
