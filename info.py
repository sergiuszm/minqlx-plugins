import minqlx
import time

from minqlx.database import Redis


class info(minqlx.Plugin):
    def __init__(self):
        super().__init__()

        # set cvars once. EDIT THESE IN SERVER.CFG!
        self.set_cvar_once("qlx_info_interval", "60")
        self.set_cvar_once("qlx_info_seconds", "15")

        self.add_hook("new_game", self.handle_new_game)

        # start counting reminders if we are in warmup
        self.handle_new_game()

        self.game_active = False

    # Goes off when new maps are loaded, games are aborted, games ended but stay on same map and matchstart
    @minqlx.delay(3)
    def handle_new_game(self):
        if self.game.state in ["in_progress", "countdown"]:
            return

        self.game_active = False
        self.display_info(time.time())

    @minqlx.thread
    def display_info(self, warmup):
        while all([self.game.state == "warmup", self.__class__.__name__ in minqlx.Plugin._loaded_plugins]):
            diff = time.time() - warmup # difference in seconds
            if diff >= int(self.get_cvar('qlx_info_seconds')):
                m = "^7Od 21.02.2018 ^3serwery beda dostepne na haslo! "
                m += "\n^2Koszt dostepu wynosi 10 zl/msc. "
                m += "\n^4Wiecej info na https://fb.me/CellsServer"
                self.msg(m.replace('\n', ''))
                self.center_print(m)
                time.sleep(int(self.get_cvar('qlx_info_interval')))
                continue
            time.sleep(1)