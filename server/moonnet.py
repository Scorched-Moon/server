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
from .moontools import Tools as tools
from . import player


# this class handles network commands for the server

class NetCommands():
    def __init__(self, selfclient, settings, selfplayer):
        logging.debug("")
        self.client = selfclient
        self.settings = settings
        self.player = selfplayer

    def login(self, client, checkname):
        logging.debug("")
        badlogin = False
        logging.debug("login name = {}" .format(checkname))
        if " " in checkname: # usernames can not have spaces in them
            badlogin = True
            logging.warning("user attempted to login with a space")
        if "channel" in checkname: # user can not be named "all" as this conflicts with chat
            badlogin = True
            logging.warning("user attempted to login as channel")
        if "team" in checkname: # user can not be named "team" as this conflicts with chat
            badlogin = True
            logging.warning("user attempted to login as team")
        for check in self.player: # make certain username has not already been taken
            if check.username == checkname:
                if check.dropped == True and check.client.address == client.address: #reconnect from same address
                    check.dropped = False
                    check.boottime = -1
                    check.client = client                    
                    badlogin = True #not really bad, but not a true login either
                    logging.debug("{} reconnected" .format(checkname))
                    client.send("welcome {}" .format(checkname))
                else:
                    logging.warning("{} tried logging in as {} which is already taken" .format(client.address, checkname))
                    client.send("error username {} already taken" .format(checkname))
                    badlogin = True
        if badlogin == False: # valid login so adding them as a player
            self.player.append(player.Player(client, checkname))
            logging.info("{} logged in from {}" .format(checkname, client.address))
            ID = tools.arrayID(self.player, checkname)
            logging.debug("identified arrayID {}" .format(ID))
            logging.debug("identified username = {}" .format(self.player[ID].username))
            client.send("welcome {}" .format(self.player[ID].username))

    def logout(self, client):
        logging.debug("")
        logging.info("logout command from {}" .format(client.address))
        for remover in self.player:
            if remover.client.address == client.address:
                ID = tools.arrayID(self.player, remover.username)
                logging.debug("Removing username {} with ID {}" .format(remover.username, ID))
                del self.player[ID]

    def broadcast(self, msg):
        logging.debug("")
        logging.info("Broadcast: {}" .format(msg))
        msg = "broadcast " + msg
        for client in self.client:
            client.send(msg)

    def version(self, client):
        logging.debug("")
        client.send("version {}" .format(self.settings.version))

    def whoall(self, client):
        logging.debug("")
        for checkname in self.player:
            ID = tools.arrayID(self.player, checkname.username)
            client.send("whoall {} {} {}" .format(ID, checkname.username, checkname.client.address))
            logging.debug("whoall {} {} {}" .format(ID, checkname.username, checkname.client.address))

    def chat(self, client, unformatted):
        logging.debug("unformatted chat request recieved: {}" .format(unformatted))
        try:
            sender, message = unformatted.split(" ", 1) # seperating sender from message
            recipient, message = message.split(" ", 1) # seperating recipient from message
        except:
            logging.warning("Improperly formatted chat command recieved: {}" .format(unformatted))
        else:
            ID = tools.arrayID(self.player, sender)
            if client.address == self.player[ID].client.address: # confirm that client sending message matches a user logged in from that particular client
                logging.debug("chat request not spoofed")
                logging.debug("searching for recipient: {}" .format(recipient))
                if recipient == "channel": # sending message to everyone in the same channel
                    checklist = 0
                    logging.debug("sending chat to channel: {}" .format(self.player[ID].channel))
                    for players in self.player:
                        if self.player[ID].channel == self.player[checklist].channel:
                            logging.debug("chat {} {} {}" .format(self.player[ID].username, recipient, message))
                            players.client.send("chat {} {} {}" .format(self.player[ID].username, recipient, message))
                            checklist += 1
          
                elif recipient == "team": # sending message to teammates only
                    logging.debug("sending chat to team: {}" .format(self.player[ID].team))
                    if self.player[ID].team != 0: # make certain player trying to team chat is actually on a team
                        checklist = 0
                        for players in self.player:
                            if self.player[ID].team == self.player[checklist].team and ID != checklist: # prevent message from bouncing back to sender
                                logging.debug("chat {} {} {}" .format(self.player[ID].username, recipient, message))
                                players.client.send("chat {} {} {}" .format(self.player[ID].username, recipient, message))
                                checklist += 1
                    else: # silly user tried sending a team message when not on a team
                        client.send("error team chat when not on team")
                        logging.warning("{} sent team chat message when not on team" .format(sender))

                elif recipient == self.player[ID].username: # silly user tried sending a message to himself
                    logging.warning("{} tried sending a message to himself" .format(recipient))
                    client.send("error unable to send messages to yourself")
                else:
                    unfound = True
                    counter = 0
                    for check in self.player: # message isn't to a channel or team so must be to a specific user
                        if recipient == self.player[counter].username:
                            logging.debug("chat {} {} {}" .format(self.player[ID].username, recipient, message))
                            check.client.send("chat {} {} {}" .format(self.player[ID].username, recipient, message))
                            unfound = False
                        else:
                            counter += 1
                    if unfound == True: # no valid user found to send message to
                        logging.warning("{} tried sending message to unknown user {}" .format(self.player[ID].username, recipient))
                        client.send("error unable to send message to {}" .format(recipient))

            else: # someone tried to pretend to be someone else
                client.send("error chatting as invalid user")
                logging.warning("{} attempted to send message as unknown user {}" .format(client.address, sender))
