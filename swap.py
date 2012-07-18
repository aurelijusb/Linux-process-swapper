#!/usr/bin/python

'''
Simple GTK+ program to start, stop and terminate processes.

In Linux, paused process are swapped firstly, so memory aggressive
programs can be "hibernated" to Linux Swap and release RAM for other
programs.

Usage:
    Pass path to program as command line parameter or open using
    graphical dialog.

@author Aurelijus Banelis
@license LGPL
@version 1.1.2
'''

import subprocess
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import sys
import os

class Swapper:
    SIGTERM = 15
    SIGCONT = 18
    SIGSTOP = 19
    SECOND = 1000
    PATH_PS = '/bin/ps'
    PATH_KILL = '/bin/kill'

    process = None
    paused = False
    command = None
    recursive = False
    
    #
    # GUI
    #
    
    def __init__(self, command=None):
        if (type(command) is str):
            command = [command]
        self.command = command
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Swapper")
        self.window.connect("delete_event", gtk.main_quit)
        self.window.connect("destroy", gtk.main_quit)

        hbox = gtk.VBox(True, 3)

        self.button_start = gtk.Button("Open")
        self.button_start.connect_object("clicked", self.start, None)
        self.button_start.show()
        hbox.add(self.button_start)

        self.button_pause = gtk.Button("Pause")
        self.button_pause.connect_object("clicked", self.pause, None)
        hbox.add(self.button_pause)
        
        self.button_terminate = gtk.Button("Terminate")
        self.button_terminate.connect_object("clicked", self.terminate,
                                                        None)
        hbox.add(self.button_terminate)
        
        self.label_status = gtk.Label('Not started')
        hbox.add(self.label_status)
        
        hbox.show()
        self.window.add(hbox)
        self.window.show()
        
        self.timer_id = gobject.timeout_add(self.SECOND,
                                            self.update_status)
        self.recursive = os.path.isfile(self.PATH_PS) & os.path.isfile(self.PATH_KILL)
        if (command != None):
            self.start()


    def show_open_dialog(self):
        dialog = gtk.FileChooserDialog(title="Choose program",
                      action=gtk.FILE_CHOOSER_ACTION_OPEN,
                      buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                               gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.command = dialog.get_filename()
        dialog.destroy()

    def show_message(self, string):
        md = gtk.MessageDialog(self.window,
                 gtk.DIALOG_DESTROY_WITH_PARENT,gtk.MESSAGE_ERROR,
                 gtk.BUTTONS_CLOSE, string)
        md.run()
        md.destroy()
        
    def update_status(self):
        if (self.command == None):
            return True
            
        if (self.process != None):
            self.process.poll()
            if (self.process.returncode != None):
                gtk.main_quit()
                return False
                
            if (self.paused):
                self.label_status.set_label('Paused: ' + self.get_name())
            else:
                self.label_status.set_label('Running: ' + self.get_name())
                
        else:
            self.label_status.set_label('Not started');
            
        self.label_status.show()
        return True

    def main(self):
        gtk.main()
    
    #
    # Starting, stopping and terminating processes
    #

    def start(self, widget=None, args=None):
        if (self.command == None):
            self.show_open_dialog()
            
        if (self.command != None):
            if (self.process != None):
                self.continue_process()
            else:
                try:
                    self.process = subprocess.Popen(self.command)
                except OSError:
                    self.process = None
                    self.show_message("Can not open: " + self.get_name())
                    self.command = None
                    return
               
            self.button_start.hide()
            self.button_pause.show()
            self.button_terminate.show()
        
    def continue_process(self):
        if (self.process != None):
            self.process.send_signal(self.SIGCONT)
            self.paused = False
            if (self.recursive):
                for pid in self.get_childs():
                    self.send_signal(pid, self.SIGCONT)
        
    def pause(self, widget=None, args=None):
        self.button_pause.hide()
        self.button_start.set_label('Continue')
        self.button_start.show()
        self.pause_process();
        
    def pause_process(self):
        if (self.process != None):
            self.process.send_signal(self.SIGSTOP)
            self.paused = True
            if (self.recursive):
                for pid in self.get_childs():
                    self.send_signal(pid, self.SIGSTOP)

    def terminate(self, widget=None, args=None):
        if (self.process != None):
            self.process.kill()
            if (self.recursive):
                for pid in self.get_childs():
                    self.send_signal(pid, self.SIGTERM)
            gtk.main_quit()

    def get_name(self):
        return ' '.join(self.command)

    def get_childs(self):
        p = subprocess.Popen(self.PATH_PS + ' --ppid ' +
                       str(self.process.pid), shell=True,
                       stdout=subprocess.PIPE)
        p.stdout.readline()
        subprocesses = [];
        while True:
            inline = p.stdout.readline()
            if not inline:
                break
            subprocesses.append(int(inline.split(' ')[0]));
        return subprocesses
        
    def send_signal(self, pid, signal):
        command = self.PATH_KILL + " -" + str(signal) + " " + str(pid)
        subprocess.call(command, shell=True)
    

#
# Using via command line
#

if __name__ == "__main__":
    if (len(sys.argv) > 1):
        arguments = sys.argv
        del arguments[0]
        swapper = Swapper(arguments)
    else:
        swapper = Swapper()
    swapper.main()
