#!/bin/sh
sudo mkdir /usr/share/ptimer
sudo cp -rf * /usr/share/ptimer
sudo cp -rf ptimer.desktop /usr/share/applications/.
sudo chmod -R 755 /usr/share/ptimer
sudo chmod a+w /usr/share/ptimer/options/options.json
sudo ln -s /usr/share/ptimer/ptimer.py /usr/bin/ptimer
