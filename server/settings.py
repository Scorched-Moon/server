"""Copyright 2014:
    Kevin Clement

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""

import logging
import os, sys
import string

# this file handles all settings

class Settings():
    def __init__(self):
        logging.debug("")
        self.version = 0.00
        self.settingsversion = 0.1 #oldest version of scorched moon settings file is compatible with remember to update this number when any changes are made to the way settings.conf is read or written to
        self.debug = True
        self.runserver = True
        self.shutdown_command = False
        self.serverport = 6112
        self.loglevel = 4
        self.boottime = -1 #time in seconds to allow a user to reconnect before they get booted completely, -1 means player is never automatically booted


    def load_settings(self):
        logging.debug("")
        logging.info("loading settings from settings.conf")
        if os.path.exists("settings.conf"):
            settingsfile=open("settings.conf", mode="r", encoding="utf-8")
            for line in settingsfile:
                line=line.strip()
                if line == "" or line[0] == "#":
                    continue
                input_array = line.split("=", 1)
                if input_array[0].strip() == "version":
                    if float(input_array[1].strip()) < self.settingsversion: #checking file version to avoid incompatibilities
                        logging.critical("Obsolete settings file detected! aborting startup")
                        logging.critical("Please create new file with -c option")
                        print("Obsolete settings file detected! Aborting startup")
                        print("Please create new file with -c option")
                        sys.exit("Invalid settings") #system ends immediately if it detects file with possibly incompatible settings
                elif input_array[0].strip() == "debug":
                    if input_array[1].strip() == "True":
                        self.debug = True
                elif input_array[0].strip() == "loglevel":
                    self.loglevel = int(input_array[1].strip())
                elif input_array[0].strip() == "serverport":
                    self.serverport = int(input_array[1].strip())
                elif input_array[0].strip() == "boottime":
                    self.boottime = int(input_array[1].strip())
            settingsfile.close()
        else:
            logging.warning("settings.conf file not found, recommend running Scorched Moon with -c option")


    def create_settings(self, version):
        logging.debug("")
        logging.critical("Creating default settings file")
        logging.critical("saving defaults to settings.conf")
        settingsfile=open("settings.conf", mode="w", encoding="utf-8")
        settingsfile.write("version="+str(version)+"\n")
        settingsfile.write("debug="+str(self.debug)+"\n")
        settingsfile.write("loglevel="+str(self.loglevel)+"\n")
        settingsfile.write("serverport="+str(self.serverport)+"\n")
        settingsfile.write("droptime="+str(self.boottime)+"\n")
        settingsfile.close()
        logging.critical("Default settings successfully saved")

