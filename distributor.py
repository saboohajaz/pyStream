'''
Simple RTP video distributor

Written by Stephen Dade (stephen@rpanion.com) for Carbonix
'''

import io
import os
import socket
import subprocess
from os.path import exists
import yaml
import argparse

from flask import Flask, redirect, url_for
from flask import render_template
from flask import request

APP = Flask(__name__)
ISSTREAMING = None

STREAMSETTINGS = {}
# Default settings
STREAMSETTINGS['inPort'] = 5600
STREAMSETTINGS['ipaddress1'] = '127.0.0.1:6000'
STREAMSETTINGS['ipaddress2'] = ''
STREAMSETTINGS['ipaddress3'] = ''
STREAMSETTINGS['ipaddress4'] = ''
STREAMSETTINGS['ipaddress5'] = ''
STREAMSETTINGS['active'] = False

def is_valid_ipv4_address(address):
    '''Returns true if string is a valid IPv4 address'''
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True

def doStream(inport, outip1, outip2, outip3, outip4, outip5):
    global ISSTREAMING
    # kill any zombies
    if ISSTREAMING:
        print("Killing zombie")
        ISSTREAMING.terminate()
    # and start streaming
    outargs = []
    (ip1, port1) = outip1.split(':')
    outargs.append('udpsink')
    outargs.append('host=\"{0}\"'.format(ip1))
    outargs.append('port={0}'.format(port1))
    if outip2 != '':
        (ip2, port2) = outip2.split(':')
        outargs.append('t.')
        outargs.append('!')
        outargs.append('queue')
        outargs.append('!')
        outargs.append('udpsink')
        outargs.append('host=\"{0}\"'.format(ip2))
        outargs.append('port={0}'.format(port2))
    if outip3 != '':
        (ip3, port3) = outip3.split(':')
        outargs.append('t.')
        outargs.append('!')
        outargs.append('queue')
        outargs.append('!')
        outargs.append('udpsink')
        outargs.append('host=\"{0}\"'.format(ip3))
        outargs.append('port={0}'.format(port3))
    if outip4 != '':
        (ip4, port4) = outip4.split(':')
        outargs.append('t.')
        outargs.append('!')
        outargs.append('queue')
        outargs.append('!')
        outargs.append('udpsink')
        outargs.append('host=\"{0}\"'.format(ip4))
        outargs.append('port={0}'.format(port4))
    if outip5 != '':
        (ip5, port5) = outip5.split(':')
        outargs.append('t.')
        outargs.append('!')
        outargs.append('queue')
        outargs.append('!')
        outargs.append('udpsink')
        outargs.append('host=\"{0}\"'.format(ip5))
        outargs.append('port={0}'.format(port5))
    ISSTREAMING = subprocess.Popen(['gst-launch-1.0', 'udpsrc','port='+str(inport), '!', 'application/x-rtp,media=video,clock-rate=90000,encoding-name=H264', '!', 'rtpjitterbuffer', '!', 'tee', 'name=t', 't.', '!', 'queue', '!'] + outargs)
    print(ISSTREAMING.args)
    print("Started Streaming")
    
@APP.route('/', methods=['GET'])
def indexget():
    '''Route index to /distributorget'''
    return redirect(url_for('distributorget'))

@APP.route('/distributor', methods=['GET'])
def distributorget():
    '''Get video streaming settings'''
    global STREAMSETTINGS
    if STREAMSETTINGS['active']:
        #format output url:
        streamaddr = ["gst-launch-1.0 udpsrc port=<PORT> ! application/x-rtp,media=video,clock-rate=90000,encoding-name=H264 ! rtpjitterbuffer ! rtph264depay ! h264parse ! avdec_h264 ! autovideosink sync=false"]
        streammpstring = ["udpsrc port=<PORT> buffer-size=90000 ! application/x-rtp ! rtpjitterbuffer ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! video/x-raw,format=BGRA ! appsink name=outsink sync=false"]
    else:
        streamaddr = ""
        streammpstring = ""
        
    return render_template('distributor.html', status=STREAMSETTINGS['active'],
                           selinPort=STREAMSETTINGS['inPort'],
                           selipaddress1=STREAMSETTINGS['ipaddress1'],
                           selipaddress2=STREAMSETTINGS['ipaddress2'],
                           selipaddress3=STREAMSETTINGS['ipaddress3'],
                           selipaddress4=STREAMSETTINGS['ipaddress4'],
                           selipaddress5=STREAMSETTINGS['ipaddress5'],
                           streamaddr=streamaddr,
                           streammpstring=streammpstring)

@APP.route('/distributorset', methods=['POST'])
def distributorset():
    '''Change video settings'''
    global STREAMSETTINGS
    global ISSTREAMING
    if not STREAMSETTINGS['active']:
        # parse and sanitise the input
        try:
            inport = int(request.form['inPort'])
            assert is_valid_ipv4_address(request.form['ipaddress1'].split(':')[0])
            assert int(request.form['ipaddress1'].split(':')[1]) > 100 and int(request.form['ipaddress1'].split(':')[1]) < 40000
            # other ports are optional
            if request.form['ipaddress2'] != '':
                assert is_valid_ipv4_address(request.form['ipaddress2'].split(':')[0])
                assert int(request.form['ipaddress2'].split(':')[1]) > 100 and int(request.form['ipaddress2'].split(':')[1]) < 40000
            if request.form['ipaddress3'] != '':
                assert is_valid_ipv4_address(request.form['ipaddress3'].split(':')[0])
                assert int(request.form['ipaddress3'].split(':')[1]) > 100 and int(request.form['ipaddress3'].split(':')[1]) < 40000
            if request.form['ipaddress4'] != '':
                assert is_valid_ipv4_address(request.form['ipaddress4'].split(':')[0])
                assert int(request.form['ipaddress4'].split(':')[1]) > 100 and int(request.form['ipaddress4'].split(':')[1]) < 40000
            if request.form['ipaddress5'] != '':
                assert is_valid_ipv4_address(request.form['ipaddress5'].split(':')[0])
                assert int(request.form['ipaddress5'].split(':')[1]) > 100 and int(request.form['ipaddress5'].split(':')[1]) < 40000
        except Exception as e:
            return render_template('errordistributor.html', error=e)
        # save settings
        STREAMSETTINGS['active'] = True
        STREAMSETTINGS['inPort'] = inport
        STREAMSETTINGS['ipaddress1'] = request.form['ipaddress1']
        STREAMSETTINGS['ipaddress2'] = request.form['ipaddress2']
        STREAMSETTINGS['ipaddress3'] = request.form['ipaddress3']
        STREAMSETTINGS['ipaddress4'] = request.form['ipaddress4']
        STREAMSETTINGS['ipaddress5'] = request.form['ipaddress5']
        
        # and start streaming process
        doStream(STREAMSETTINGS['inPort'], STREAMSETTINGS['ipaddress1'], STREAMSETTINGS['ipaddress2'], STREAMSETTINGS['ipaddress3'], STREAMSETTINGS['ipaddress4'], STREAMSETTINGS['ipaddress5'])
    else:
        # stop streaming
        STREAMSETTINGS['active'] = False
        ISSTREAMING.terminate()
        ISSTREAMING = None
    # write settings to file
    with open('settingsDistributor.yaml', 'w') as fileout:
        yaml.dump(STREAMSETTINGS, fileout)
        
    return redirect(url_for('distributorget'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Video Distributor')
    parser.add_argument('--host', type=str, default="127.0.0.1", help='Host IP')

    args = parser.parse_args()

    print("----Starting pyStream Distributor----")
    #open settings file, if it exists
    if os.path.exists('settingsDistributor.yaml'):
        with open('settingsDistributor.yaml', 'r') as filein:
            loadedSTREAMSETTINGS = yaml.safe_load(filein)
            # Sanity check settings first
            badSettings = False
            try:
                if loadedSTREAMSETTINGS['inPort'] < 5000 or loadedSTREAMSETTINGS['inPort'] > 10000:
                    badsettings = True
                if loadedSTREAMSETTINGS['active'] not in [True, False]:
                    badsettings = True
                if not is_valid_ipv4_address(loadedSTREAMSETTINGS['ipaddress1'].split(':')[0]):
                    badsettings = True
                if int(loadedSTREAMSETTINGS['ipaddress1'].split(':')[1]) < 100 or int(loadedSTREAMSETTINGS['ipaddress1'].split(':')[1]) > 40000:
                    badsettings = True
                if loadedSTREAMSETTINGS['ipaddress2'] != '':
                    if not is_valid_ipv4_address(loadedSTREAMSETTINGS['ipaddress2'].split(':')[0]):
                        badsettings = True
                    if int(loadedSTREAMSETTINGS['ipaddress2'].split(':')[1]) < 100 or int(loadedSTREAMSETTINGS['ipaddress2'].split(':')[1]) > 40000:
                        badsettings = True
                if loadedSTREAMSETTINGS['ipaddress3'] != '':
                    if not is_valid_ipv4_address(loadedSTREAMSETTINGS['ipaddress3'].split(':')[0]):
                        badsettings = True
                    if int(loadedSTREAMSETTINGS['ipaddress3'].split(':')[1]) < 100 or int(loadedSTREAMSETTINGS['ipaddress3'].split(':')[1]) > 40000:
                        badsettings = True
                if loadedSTREAMSETTINGS['ipaddress4'] != '':
                    if not is_valid_ipv4_address(loadedSTREAMSETTINGS['ipaddress4'].split(':')[0]):
                        badsettings = True
                    if int(loadedSTREAMSETTINGS['ipaddress4'].split(':')[1]) < 100 or int(loadedSTREAMSETTINGS['ipaddress4'].split(':')[1]) > 40000:
                        badsettings = True
                if loadedSTREAMSETTINGS['ipaddress5'] != '':
                    if not is_valid_ipv4_address(loadedSTREAMSETTINGS['ipaddress5'].split(':')[0]):
                        badsettings = True
                    if int(loadedSTREAMSETTINGS['ipaddress5'].split(':')[1]) < 100 or int(loadedSTREAMSETTINGS['ipaddress5'].split(':')[1]) > 40000:
                        badsettings = True
            except:
                badSettings = True
            if not badSettings:
                STREAMSETTINGS = loadedSTREAMSETTINGS
                print("Loaded settings")
            else:
                print("Bad settings, not loading")
    else:
        print("Reset settings")

    try:
        # start streaming if required
        if STREAMSETTINGS['active']:
            doStream(STREAMSETTINGS['inPort'], STREAMSETTINGS['ipaddress1'], STREAMSETTINGS['ipaddress2'], STREAMSETTINGS['ipaddress3'], STREAMSETTINGS['ipaddress4'], STREAMSETTINGS['ipaddress5'])
        APP.run(use_reloader=False, host=args.host)
    finally:
        # kill any streaming on exit
        if ISSTREAMING:
            ISSTREAMING.terminate()
            print("Stopped streaming")
            
    print("Exiting")
