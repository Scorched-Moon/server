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

# this class handles information for each player

class Player():
    def __init__(self, client, username):
        logging.debug("")
        self.username = username
        self.client = client
        self.energy = 0
        self.channel = "looking_for_game"
        self.team = 0 # team 0 is specifically reserved for players not on a team
        self.dropped = False #whether players client has dropped or not
        self.boottime = 0 #how much time in minutes before dropped player is booted
