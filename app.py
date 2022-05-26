'''
Simple RTP video streamer for the Raspberry Pi

Written by Stephen Dade (stephen@rpanion.com) for Carbonix
'''

import io
import os
import socket
import subprocess
from os.path import exists
import yaml

from flask import Flask, redirect, url_for
from flask import render_template
from flask import request

APP = Flask(__name__)
ISSTREAMING = None

STREAMSETTINGS = {}
# Default settings
STREAMSETTINGS['bitrate'] = 200
STREAMSETTINGS['framerate'] = 15
STREAMSETTINGS['active'] = False
STREAMSETTINGS['resolution'] = "640x480"
STREAMSETTINGS['ipaddress'] = "127.0.0.1"
STREAMSETTINGS['mode'] = "RTP"
STREAMSETTINGS['rotation'] = "0"

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

def is_raspberrypi():
    '''Returns true if running on a Pi'''
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

def getTemperature():
    '''Get system temperature in C'''
    completed = subprocess.run(["cat", "/sys/class/thermal/thermal_zone0/temp"],
                               capture_output=True)

    try:
        tmp = int((completed.stdout).strip())/1000
        return round(tmp, 1)
    except:
        return 0

def getCameraDetect():
    '''Confirm camera is detected'''
    completed = subprocess.run(["vcgencmd", "get_camera"],
                               capture_output=True)

    if b'detected=1' in completed.stdout:
        return True
    else:
        return False
        
def doStream(resolution, bitrate, framerate, ipaddress, mode, rotation):
    ''''Execute the streaming process'''
    global ISSTREAMING
    # form up the res arguments
    if resolution == '1920x1080':
        width = '--width=1920'
        height = '--height=1080'
    elif resolution == '1280x720':
        width = '--width=1280'
        height = '--height=720'
    else:
        width = '--width=640'
        height = '--height=480'
    device = '--videosource=/dev/video0'

    # kill any zombies
    if ISSTREAMING:
        print("Killing zombie")
        ISSTREAMING.terminate()
    # and start streaming
    if mode == "RTP":
        ISSTREAMING = subprocess.Popen(['python3', 'rtsp-server.py',
                                        '--fps='+str(framerate),
                                        '--bitrate='+str(bitrate), width, height, device,
                                        '--udp=' + ipaddress + ':5600',
                                        '--rotation=' + rotation])
    else:
        ISSTREAMING = subprocess.Popen(['python3', 'rtsp-server.py',
                                        '--fps='+str(framerate),
                                        '--bitrate='+str(bitrate), width, height, device,
                                        '--rotation=' + rotation])
    print("Started Streaming")

@APP.route('/restart', methods=['POST'])
def restartPi():
    '''Route /restart to restart the system'''
    subprocess.run(["sudo", "reboot", "now"])
    return redirect(url_for('videoget'))

@APP.route('/', methods=['GET'])
def indexget():
    '''Route index to /videoget'''
    return redirect(url_for('videoget'))

@APP.route('/video', methods=['GET'])
def videoget():
    '''Get video streaming settings'''
    global STREAMSETTINGS

    if STREAMSETTINGS['active'] and STREAMSETTINGS['mode'] == "RTP":
        #format output url:
        streamaddr = ["gst-launch-1.0 udpsrc port=5600 ! application/x-rtp,media=video,clock-rate=90000,encoding-name=H264 ! rtpjitterbuffer ! rtph264depay ! h264parse ! avdec_h264 ! autovideosink sync=false"]
        streammpstring = ["udpsrc port=5600 buffer-size=90000 ! application/x-rtp ! rtpjitterbuffer ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! video/x-raw,format=BGRA ! appsink name=outsink sync=false"]
    elif STREAMSETTINGS['active'] and STREAMSETTINGS['mode'] == "RTSP":
        device = 'devvideo0'
        #format output url:
        ip = request.host.split(':')[0]
        streamaddr = ["gst-launch-1.0 rtspsrc location=rtsp://" + ip + ":8554/" + device + " latency=0 is-live=True ! queue ! decodebin ! autovideosink"]
        streammpstring = ["rtspsrc location=rtsp://" + ip + ":8554/" + device + " latency=0 is-live=True ! queue ! application/x-rtp ! rtph264depay ! avdec_h264 ! videoconvert ! video/x-raw,format=BGRA ! appsink name=outsink"]
    else:
        streamaddr = ""
        streammpstring = ""

    if is_raspberrypi() and getCameraDetect():
        camString = "CSI Camera Detected"
    elif is_raspberrypi() and not getCameraDetect():
        camString = "CSI Camera NOT Detected"
    else:
        camString = "Not running on Raspberry Pi"
        
    return render_template('index.html', status=STREAMSETTINGS['active'],
                           selframerate=STREAMSETTINGS['framerate'],
                           selbitrate=STREAMSETTINGS['bitrate'],
                           selres=STREAMSETTINGS['resolution'],
                           selmode=STREAMSETTINGS['mode'],
                           streamaddr=streamaddr,
                           streammpstring=streammpstring,
                           selipaddress=STREAMSETTINGS['ipaddress'],
                           tempC=getTemperature(),
                           cameraDetect=camString,
                           selrot=STREAMSETTINGS['rotation'])

@APP.route('/videoset', methods=['POST'])
def videopost():
    '''Change video settings'''
    global STREAMSETTINGS
    global ISSTREAMING
    print(STREAMSETTINGS)

    if not STREAMSETTINGS['active']:
        # parse and sanitise the input
        try:
            framerate = int(request.form['framerate'])
            bitrate = int(request.form['bitrate'])
            assert request.form['resolution'] in ['1920x1080', '1280x720', '640x480']
            assert request.form['rotation'] in ['0', '90', '180', '270']
            assert request.form['mode'] in ['RTP', 'RTSP']
            assert framerate < 26
            assert framerate > 4
            assert bitrate < 10001
            assert bitrate > 49
            if request.form['mode'] == 'RTP':
                assert is_valid_ipv4_address(request.form['ipaddress'])
        except Exception as e:
            return render_template('error.html', error=e)

        doStream(request.form['resolution'], bitrate, framerate, request.form['ipaddress'], request.form['mode'], request.form['rotation'])

        STREAMSETTINGS['bitrate'] = bitrate
        STREAMSETTINGS['mode'] = request.form['mode']
        STREAMSETTINGS['framerate'] = framerate
        STREAMSETTINGS['active'] = True
        STREAMSETTINGS['resolution'] = request.form['resolution']
        STREAMSETTINGS['rotation'] = request.form['rotation']
        STREAMSETTINGS['ipaddress'] = request.form['ipaddress']
        with open('settings.yaml', 'w') as fileout:
            yaml.dump(STREAMSETTINGS, fileout)
    else:
        # Stop streaming
        print("Stopped Streaming")
        ISSTREAMING.terminate()
        ISSTREAMING = None
        STREAMSETTINGS['active'] = False
        with open('settings.yaml', 'w') as filein:
            yaml.dump(STREAMSETTINGS, filein)

    return redirect(url_for('videoget'))

if __name__ == "__main__":
    print("----Starting pyStream----")
    #open settings file, if it exists
    if os.path.exists('settings.yaml'):
        with open('settings.yaml', 'r') as filein:
            loadedSTREAMSETTINGS = yaml.safe_load(filein)
            # Sanity check settings first
            badSettings = False
            try:
                if loadedSTREAMSETTINGS['bitrate'] < 50 or loadedSTREAMSETTINGS['bitrate'] > 10000:
                    badSettings = True
                if loadedSTREAMSETTINGS['framerate'] < 5 or loadedSTREAMSETTINGS['framerate'] > 25:
                    badsettings = True
                if loadedSTREAMSETTINGS['active'] not in [True, False]:
                    badsettings = True
                if loadedSTREAMSETTINGS['resolution'] not in ['1920x1080', '1280x720', '640x480']:
                    badsettings = True
                if loadedSTREAMSETTINGS['mode'] not in ['RTP', 'RTSP']:
                    badsettings = True
                if loadedSTREAMSETTINGS['mode'] == "RTP" and not is_valid_ipv4_address(loadedSTREAMSETTINGS['ipaddress']):
                    badsettings = True
                if loadedSTREAMSETTINGS['rotation'] not in ['0', '90', '180', '270']:
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
            doStream(STREAMSETTINGS['resolution'],
                     STREAMSETTINGS['bitrate'],
                     STREAMSETTINGS['framerate'],
                     STREAMSETTINGS['ipaddress'],
                     STREAMSETTINGS['mode'],
                     STREAMSETTINGS['rotation'])

        APP.run(use_reloader=False, host='0.0.0.0')
    finally:
        # kill any streaming on exit
        if ISSTREAMING:
            ISSTREAMING.terminate()
            print("Stopped streaming")

    print("Exiting")
