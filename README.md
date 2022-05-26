## pyStream

A simple RTSP streamer for the Ras Pi  

### Operating System

Tested using Raspain Bullseye 32bit armhf lite  
[https://downloads.raspberrypi.org/raspios_full_armhf/images/raspios_full_armhf-2022-04-07/](https://downloads.raspberrypi.org/raspios_full_armhf/images/raspios_full_armhf-2022-04-07/2022-04-04-raspios-bullseye-armhf-full.img.xz)

After flashing, created new user pi  
user must be pi and later copy this repo to /home/pi/pyStream  

### Camera configuration
Using camera in **legacy mode**  
change mode using:   
sudo raspi-config   

For Rpi 4 Device tree is already loaded  

#### CM4 with seeedstudio carrier board    
Follow the link: https://wiki.seeedstudio.com/Dual-Gigabit-Ethernet-Carrier-Board-for-Raspberry-Pi-CM4/#dsi-and-csi-connectors-configuration  

Else just copy and paste this:  
> sudo wget https://datasheets.raspberrypi.org/cmio/dt-blob-disp1-cam1.bin -O /boot/dt-blob.bin  

#### CM4 with Waveshare Nano B carrier board  
> sudo apt update  
> sudo apt upgrade  
> sudo apt-get install p7zip-full  
> wget https://www.waveshare.com/w/upload/4/41/CM4_dt_blob.7z  
> 7z x CM4_dt_blob.7z -O./CM4_dt_blob  
> sudo chmod 777 -R CM4_dt_blob  
> cd CM4_dt_blob/  
> sudo cp dt-blob1.bin /boot/dt-blob.bin   
> sudo reboot  

### Packages Reequired
> sudo apt update  
> sudo apt upgrade  
> sudo apt-get install gstreamer1.0-tools libgstreamer1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev  
> sudo apt install -y python3-gst-1.0 libgstrtspserver-1.0-dev python3-pip gstreamer1.0-plugins-good libgstreamer-plugins-base1.0*  
> sudo apt install autoconf automake git vim nano  
> sudo apt install vnstat bmon nload  

### Installing
This assumes that pyStream is located in /home/pi/pyStream  

Run the following commands to install required packages:  
> cd /home/pi/pyStream  
> echo "PATH=\$PATH:~/.local/bin" >> ~/.profile  
> source ~/.profile  
> pip install -r requirements.txt --user  

At this point, first test for debugging purpose
> sudo chmod +x ./run*  
> ./runDebug.sh    

Note: In case runDebug.sh creates execution issue, it is probably it is modifid in windows and have EOL issue.   
Usee this:   
> sed -i -e 's/\r$//' ./runDebug.sh  

Once tested and verified, create a service:  
> sudo cp pystream.service /etc/systemd/system  
> sudo systemctl enable pystream  
> sudo systemctl start pystream  

### Running

Once running, the video streamer will be active at http://<CM4 IP>:5000, where settings can be configured.  
 
The video streamer automatically saves settings and will restore them on reboot.

### Video Receiver sample strings:  
Sample Strings    

#### Mission Planner RTP:
> udpsrc port=5600 ! application/x-rtp,media=video,clock-rate=90000,encoding-name=H264 ! rtpjitterbuffer ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! video/x-raw,format=BGRA ! appsink name=outsink

#### gStreamer:
> gst-launch-1.0 udpsrc port=5600 ! application/x-rtp,media=video,clock-rate=90000,encoding-name=H264 ! rtpjitterbuffer ! rtph264depay ! h264parse ! avdec_h264 ! autovideosink sync=false


