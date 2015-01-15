#!/bin/bash
# @version $Id: push_api_tam_stats.sh 934 2014-12-22 03:27:50Z pete.cornell $
#
# Push Sabre TAM pool usage data to dashing server
#
## Example curl to plot a sequence of data points to graph widget:
# curl -d '{ "AUTH_TOKEN": "mingle#trip", "points": [{ "x" :1, "y" :250 }, { "x" :2, "y" :1120 }, { "x" :3, "y" :822 } ] }' http://dashing/widgets/webconnections

[ $# -ne 2 ] && { echo "usage: $(basename $0) [loginKey] [# of data points to plot]" && exit 1 ;}

LOGINKEY="$1"
DATAPOINTS="$2"
DASHING_SERVER="http://dashing.virginam.com"
AUTH_TOKEN="mingle#trip"
TARGET_WIDGET="sabresessions"
SERVER_CONNECTION="${DASHING_SERVER}/widgets/${TARGET_WIDGET}"
DATA_VIEW="points"
SESSION_HISTORY_FILE="/home/vajobs/bin/dashboards/webstats/jobs/api_tam_stats.history"

get_tam_pool_usage () {
  # Lookup TAM pool usage via api call and append to history file

  connections=$( curl -sL https://www.virginamerica.com/api/v0/session/usage?loginKey=${LOGINKEY} | awk '{print $54}'  )
  echo $connections >> $SESSION_HISTORY_FILE

}

update_widget () {
  # Send data points to dashboard server

  echo "Sending ${#} values to ${TARGET_WIDGET} widget:  ${*}"

  # Build json string
  #
  # The first and last lines of the json string need to be slightly different,
  # hence 3 if statements are used to set the string accordingly
  for (( i = 1; i <= ${value_len}; i++ )); do
    if [ $i -eq 1 ]; then
      post_data+="[ { \"x\": ${i}, \"y\": ${value[i]} }, "
    fi
    if [ $i -gt 1 -a $i -lt ${value_len} ]; then
      post_data+="{ \"x\": ${i}, \"y\": ${value[i]} }, "
    fi
    if [ $i -eq ${value_len} ]; then
      post_data+="{ \"x\": ${i}, \"y\": ${value[i]} } ] "
    fi
  done

  # Push the constructed json string to dashboard server
  curl -d "{ \"auth_token\": \"${AUTH_TOKEN}\", \"${DATA_VIEW}\": ${post_data} }" ${SERVER_CONNECTION}

}

get_values_from_file () {
  # Get values from file

  value_len=$1
  let i=0
  values=$( tail -n ${value_len} $SESSION_HISTORY_FILE )
  for field in $values; do
    (( i++ ))  
    value[$i]=$field
  done

}

## Main ##

get_tam_pool_usage
get_values_from_file ${DATAPOINTS} # Call function with the number of recoreds to read from file

update_widget ${value[*]} # Call function with array of retrieved values
