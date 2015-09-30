#!/bin/sh
sudo mkdir /opt/pTimer
sudo cp -rf * /opt/pTimer
sudo chmod -R 755 /opt/pTimer
sudo ln -s /opt/pTimer/pTimer.py /usr/bin/pTimer
