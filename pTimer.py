#!/usr/bin/env python
# Unity indicator for a pomodoro timer
# Author: João Ribeiro
# Year: 2015

# TODO: Implement options menu for selecting work and break time
# TODO: Add "Auto Start" to options to change automatically between states when it finishes
# TODO: Refactor the code and finish commenting

import time
import signal
import os
from collections import OrderedDict as dict
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
from gi.repository import GLib as glib


class PomodoroTimer:
    def __init__(self):
        # Create variables
        self.default_work_value = 2400
        self.default_break_value = 300
        self.timer_value = self.default_work_value
        self.counter_timeout_id = 0
        # See how to define this in a better way
        # (But for now 0 - ReadyToWork, 1 - Working, 2 - ReadyToBreak, 3 - InBreak)
        self.state = 0
        # Define icons and notifications by state
        self.icon_by_state = {0: 'work_gray', 1: 'work_red', 2: 'break_gray', 3: 'break_green'}
        self.notification_by_state = {1: 'Your work time is over. You should take a break!',
                                      3: 'Your break is over. Ready to get back to work?'}

        self.icons_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons/')

        # Create the Indicator instance
        self.ind = appindicator.Indicator.new_with_path(
                    "pTimer",
                    "work_gray",
                    appindicator.IndicatorCategory.APPLICATION_STATUS,
                    self.icons_path)
        self.ind.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.ind.set_label(self.get_time_string(), "00:00:00")

        # Init notifications
        notify.init('pTimer')

        # Init menu class
        self.menu = PMenu(self)

    def main(self):
        self.menu.generate()
        gtk.main()

    def start_counting(self, widget=None):
        # print "Starting..."
        self.counter_timeout_id = glib.timeout_add(1000, self.count_down)
        self.state += 1
        if self.state > 3:
            self.state = 0
        self.update_visuals()
        self.menu.reload()

    def stop_counting(self, widget=None):
        # print "Stopping..."
        glib.source_remove(self.counter_timeout_id)
        if self.state == 1:
            self.state = 2
            self.timer_value = self.default_break_value
        if self.state == 3:
            self.state = 0
            self.timer_value = self.default_work_value
        self.update_visuals()
        self.menu.reload()

    def pause_counting(self, widget=None):
        if widget.get_label() == 'Pause':
            glib.source_remove(self.counter_timeout_id)
            widget.set_label('Resume')
        elif widget.get_label() == 'Resume':
            self.counter_timeout_id = glib.timeout_add(1000, self.count_down)
            widget.set_label('Pause')

    def count_down(self):
        self.timer_value -= 1
        if self.timer_value > 0:
            self.ind.set_label(self.get_time_string(), '00:00:00')
        else:
            notification = notify.Notification.new("pTimer", self.notification_by_state[self.state], "")
            notification.show()
            self.stop_counting()
        return True

    def get_time_string(self):
        if self.timer_value >= 3600:
            return time.strftime('%H:%M:%S', time.gmtime(self.timer_value))
        else:
            return time.strftime('%M:%S', time.gmtime(self.timer_value))

    def update_visuals(self):
        self.ind.set_label(self.get_time_string(), '00:00:00')
        self.ind.set_icon(self.icon_by_state[self.state])

    @staticmethod
    def quit(widget=None):
        gtk.main_quit()


class PMenu:
    def __init__(self, timer):
        self.timer = timer
        self.menu = gtk.Menu()

    def generate(self):
        # Check if there are something close to switch in python
        if self.timer.state == 0:
            menu_items = dict([('Start Working', 'start_counting'), ('Exit', 'quit')])
        elif self.timer.state == 1:
            menu_items = dict([('Pause', 'pause_counting'), ('Stop Working', 'stop_counting'), ('Exit', 'quit')])
        elif self.timer.state == 2:
            menu_items = dict([('Start Break', 'start_counting'), ('Exit', 'quit')])
        elif self.timer.state == 3:
            menu_items = dict([('Pause', 'pause_counting'), ('Stop Break', 'stop_counting'), ('Exit', 'quit')])

        for key, value in menu_items.iteritems():
            item = gtk.MenuItem()
            item.set_label(key)
            item.connect("activate", getattr(self.timer, value))
            self.menu.append(item)

        self.menu.show_all()
        self.timer.ind.set_menu(self.menu)

    def reload(self):
        for i in self.menu.get_children():
            self.menu.remove(i)
        self.generate()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    pTimer = PomodoroTimer()
    pTimer.main()