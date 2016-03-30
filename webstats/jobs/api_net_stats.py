#!/usr/bin/python

'''
Dashing job for graphing open HTTP connections across server farm.
Get network stats from each server.
Get sum and write to file.
Push stats to dashing widget.
'''

import sys
import json
import time
import argparse
import urllib2
import httplib
import paramiko
import os


def parse_args():
    '''Parse command line arguments'''

    parser = argparse.ArgumentParser(
                        description='Count open HTTP connections across '
                        'API server farm and send to Dashing server for display')
    parser.add_argument('-s', help='API servers to collect stats from',
                        required=False, dest='servers')
    parser.add_argument('-d', help='Dashing server to push data to',
                        required=False, dest='dashing_host',
                        default='dashing.virginam.com')
    parser.add_argument('-w', help='Widget to send data to',
                        required=False, dest='widget',
                        default='web_api_netstats')
    parser.add_argument('-n', help='Number of data points to '
                        'send to Dashing server, This will be the nuber of '
                        'values shown on the x-axis of the graph',
                        required=False, dest='num_recs', default=12, type=int)
    parser.add_argument('-a', help='Authentication token for Dashing server',
                        required=False, dest='authtoken')
    parser.add_argument('-l', help='login name used for remote ssh commands',
                        required=True, dest='username')
    parser.add_argument('-i', required=False, dest='identity_file',
                        default="~/.ssh/id_dsa", help='ssh private key file')
    parser.add_argument('-f', help='File where stat history is stored',
                        required=False, dest='historyfile',
                        default=sys.argv[0].strip('py') + "history")
    parser.add_argument('--environment', help='Dashing environment to use, '
                        'either "production" or "development", '
                        'Defaults to production on port 80, '
                        'Development uses port 3030',
                        required=False, dest='dashing_env',
                        default="production")

    args                 = parser.parse_args()
    auth_token           = args.authtoken
    servers              = args.servers.split()
    dashing_host         = args.dashing_host.strip('http://')
    dashing_host         = "http://" + dashing_host
    target_widget        = args.widget
    dashing_env          = args.dashing_env
    num_recs             = args.num_recs
    historyfile          = args.historyfile
    ssh_username         = args.username
    ssh_identity_file    = args.identity_file

    return (auth_token,
        dashing_host,
        target_widget,
        dashing_env,
        num_recs,
        historyfile,
        servers,
        ssh_username,
        ssh_identity_file)


def get_http_connection_count(server, username, identity_file, cmd):
    ##
    print "server, user in loop: ", server, username
    ##
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    privatekeyfile = os.path.expanduser(identity_file)
    ssh_key = paramiko.DSSKey.from_private_key_file(privatekeyfile, password="")

    ssh.load_system_host_keys()
    ssh.connect(server, username=username, key_filename=privatekeyfile, look_for_keys=False)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)

    # Get output of remote ssh command
    http_established_cx = []
    for output in ssh_stdout:
        # http_established_cx = ssh_stdout[6]
        http_established_cx.append(output)

    len_http_established_cx = len(http_established_cx)
    ssh.close()

    return len_http_established_cx


def get_sum_http_established_cx(servers, username, identity_file):

    '''
    Cycle through API servers,
    Retrieve count of open http connections,
    Return the sum.
    '''

    cmd = 'netstat -tna | grep -i 80.*established'

    # Create dict containing servername : connection count
    http_connections = {}
    for server in servers:
        established_cx = get_http_connection_count(server, username, identity_file, cmd)
        http_connections[server] = established_cx

    # Add all values from dict
    http_connections_total = []
    for val in http_connections.values():
        http_connections_total.append(val)

    return sum(http_connections_total)


def save_values(stats, file):

    '''Write sums to file.'''

    # Get timestamp
    now_time = time.strftime("%H:%M")
    now_date = time.strftime("%Y-%m-%d")
    time_stamp = now_date + " " + now_time

    # convert integers to string and strip out parens ()
    stats = str(stats).strip('()') + "\n"
    line = time_stamp + ", " + stats
    f = open(file, 'a')
    f.write(line)
    print "\nWriting value: ", line
    f.close


def tail_history(num_recs, historyfile):

    '''
    * Load entire file into list
    * Put value into list
    * Return tail -n where n is num_recs
    '''

    f = open(historyfile, 'r')

    # skip header
    f.readline()
    lines = f.read().split('\n')
    # Drop empy value from end of list
    lines.pop()

    # Put 3rd element of each line and put into new list
    value_list = [ value.split()[2] for value in lines ]

    # Return slice of the last num_recs
    return value_list[-num_recs:]

    f.close()


def build_json_values(values):
    # Build json string
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
    return json_post_data


def transmit_values(stat_values, target_widget):
    '''Send data to Dashing server via http.'''

    data = '{ "auth_token": "auth_token", "points":' + stat_values + '}'

    print "FOR JSON DATA\n", data

    h = httplib.HTTPConnection('dashing.virginam.com:3030')

    # u = urllib2.urlopen('http://dashing.virginam.com:3030', data)

    h.request('POST', '/widgets/' + target_widget, data)
    r = h.getresponse()
    print r.read()


def main():

    (auth_token,
        dashing_host,
        target_widget,
        dashing_env,
        num_recs,
        historyfile,
        servers,
        ssh_username,
        ssh_identity_file) = parse_args()

    DATA_VIEW   = "points"

    if dashing_env == "production": dashing_http_port = "80"
    if dashing_env == "development": dashing_http_port = "3030"

    server_connection = (dashing_host + ':' +
                         dashing_http_port + '/widgets/' + target_widget)

    ##
    print "\nUsing options:"
    print "auth_token: ", auth_token
    print "dashing server connection: ", server_connection
    print "dashing_http_port: ", dashing_http_port
    print "servers in main: ", servers
    print "num_recs: ", num_recs
    print "historyfile", historyfile
    ##

    # Create log file if it doesn't exist and write header
    HEADER = "# Time, Established Connections"
    with open(historyfile, 'r+') as f:
        line = f.readline()
        if not line.startswith('#'):
            f.write(HEADER + "\n")

    #
    # Call functions
    #

    sum_http_established_cx = get_sum_http_established_cx(servers, ssh_username, ssh_identity_file)
    save_values(sum_http_established_cx, historyfile)
    print tail_history(num_recs, historyfile)
    ##
    sys.exit(0)
    ##


    stat_values = tail_history(num_recs, stat)
    transmit_values(stat_values, target_widget)

if __name__ == '__main__':
    main()
