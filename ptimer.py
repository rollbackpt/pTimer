#!/usr/bin/env python
# Unity indicator for a pomodoro timer
# Author: Joao Ribeiro
# Year: 2015

# TODO: Prevent multiple instances to run
# TODO: Add "Auto Start" to options to change automatically between states when it finishes and improve UI
# TODO: Refactor the code and finish commenting

import time
import signal
import os
import json
from os import popen
from collections import OrderedDict as dict
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify
from gi.repository import GLib as glib


class PomodoroTimer:
    def __init__(self):
        # Create variables
        # See how to define this in a better way
        # (But for now 0 - ReadyToWork, 1 - Working, 2 - ReadyToBreak, 3 - InBreak)
        self.state = 0
        self.read_options_file()
        self.counter_timeout_id = 0
        # Define icons and notifications by state
        self.icon_by_state = {0: 'work_gray', 1: 'work_red', 2: 'break_gray', 3: 'break_green'}
        self.notification_by_state = {1: 'Your work time is over. You should take a break!',
                                      3: 'Your break is over. Ready to get back to work?'}

        self.icons_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons/')

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

    def read_options_file(self):
        try:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "options/options.json")) as data_file:
                data = json.load(data_file)

            self.work_value = int(data["timer"]["work"]) * 60
            self.break_value = int(data["timer"]["break"]) * 60
        except ValueError:
            # In case of any error with the file fall back to the default values
            self.work_value = 40 * 60
            self.break_value = 5 * 60

        if self.state == 0:
            self.timer_value = self.work_value
        elif self.state == 2:
            self.timer_value = self.break_value

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
            self.timer_value = self.break_value
        if self.state == 3:
            self.state = 0
            self.timer_value = self.work_value
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
            popen("canberra-gtk-play --file=" +
                  os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sounds/complete.oga') +
                  " > /dev/null 2>&1 || true")
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

    def options(self, widget):
        self.options = pOptions(self)

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
            menu_items = dict([('Start Working', 'start_counting'),
                               ('Options', 'options'),
                               ('Exit', 'quit')])
        elif self.timer.state == 1:
            menu_items = dict([('Pause', 'pause_counting'),
                               ('Stop Working', 'stop_counting'),
                               ('Options', 'options'),
                               ('Exit', 'quit')])
        elif self.timer.state == 2:
            menu_items = dict([('Start Break', 'start_counting'),
                               ('Options', 'options'),
                               ('Exit', 'quit')])
        elif self.timer.state == 3:
            menu_items = dict([('Pause', 'pause_counting'),
                               ('Stop Break', 'stop_counting'),
                               ('Options', 'options'),
                               ('Exit', 'quit')])

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


class pOptions:
    def __init__(self, timer):
        self.timer = timer

        self.window = gtk.Window()
        self.window.set_position(gtk.WindowPosition.CENTER)
        self.window.set_title("Options")
        self.window.set_size_request(180,120)

        label1 = gtk.Label("Work Time:")
        label2 = gtk.Label("Break Time:")
        self.text1 = gtk.Entry()
        self.text1.set_max_length(4)
        self.text1.set_text(str(self.timer.work_value / 60))
        self.text2 = gtk.Entry()
        self.text2.set_max_length(4)
        self.text2.set_text(str(self.timer.break_value / 60))

        button_save = gtk.Button("Save")
        button_save.set_size_request(150, 10)
        button_save.connect("clicked", self.save)

        fixed = gtk.Fixed()
        fixed.put(label1, 15, 10)
        fixed.put(label2, 15, 45)
        fixed.put(self.text1, 105, 6)
        fixed.put(self.text2, 105, 41)
        fixed.put(button_save, 15, 80)
        self.window.add(fixed)

        self.window.show_all()

    def save(self, widget, data=None):
        if self.text1.get_text().isdigit() and self.text2.get_text().isdigit():
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "options/options.json"), "w") as outfile:
                json.dump({"timer": {"work": self.text1.get_text(), "break": self.text2.get_text()}},
                          outfile,
                          indent=4)
            ''' Read file to reload values and close the window '''
            self.timer.read_options_file()
            self.timer.update_visuals()
            self.window.destroy()
        else:
            self.error_message()

    def error_message(self):
        md = gtk.MessageDialog(self.window,
                               gtk.DialogFlags.MODAL,
                               gtk.MessageType.ERROR,
                               gtk.ButtonsType.CLOSE, "Insert valid values for the work and break time in minutes.")
        md.run()
        md.destroy()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    pTimer = PomodoroTimer()
    pTimer.main()