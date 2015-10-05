#!/bin/sh
sudo mkdir /opt/pTimer
sudo cp -rf * /opt/pTimer
sudo cp -rf pTimer.desktop /usr/share/applications/.
sudo chmod -R 755 /opt/pTimer
sudo chmod a+w /opt/pTimer/options/options.json
sudo ln -s /opt/pTimer/pTimer.py /usr/bin/pTimer
