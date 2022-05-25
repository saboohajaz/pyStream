# pyStream

## Summary

A simple RTSP streamer for the Ras Pi

## Camera configuration

To enable the CSI1 port on the RPi CM4, see https://wiki.seeedstudio.com/Dual-Gigabit-Ethernet-Carrier-Board-for-Raspberry-Pi-CM4/#dsi-and-csi-connectors-configuration

## Installing

Ras Pi OS "Bullseye" must be used, with Legacy camera support ON.

This assumes that pyStream is located in /home/pi/pyStream

Run the following commands to install required packages:

sudo apt install -y python3-gst-1.0 libgstrtspserver-1.0-dev python3-pip gstreamer1.0-plugins-good libgstreamer-plugins-base1.0*
echo "PATH=\$PATH:~/.local/bin" >> ~/.profile
source ~/.profile
pip install -r requirements.txt --user

sudo cp pystream.service /etc/systemd/system
sudo systemctl enable pystream
sudo systemctl start pystream

## Running

Once running, the video streamer will be active at http://<CM4 IP>:5000, where settings can be configured.

The video streamer automatically saves settings and will restore them on reboot.


#mp rtp:
udpsrc port=5600 ! application/x-rtp,media=video,clock-rate=90000,encoding-name=H264 ! rtpjitterbuffer ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! video/x-raw,format=BGRA ! appsink name=outsink

#gst:
gst-launch-1.0 udpsrc port=5600 ! application/x-rtp,media=video,clock-rate=90000,encoding-name=H264 ! rtpjitterbuffer ! rtph264depay ! h264parse ! avdec_h264 ! autovideosink sync=false

# MUST INSTALL
sudo apt-get install gstreamer1.0-tools libgstreamer1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev
sudo apt install -y python3-gst-1.0 libgstrtspserver-1.0-dev python3-pip gstreamer1.0-plugins-good libgstreamer-plugins-base1.0*

sudo apt install autoconf automake git vim nano
sudo apt install vnstat bmon nload


