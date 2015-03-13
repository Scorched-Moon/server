"""Copyright 2015:
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

import sys
import logging
import time
import platform
from .miniboa import TelnetServer
from .moontools import Tools as tools
from . import moonnet
from . import player
from . import settings


#the main server class that handles everything

class Main: #the main server class
    def __init__(self, debug, loglevel, makesettings, settingpath):

        version = 0.1 # server version number

        # breaking up sessions in logfile
        logging.basicConfig(filename='logs/scorched_moon_server.log',level=logging.DEBUG,format='%(message)s')
        logging.critical("----------------------------------------------------------------------------------------------------------------------------")
        logging.critical("----------------------------------------------------------------------------------------------------------------------------")

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler) # clears out handler to prepare for next logging session

        logging.basicConfig(filename='logs/scorched_moon_server.log',level=logging.ERROR,format='%(levelname)s - %(asctime)s -- %(message)s') #default logging configuration until we can load custom settings

        if makesettings == True:
            logging.critical("Scorched Moon server creating default settings.conf file")
            settings.Settings.create_settings(settings.Settings(), version)
            logging.critical("Scorched Moon Server shutting down to allow settings.conf file to be edited")
            print("Default settings.conf file created, please edit settings and launch Scorched Moon again")
            print("Scorched Moon server has been successfully shutdown")
            sys.exit()

        logging.critical("Starting Scorched Moon Server")
        print("Starting Scorched Moon server")

        self.settings = settings.Settings() #initalizaing settings
        self.settings.version = version
        self.settings.load_settings() #loading custom settings from file

        if loglevel != 0: #arguments override settings file for logging
            self.settings.loglevel = loglevel
        else: # loglevel 0 means no argument used so we go with settings file
            loglevel = self.settings.loglevel

        if debug == True: # arguments override settings file for debug
            self.settings.debug = True

        if self.settings.debug == True: #debug overrides loglevels
            loglevel = 1

        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler) # clears out handler again so we can use custom logging settings
        
        if loglevel == 1:
            logging.basicConfig(filename='logs/scorched_moon_server.log',level=logging.DEBUG,format='%(levelname)s - %(asctime)s - %(module)s:%(funcName)s:%(lineno)s -- %(message)s')
        elif loglevel == 2:
            logging.basicConfig(filename='logs/scorched_moon_server.log',level=logging.INFO,format='%(levelname)s - %(asctime)s -- %(message)s')
        elif loglevel == 3:
            logging.basicConfig(filename='logs/scorched_moon_server.log',level=logging.WARNING,format='%(levelname)s - %(asctime)s -- %(message)s')
        elif loglevel == 4:
            logging.basicConfig(filename='logs/scorched_moon_server.log',level=logging.ERROR,format='%(levelname)s - %(asctime)s -- %(message)s')
        elif loglevel == 5:
            logging.basicConfig(filename='logs/scorched_moon_server.log',level=logging.CRITICAL,format='%(levelname)s - %(asctime)s -- %(message)s')
        else: #invalid loglevel
            print("Invalid loglevel {}" .format(loglevel))
            print("Unable to start logging")
            print("Invalid settings detected! Aborting startup")
            print("Please correct settings file or create new file with -C option")
            sys.exit()

        # confirming startup status and logging
        if self.settings.debug:
            print("Scorched Moon server ver. {} successfully started in debug mode" .format(version))
            print("Logging level forced to 1")
            logging.critical("Scorched Moon server ver. {} successfully started in debug mode" .format(version))
            logging.critical("Log level forced to {}" .format(loglevel))
        else:
            print("Scorched Moon server ver. {} successfully started" .format(version))
            print("Logging level set to {}" .format(loglevel))
            logging.critical("Scorched Moon server ver. {} successfully started" .format(version))
            logging.critical("Log level is set to {}" .format(loglevel))

        logging.critical("Platform: {}" .format(platform.platform()))
        logging.critical("Python version: {}" .format(sys.version))

        # setting globals
        self.player = [] # a list of player classes
        self.game = [] # a list of game classes
        self.clientlist = [] # a list of all connected clients
        netcommand = moonnet.NetCommands(self.clientlist, self.settings, self.player)


        def process_clients(): #handles commands client has sent to server
            for client in self.clientlist:
                if client.active and client.cmd_ready:
                    total_cmd = client.get_command()
                    logging.debug("processing raw command: {}" .format(total_cmd))
                    if total_cmd.find(" ") != -1: # seperating any variables from the actual command
                        cmd, cmd_var = total_cmd.split(" ", 1)
                    else:
                        cmd = total_cmd
                        cmd_var = ""
                    if cmd == "exit": #command to disconnect client
                        logging.info("{} disconnected intentionally" .format(client.address))
                        client.send("goodbye")
                        self.server.poll()
                        client.active = False
                    elif cmd == "shutdown": #command to shutdown entire server
                        logging.info("Shutdown command recieved by {}" .format(client.address))
                        self.settings.shutdown_command = True
                    elif cmd == "broadcast": #command to send message to all clients
                        netcommand.broadcast(cmd_var)
                    elif cmd == "version": # command to provide the server version
                        netcommand.version(client)
                    elif cmd == "login": # command to log in username and recognize them as an actual player
                        netcommand.login(client, cmd_var)
                    elif cmd == "logout": # command to logout username
                        netcommand.logout(client)
                    elif cmd == "whoall": # command to list all connected users
                        netcommand.whoall(client)
                    elif cmd == "chat": # standard chat message
                        netcommand.chat(client, cmd_var)
                    elif cmd == "test":
                        logging.critical("test command received")
                        print("test!")
                    else:
                        logging.debug("recieved unidentified command: {}" .format(cmd))
                        client.send("error unknown command \"{}\"" .format(cmd))

        def client_connects(client): #called when a client first connects
            self.clientlist.append(client) 
            client.send("hello")
            logging.info("{} connected to server" .format(client.address))
            netcommand.version(client)

        def client_disconnects(client): #called when a client drops on it's own without exit command
            logging.info("{} dropped" .format(client.address))
            self.clientlist.remove(client)
            for checkplayer in self.player:
                if checkplayer.client == client:
                    checkplayer.dropped = True
                    if self.settings.boottime > -1: #checking to see if player gets booted or not 
                        checkplayer.boottime = time.time() + self.settings.boottime
                        logging.debug("Marking {} as dropped, booting at: {}" .format(checkplayer.username, checkplayer.boottime))
                    else:
                        logging.debug("System set to never boot dropped player")

        logging.debug("Starting Telnet server")
        self.server = TelnetServer(port=self.settings.serverport, on_connect=client_connects, on_disconnect=client_disconnects) #starts server
        logging.debug("Telnet Server started on port {}" .format(self.settings.serverport))

        ## Server Loop
        while self.settings.runserver:
            self.server.poll()        # Send, Recv, and look for new connections
            process_clients()           # Check for client input
            if self.settings.boottime > -1: #never boot if boottime is < 0
                for player in self.player:
                    if player.dropped == True and player.boottime < time.time(): #check if dropped players need to be booted
                        ID = tools.arrayID(self.player, player.username)
                        logging.info("Booting username {} due to disconnect timeout" .format(player.username))
                        del self.player[ID]
            if self.settings.shutdown_command == True:
                netcommand.broadcast("Server is being intentionally shutdown, Disconnecting all users")
                self.server.poll()
                for client in self.clientlist: # disconnecting clients before shutdown
                    logging.debug("goodbye {}" .format(client.address))
                    client.send("disconnecting")
                    self.server.poll()
                    client.active = False
                self.settings.runserver = False

        logging.critical("Scorched Moon server successfully shutdown")
        logging.shutdown()
        print("Scorched Moon server has been successfully shutdown") 
        sys.exit(0) # final shutdown confirmation
