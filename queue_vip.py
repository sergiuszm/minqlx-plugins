# This is an extension plugin  for minqlx.
# Copyright (C) 2018 sergiuszm (github) aka SerchioQ (ql)
# Copyright (C) 2016 mattiZed (github) aka mattiZed (ql)
# Copyright (C) 2016 Melodeiro (github)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# This is a queue plugin written for Mino's Quake Live Server Mod minqlx.
# Some parts of it were inspired by the original queueinfo plugin which was
# written by WalkerX (github) for the old minqlbot.

# The plugin put players to the queue when teams are full or even if match in progress.
# When more players adding or there is the place for someone, guys from queue putting to the game.

# The plugin also features an AFK list, to which players can
# subscribe/unsubscribe to.

# Its the alpha state, so any bugs might happen

# For correctly updating the player tags after using !clan, server needs changed clan.py:
# https://github.com/Melodeiro/minqlx-plugins_MinoMino/blob/master/clan.py
# Also you can use the updated version of uneventeams.py, which will put players in queue:
# https://github.com/Melodeiro/minqlx-plugins_mattiZed/blob/master/uneventeams.py

import minqlx
import time
import threading
import logging
from logging.handlers import RotatingFileHandler
import datetime
import sys
import os
import os.path
import operator

TEAM_BASED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm", "ad", "1f", "har")
NONTEAM_BASED_GAMETYPES = ("ffa", "race", "rr")
_tag_key = "minqlx:players:{}:clantag"
_extended_vip_key = "minqlx:servers:{}:extended_vip"

class queue_vip(minqlx.Plugin):
    def __init__(self):
        self.add_hook("new_game", self.handle_new_game)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("team_switch", self.handle_team_switch)
        self.add_hook("team_switch_attempt", self.handle_team_switch_attempt)
        self.add_hook("set_configstring", self.handle_configstring, priority=minqlx.PRI_HIGH)
        self.add_hook("client_command", self.handle_client_command)
        self.add_hook("vote_ended", self.handle_vote_ended)
        self.add_hook("console_print", self.handle_console_print)
        self.add_command(("q", "queue"), self.cmd_lq)
        self.add_command("afk", self.cmd_afk)
        self.add_command("here", self.cmd_playing)
        self.add_command("qversion", self.cmd_qversion)
        self.add_command(("teamsize", "ts"), self.cmd_teamsize, priority=minqlx.PRI_HIGH)

        # Commands for debugging
        self.add_command("qpush", self.cmd_qpush, 5)
        self.add_command("qadd", self.cmd_qadd, 5, usage="<id>")
        self.add_command("qupd", self.cmd_qupd, 5)

        self.version = "1.0"
        self._queue = []
        self._vip_queue = []
        self._afk = []
        self._tags = {}
        self.initialize()
        self.is_red_locked = False
        self.is_blue_locked = False
        self.is_push_pending = False
        self.is_endscreen = False  ######## TODO: replace for something better, because
        ######## loading during the endgame screen might cause bugs
        self.set_cvar_once("qlx_queueSetAfkPermission", "2")
        self.set_cvar_once("qlx_queueAFKTag", "^3AFK")
        self.game_port = minqlx.get_cvar("net_port")
        self.jointimes = {}
        self._extended_vip = self.check_if_extended_vip()

        self.test_logger = minqlx.get_logger()
        self.qlogger = self._configure_logger()

    def initialize(self):
        for p in self.players():
            self.updTag(p)
        self.unlock()

    def check_if_extended_vip(self):
        try:
            extended_vip = bool(self.db[_extended_vip_key.format(self.game_port)])

            if extended_vip:
                return extended_vip

        except KeyError as e:
            extended_vip = False

        return extended_vip

    ## Basic List Handling (Queue and AFK)
    @minqlx.thread
    def addToQueue(self, player, pos=-1):
        '''Safely adds players to the queue'''
        if player not in self._vip_queue and player not in self._queue:
            if pos == -1:
                self._vip_queue.append(player) if player.vip else self._queue.append(player)
            else:
                if player.vip:
                    self._vip_queue.insert(pos, player)
                    for p in self._vip_queue:
                        self.updTag(p)
                else:
                    self._queue.insert(pos, player)
                    for p in self._queue:
                        self.updTag(p)

            for p in self.teams()['spectator']:
                self.center_print(p, "{} joined the VIP Queue".format(player.name)) \
                    if player.vip else self.center_print(p, "{} joined the Queue".format(player.name))
        if player in self._queue:
            self.center_print(player, "You are in the queue to play")
        elif player in self._vip_queue:
            self.center_print(player, "You are in the VIP queue to play")
        self.updTag(player)
        self.pushFromQueue()

    def remFromQueue(self, player, update=True):
        '''Safely removes player from the queue'''
        if player in self._vip_queue:
            self._vip_queue.remove(player)
        elif player in self._queue:
            # self.test_logger.warning("removing {} from queue".format(player))
            self._queue.remove(player)

        for p in self._vip_queue:
            self.updTag(p)
        for p in self._queue:
            self.updTag(p)
        if update:
            self.updTag(player)

    @minqlx.thread
    def pushFromQueue(self, delay=0):
        '''Check if there is the place and players in queue, and put them in the game'''

        @minqlx.next_frame
        def pushToTeam(amount, team):
            '''Safely put certain amout of players to the selected team'''

            pushToTeam.remaining = amount
            self.qlogger.debug("pushToTeam.remaining = {}".format(amount))

            def popFromQueue(queue):
                if pushToTeam.remaining == 0:
                    self.qlogger.debug("pushToTeam.remaining = 0")
                    self.pushFromQueue(0.5)
                    return

                self.qlogger.debug("pushToTeam.remaining = {}".format(pushToTeam.remaining))
                for count, player in enumerate(queue, start=1):
                    self.qlogger.debug("{}: Player: {}, IS_VIP: {}".format(count, player.name, player.vip))
                    if player in self.teams()['spectator'] and player.connection_state == 'active':
                        self.qlogger.debug("{}: Player: {}, from spectator to {}".format(count, player.name, team))
                        # self.test_logger.warning("pop out {}".format(player))
                        queue.pop(0).put(team)
                        pushToTeam.remaining -= 1
                    elif player.connection_state not in ['connected', 'primed']:
                        self.remFromQueue(player)
                    if pushToTeam.remaining == 0:
                        self.pushFromQueue(0.5)
                        return

            if not self.is_endscreen:
                self.qlogger.debug("pushFromQueue -> vip")
                popFromQueue(self._vip_queue)
                self.qlogger.debug("pushFromQueue -> normal")
                popFromQueue(self._queue)

        @minqlx.next_frame
        def pushToBoth():
            self.qlogger.debug("pushToTeam: 1, red")
            pushToTeam(1, "red")
            self.qlogger.debug("pushToTeam: 1, blue")
            pushToTeam(1, "blue")

        @minqlx.next_frame
        def checkForPlace():
            maxplayers = self.get_maxplayers()
            teams = self.teams()
            red_amount = len(teams["red"])
            blue_amount = len(teams["blue"])
            free_amount = len(teams["free"])
            spec_amount = len(teams['spectator'])

            self.qlogger.debug("------------------ checkForPlace ------------------ ")
            self.qlogger.debug("MAXPLAYERS: {}".format(maxplayers))
            self.qlogger.debug("RED: {}, BLUE: {}, FREE: {}, SPEC: {}".format(
                red_amount, blue_amount, free_amount, spec_amount))
            # self.msg("DEBUG max:{} ts:{} red:{} blue{} free:{}".format(maxplayers, self.game.teamsize, red_amount, blue_amount, free_amount))

            if self.game.type_short in TEAM_BASED_GAMETYPES:
                diff = red_amount - blue_amount
                self.qlogger.debug("red - blue: {}".format(diff))
                if diff > 0 and not self.is_blue_locked:
                    self.qlogger.debug("Push to BLUE: {}".format(diff))
                    pushToTeam(diff, "blue")
                elif diff < 0 and not self.is_red_locked:
                    self.qlogger.debug("Push to RED: {}".format(-diff))
                    pushToTeam(-diff, "red")
                elif red_amount + blue_amount < maxplayers:
                    self.qlogger.debug("Red + Blue < Maxplayers")
                    self.qlogger.debug("RED: {}, BLUE: {}, MAXPLAYERS: {}, FREE: {}, SPEC: {}, QVIP: {}, QN: {}".format(
                        red_amount, blue_amount, maxplayers, free_amount, spec_amount, len(self._vip_queue), len(self._queue)
                    ))
                    if ((len(self._queue) + len(self._vip_queue)) > 1) and not self.is_blue_locked and not self.is_red_locked:
                        self.qlogger.debug("(len(self._queue) > 1 or len(self._vip_queue) > 1): pushToBoth()")
                        pushToBoth()  ################ add elo here for those, who want
                    elif self.game.state == 'warmup':  # for the case if there is 1 player in queue
                        self.qlogger.debug("PUSH on WARMUP to: ")
                        if not self.is_red_locked and red_amount < int(self.game.teamsize):
                            self.qlogger.debug("RED")
                            pushToTeam(1, "red")
                        elif not self.is_blue_locked and blue_amount < int(self.game.teamsize):
                            self.qlogger.debug("BLUE")
                            pushToTeam(1, "blue")

            elif self.game.type_short in NONTEAM_BASED_GAMETYPES:
                if free_amount < maxplayers:
                    pushToTeam(maxplayers - free_amount, "free")

        if self.is_push_pending:
            return
        self.is_push_pending = True
        time.sleep(delay)
        self.is_push_pending = False

        if len(self._vip_queue) > 0 and self.game.state == 'warmup' and self._extended_vip:
            for p in self._vip_queue:
                youngest_player = max(self.jointimes, key=lambda key: self.jointimes[key])
                
        if len(self._vip_queue) == 0 and len(self._queue) == 0:
            return
        if self.game.state != 'in_progress' and self.game.state != 'warmup':
            return
        if self.is_endscreen:
            return

        checkForPlace()

    @minqlx.thread
    def remAFK(self, player, update=True):
        '''Safely removes players from afk list'''
        if player in self._afk:
            self._afk.remove(player)
            if update:
                self.updTag(player)

    def posInQueue(self, player):
        '''Returns position of the player in queue'''
        try:
            return self._vip_queue.index(player) if player.vip else self._queue.index(player)
        except ValueError:
            return -1

    ## AFK Handling
    def setAFK(self, player):
        '''Returns True if player's state could be set to AFK'''
        if player in self.teams()['spectator'] and player not in self._afk:
            self._afk.append(player)
            self.remFromQueue(player)
            return True
        return False

    @minqlx.thread
    def remTag(self, player):
        if player.steam_id in self._tags:
            del self._tags[player.steam_id]

    # @minqlx.thread
    def updTag(self, player):
        '''Update the tags dictionary and start the set_configstring event for tag to apply'''

        @minqlx.next_frame
        def upd():
            if player in self.players():
                player.clan = player.clan

        if player in self.players():
            addition = ""
            position = self.posInQueue(player)
            # self.qlogger.debug("TEST")
            # self.qlogger.debug("POS IN {}_QUEUE: {}".format("VIP" if player.vip else "NORMAL", position + 1))

            if position > -1:
                addition = 'V({})'.format(position + 1) if player.vip else '({})'.format(position + 1)
            elif player in self._afk:
                addition = '({})'.format(self.get_cvar("qlx_queueAFKTag"))
            elif self.game.type_short not in TEAM_BASED_GAMETYPES + NONTEAM_BASED_GAMETYPES:
                addition = ""
            elif player in self.teams()['spectator']:
                addition = '(s)'

            self._tags[player.steam_id] = addition

            upd()

    @minqlx.next_frame
    def center_print(self, player, message):
        if player in self.players():
            minqlx.send_server_command(player.id, "cp \"{}\"".format(message))

    def get_maxplayers(self):
        maxplayers = int(self.game.teamsize)
        if self.game.type_short in TEAM_BASED_GAMETYPES:
            maxplayers = maxplayers * 2
        if maxplayers == 0:
            maxplayers = minqlx.get_cvar("sv_maxClients", int)
        return maxplayers

    ## Plugin Handles and Commands
    def handle_player_disconnect(self, player, reason):
        if player.steam_id in self.jointimes:
            del self.jointimes[player.steam_id]
        self.remAFK(player, False)
        self.remFromQueue(player, False)
        self.remTag(player)
        self.pushFromQueue(0.5)

    def handle_player_loaded(self, player):
        self.qlogger.debug("Player loaded: {}".format(player.name))
        if not player.vip:
            self.jointimes[player.steam_id] = time.time()
        self.updTag(player)

    def handle_team_switch(self, player, old_team, new_team):
        self.qlogger.debug("handle_team_switch")
        if new_team != "spectator":
            self.qlogger.debug("new_team != spectator")
            self.remFromQueue(player)
            self.remAFK(player)
        else:
            self.qlogger.debug("new_team == spectator")
            self.updTag(player)
            self.pushFromQueue(0.5)

    def handle_team_switch_attempt(self, player, old_team, new_team):
        if self.game.type_short not in TEAM_BASED_GAMETYPES + NONTEAM_BASED_GAMETYPES:
            return

        if new_team != "spectator" and old_team == "spectator":
            teams = self.teams()
            maxplayers = self.get_maxplayers()
            if len(teams["red"]) + len(teams["blue"]) == maxplayers or len(
                    teams["free"]) == maxplayers or self.game.state == 'in_progress' or len(
                    self._queue) > 0 or len(self._vip_queue) > 0 or self.is_red_locked or self.is_blue_locked:
                self.remAFK(player)
                self.addToQueue(player)
                return minqlx.RET_STOP_ALL

    def cmd_qpush(self, player, msg, channel):
        self.pushFromQueue()

    def cmd_qadd(self, player, msg, channel):
        if len(msg) < 2:
            self.addToQueue(player)

        try:
            i = int(msg[1])
            target_player = self.player(i)
            if not (0 <= i < 64) or not target_player:
                raise ValueError
        except ValueError:
            channel.reply("Invalid ID.")
            return

        self.addToQueue(target_player)

    def cmd_qupd(self, player, msg, channel):
        for p in self.players():
            self.updTag(p)

    def cmd_qversion(self, player, msg, channel):
        channel.reply('^7This server has installed ^2vip_queue.py {} ^7ver. by ^1S^7er^1ch^7io^Q'.format(self.version))

    def handle_client_command(self, player, command):
        @minqlx.thread
        def handler():
            if command == "team s":
                if player in self.teams()['spectator']:
                    self.remFromQueue(player)
                    if player not in self._queue and player not in self._vip_queue:
                        self.center_print(player, "You are set to spectate only")

        handler()

    def handle_vote_ended(self, votes, vote, args, passed):
        if vote == "teamsize":
            self.pushFromQueue(4)

    def handle_configstring(self, index, value):
        if not value:
            return

        elif 529 <= index < 529 + 64:
            try:
                player = self.player(index - 529)
            except minqlx.NonexistentPlayerError:
                return

            if player.steam_id in self._tags:
                tag = self._tags[player.steam_id]

                tag_key = _tag_key.format(player.steam_id)
                if tag_key in self.db:
                    if len(tag) > 0:
                        tag += ' '
                    tag += self.db[tag_key]

                cs = minqlx.parse_variables(value, ordered=True)
                cs["xcn"] = tag
                cs["cn"] = tag
                new_cs = "".join(["\\{}\\{}".format(key, cs[key]) for key in cs])
                return new_cs

    def handle_new_game(self):
        self.is_endscreen = False
        self.is_red_locked = False
        self.is_blue_locked = False

        if self.game.type_short not in TEAM_BASED_GAMETYPES + NONTEAM_BASED_GAMETYPES:
            # self.test_logger.warning("Emptying queue")
            self._queue = []
            self._vip_queue = []
            for p in self.players():
                self.updTag(p)
        else:
            self.pushFromQueue()

    def handle_game_end(self, data):
        self.is_endscreen = True

    def cmd_lq(self, player, msg, channel):
        self.qlogger.debug("cmd_lq")
        msg = "^7No one in VIP queue and standard queue."
        if self._vip_queue:
            msg = "^4VIP ^1Queue^7 >> "
            for count, p in enumerate(self._vip_queue, start=1):
                msg += '{}^7({}) '.format(p.name, count)
            channel.reply(msg)
            msg = ""

        if self._queue:
            msg = "^1Queue^7 >> "
            for count, p in enumerate(self._queue, start=1):
                msg += '{}^7({}) '.format(p.name, count)

        if len(msg) > 0:
            channel.reply(msg)

        if self._afk:
            msg = "^3Away^7 >> "
            for p in self._afk:
                msg += p.name + " "

            channel.reply(msg)

    def cmd_afk(self, player, msg, channel):
        if len(msg) > 1:
            if self.db.has_permission(player, self.get_cvar("qlx_queueSetAfkPermission", int)):
                guy = self.find_player(msg[1])[0]
                if self.setAFK(guy):
                    player.tell("^7Status for {} has been set to ^3AFK^7.".format(guy.name))
                    return minqlx.RET_STOP_ALL
                else:
                    player.tell("Couldn't set status for {} to AFK.".format(guy.name))
                    return minqlx.RET_STOP_ALL
        if self.setAFK(player):
            player.tell("^7Your status has been set to ^3AFK^7.")
        else:
            player.tell("^7Couldn't set your status to AFK.")

    def cmd_playing(self, player, msg, channel):
        self.remAFK(player)
        self.updTag(player)
        player.tell("^7Your status has been set to ^2AVAILABLE^7.")

    def cmd_teamsize(self, playing, msg, channel):
        self.pushFromQueue(0.5)

    def handle_console_print(self, text):
        if text.find('broadcast: print "The RED team is now locked') != -1:
            self.is_red_locked = True
        elif text.find('broadcast: print "The BLUE team is now locked') != -1:
            self.is_blue_locked = True
        elif text.find('broadcast: print "The RED team is now unlocked') != -1:
            self.is_red_locked = False
            self.pushFromQueue(0.5)  ################ if cause errors maybe call that in next_frame
        elif text.find('broadcast: print "The BLUE team is now unlocked') != -1:
            self.is_blue_locked = False
            self.pushFromQueue(0.5)

    def _configure_logger(self):
        logger = logging.getLogger("queue_vip")
        logger.setLevel(logging.DEBUG)

        # File
        file_path = os.path.join(minqlx.get_cvar("fs_homepath"), "queue_vip.log")
        maxlogs = minqlx.Plugin.get_cvar("qlx_logs", int)
        maxlogsize = minqlx.Plugin.get_cvar("qlx_logsSize", int)
        file_fmt = logging.Formatter("(%(asctime)s) [%(levelname)s @ %(name)s.%(funcName)s] %(message)s", "%H:%M:%S")
        file_handler = RotatingFileHandler(file_path, encoding="utf-8", maxBytes=maxlogsize, backupCount=maxlogs)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)
        logger.info("============================= queue_vip run @ {} ============================="
                    .format(datetime.datetime.now()))

        # Console
        console_fmt = logging.Formatter("[%(name)s.%(funcName)s] %(levelname)s: %(message)s", "%H:%M:%S")
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_fmt)
        logger.addHandler(console_handler)

        return logger