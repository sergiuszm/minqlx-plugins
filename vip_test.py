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

_extended_vip_key = "minqlx:servers:{}:extended_vip"

class vip_test(minqlx.Plugin):
    def __init__(self):
        self.add_hook("new_game", self.handle_new_game)
        # self.add_hook("game_end", self.handle_game_end)
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_hook("player_disconnect", self.handle_player_disconnect)

        # Commands for debugging
        # self.add_command("qpush", self.cmd_qpush, 5)
        # self.add_command("qadd", self.cmd_qadd, 5, usage="<id>")
        # self.add_command("qupd", self.cmd_qupd, 5)

        self._queue = []
        self._vip_queue = []
        # self.initialize()
        self.is_endscreen = False  ######## TODO: replace for something better, because
        ######## loading during the endgame screen might cause bugs
        # self.set_cvar_once("qlx_queueSetAfkPermission", "2")
        # self.set_cvar_once("qlx_queueAFKTag", "^3AFK")
        self.game_port = minqlx.get_cvar("net_port")
        self.jointimes = {}
        self._extended_vip = self.checkIfExtendedVipEnabled()

        self.qlogger = self._configure_logger()


    def checkIfExtendedVipEnabled(self):
        try:
            extended_vip = bool(self.db[_extended_vip_key.format(self.game_port)])

            if extended_vip:
                return extended_vip

        except KeyError as e:
            extended_vip = False

        return extended_vip

    ## Plugin Handles and Commands
    def handle_new_game(self):
        self.qlogger.debug("NEW GAME")

    def handle_player_disconnect(self, player, reason):
        if player.steam_id in self.jointimes:
            del self.jointimes[player.steam_id]

        self.qlogger.debug(self.jointimes)
        self.qlogger.debug(self.players())


    def handle_player_loaded(self, player):
        self.qlogger.debug(self.jointimes)

        if not player.vip:
            self.jointimes[player.steam_id] = int(time.time())

        self.qlogger.debug(self.players())
        self.qlogger.debug(self.jointimes)


    def _configure_logger(self):
        logger = logging.getLogger("vip_test")
        logger.setLevel(logging.DEBUG)

        # File
        file_path = os.path.join(minqlx.get_cvar("fs_homepath"), "vip_test.log")
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