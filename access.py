# This is an extension plugin  for minqlx.
# Copyright (C) 2018 sergiuszm (github) aka SerchioQ (ql)

# You can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

# The plugin checks if connecting player can access the server.

# Access is kept in Redis key: minqlx:players:{}:access as a timestamp (player can connect the server if the timestamp
# is lover than the current one)

# Its the alpha state, so any bugs might happen

import minqlx
import time
import requests
import itertools
import datetime

PLAYER_ACCESS_KEY = "minqlx:players:{}:access"


class access(minqlx.Plugin):
    def __init__(self):
        super().__init__()

        self.requests = {}
        self.request_counter = itertools.count()

        # self.add_command("setaccess", self.cmd_set_access, 5, priority=minqlx.PRI_HIGH, usage="<id> <date_timestamp>")
        self.add_command("vip", self.cmd_get_my_access, priority=minqlx.PRI_LOW)
        # self.add_command("getaccess", self.cmd_check_player_access, 3, priority=minqlx.PRI_LOW, usage="<id>")
        # self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_HIGH)
        self.add_hook("player_loaded", self.handle_player_loaded, priority=minqlx.PRI_LOWEST)

    # def handle_player_connect(self, player):
    #     user_access_timestamp = self.get_access_deadline(player, True)
    #
    #     if user_access_timestamp == 0 or int(time.time()) >= user_access_timestamp:
    #         msg = "You have no access to the server. Visit http://fb.me/CellsServer for more info!"
    #
    #         return msg
    #
    #     user_access_date = self.timestamp_to_date(user_access_timestamp)
    #
    #     # self.msg("^6{}^7 has server access until: ^6{}".format(player.name, user_access_date))

    @minqlx.delay(5)
    def handle_player_loaded(self, player):
        user_access_date = self.get_access_deadline(player, True)

        if user_access_date > 0:
            access_date = self.timestamp_to_date(user_access_date)
            if int(time.time()) >= user_access_date:
                player.reply("^6{}^7, your VIP status expired on ^6{}".format(player.name, access_date))
            else:
                player.reply("^6{}^7, you have VIP status to ^6{}".format(player.name, access_date))

        # player.tell("^6{}^7 your access to the server expires on: ^6{}".format(player.name, user_access_date))

    # def cmd_check_player_access(self, player, msg, channel):
    #     if len(msg) < 2:
    #         return minqlx.RET_USAGE
    #
    #     try:
    #         sid = int(msg[1])
    #         assert len(msg[1]) == 17
    #     except:
    #         channel.reply("Invalid player's ID!")
    #         return minqlx.RET_STOP_ALL
    #
    #     checked_player = {'steam_id': sid}
    #
    #     user_access_date = self.get_access_deadline(checked_player)
    #
    #     player.tell("^6{}^7, has access to Cells servers until: ^6{}".format(player.name, user_access_date))

    def cmd_get_my_access(self, player, msg, channel):
        user_access_date = self.get_access_deadline(player, True)

        if user_access_date > 0:
            access_date = self.timestamp_to_date(user_access_date)
            if int(time.time()) >= user_access_date:
                channel.reply("^6{}^7, your VIP status expired on ^6{}".format(player.name, access_date))
            else:
                channel.reply("^6{}^7, you have VIP status to ^6{}".format(player.name, access_date))
        else:
            channel.reply("^6{}^7, you have never been a VIP!".format(player.name))

    # def cmd_set_access(self, player, msg, channel):
    #     if len(msg) < 3:
    #         return minqlx.RET_USAGE
    #
    #     try:
    #         sid = int(msg[1])
    #         assert len(msg[1]) == 17
    #     except:
    #         channel.reply("Invalid player's ID!")
    #         return minqlx.RET_STOP_ALL
    #
    #     try:
    #         ptime = int(msg[2])
    #         assert len(msg[2]) == 10
    #     except:
    #         channel.reply("Invalid timestamp!")
    #         return minqlx.RET_STOP_ALL
    #
    #     player = {'id': sid, 'access_to': ptime, 'status': 0}
    #
    #     self.add_request(player, self.callback_getplayer, minqlx.CHAT_CHANNEL)

    @minqlx.thread
    def fetch_player(self, player, request_id):
        try:
            url = "http://qlstats.net/player/{}.json".format(player['id'])
            res = requests.get(url)

            if res.status_code != requests.codes.ok:
                player['status'] = 1
                player['msg'] = "^1Request to qlstats failed!"
                self.handle_player_info_fetched(request_id, res.status_code)
                return

            js = res.json()
            if "player" not in js[0]:
                player['status'] = 2
                player['msg'] = "^1Missing data from qlstats!"
                self.handle_player_info_fetched(request_id, requests.codes.ok)
                return

            player['nick'] = js[0]['player']['nick']
            self.handle_player_info_fetched(request_id, requests.codes.ok)

        except Exception as e:
            player['status'] = 3
            player['msg'] = "^1Problem fetching player_id {} info!".format(player['id'])
            self.handle_player_info_fetched(request_id, requests.codes.ok)

    def get_access_deadline(self, player, timestamp=False):
        try:
            access_to = int(self.db[PLAYER_ACCESS_KEY.format(player.steam_id)])

            if timestamp:
                return access_to

            user_access_date = self.timestamp_to_date(access_to)
        except KeyError as e:
            user_access_date = 0

        return user_access_date

    def add_request(self, player, callback, channel, *args):
        req = next(self.request_counter)
        self.requests[req] = player, callback, channel, args

        self.fetch_player(player, req)

    @minqlx.next_frame
    def handle_player_info_fetched(self, request_id, status_code):
        player, callback, channel, args = self.requests[request_id]
        del self.requests[request_id]
        if status_code != requests.codes.ok or player['status'] > 0:
            channel.reply("ERROR {}: Failed to fetch player info.".format(status_code))
            channel.reply(player['message'])
        else:
            callback(player, channel, *args)

    def callback_getplayer(self, player, channel):
        user_access_date = self.timestamp_to_date(player['access_to'])

        self.db[PLAYER_ACCESS_KEY.format(player['id'])] = player['access_to']
        channel.reply("{} server access has been set to date: ^6{}".format(player['nick'], user_access_date))

    def timestamp_to_date(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
