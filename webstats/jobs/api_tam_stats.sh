#!/bin/bash
# @version $Id: push_api_tam_stats.sh 934 2014-12-22 03:27:50Z pete.cornell $
#
# Push Sabre TAM pool usage data to dashboard server http://dashing.virginam.com
#
## Example curl to plot a sequence of data points:
# curl -d '{ "AUTH_TOKEN": "mingle#trip", "points": [{ "x" :1, "y" :250 }, { "x" :2, "y" :1120 }, { "x" :3, "y" :822 } ] }' http://dashing/widgets/webconnections
#
# TODO: make loop for post_data

LOGINKEY="$1"
DASHING_SERVER="http://dashing.virginam.com"
AUTH_TOKEN="mingle#trip"
TARGET_WIDGET="sabresessions"
SERVER_CONNECTION="${DASHING_SERVER}/widgets/${TARGET_WIDGET}"
DATA_VIEW="points"
SESSION_HISTORY_FILE="/home/vajobs/bin/dashboards/webstats/jobs/api_tam_stats.history"

# Lookup TAM usage via api call and append to file
get_sabresessions () {
  connections=$( curl -sL https://www.virginamerica.com/api/v0/session/usage?loginKey=${LOGINKEY} | awk '{print $54}'  )
  echo $connections >> $SESSION_HISTORY_FILE
}

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
