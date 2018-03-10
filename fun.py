# minqlx - A Quake Live server administrator bot.
# Copyright (C) 2015 Mino <mino@minomino.org>

# This file is part of minqlx.

# minqlx is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# minqlx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with minqlx. If not, see <http://www.gnu.org/licenses/>.

import minqlx
import random
import time
import re

from minqlx.database import Redis
from random import randint

# changes done by niewi (rniebecker@gmail.com)

my_sounds= ["hahaha yeah", "sound/player/lucy/taunt.wav",
         "haha yeah haha", "sound/player/biker/taunt.wav",
         "yeah hahaha", "sound/player/razor/taunt.wav",
         "duahaha", "sound/player/keel/taunt.wav",
         "hahaha", "sound/player/santa/taunt.wav",
         "glhf", "sound/vo/crash_new/39_01.wav",
         "f3", "sound/vo/crash_new/36_04.wav",
         "holy shit", "sound/vo_female/holy_shit",
         "infected", "sound/vo_female/infected",
         "perforated", "sound/vo_female/perforated",
         "quad god", "sound/vo_female/quad_god",
         "sudden death", "sound/vo_female/sudden_death",
         "welcome to", "sound/vo_evil/welcome",
         "goo", "sound/vo/go",
         "beep boop", "sound/player/tankjr/taunt.wav",
         "you win", "sound/vo_female/you_win.wav",
         "you lose", "sound/vo/you_lose.wav",
         "impressive", "sound/vo_female/impressive1.wav",
         "excellent", "sound/vo_evil/excellent1.wav",
         "denied", "sound/vo/denied",
         "balls out", "sound/vo_female/balls_out",
         "one", "sound/vo_female/one",
         "two", "sound/vo_female/two",
         "three", "sound/vo_female/three",
         "fight", "sound/vo_evil/fight",
         "gauntlet", "sound/vo_evil/gauntlet",
         "humiliation", "sound/vo_evil/humiliation1",
         "perfect", "sound/vo_evil/perfect",
         "wah wah wah wah", "sound/misc/yousuck",
         "ah ah ah", "sound/player/slash/taunt.wav",
         "oink", "sound/player/sorlag/pain50_1.wav",
         "argh", "sound/player/doom/taunt.wav",
         "hah haha", "sound/player/hunter/taunt.wav",
         "woohoo", "sound/player/janet/taunt.wav",
         "quake live", "sound/vo_female/quake_live",
         "$", "sound/misc/chaching",
         "uh ah", "sound/player/mynx/taunt.wav",
         "oohwee", "sound/player/anarki/taunt.wav",
         "erah", "sound/player/bitterman/taunt.wav",
         "yeahhh", "sound/player/major/taunt.wav",
         "scream", "sound/player/bones/taunt.wav",
         "salute", "sound/player/sarge/taunt.wav",
         "squish", "sound/player/orb/taunt.wav",
         "oh god", "sound/player/ranger/taunt.wav",
         "snarl", "sound/player/sorlag/taunt.wav",
         "hohoho", "sound/player/santa/taunt.wav",
         #duke
         "alien", "sound/duke/2ride06.wav",
         "abort", "sound/duke/abort01.wav",
         "pee", "sound/duke/ahmuch03.wav",
         "cleanup", "sound/duke/aisle402.wav",
         "what a mess", "sound/duke/amess06.wav",
         "annoying", "sound/duke/annoy03.wav",
         "be back", "sound/duke/beback01.wav",
         "blow it", "sound/duke/blowit01.wav",
         "booby", "sound/duke/booby04.wav",
         "bookem", "sound/duke/bookem03.wav",
         "born", "sound/duke/born01.wav",
         "chew", "sound/duke/chew05.wav",
         "cool", "sound/duke/cool01.wav",
         "damn it", "sound/duke/damnit04.wav",
         "dance", "sound/duke/dance01.wav",
         "die", "sound/duke/diesob03.wav",
         "cry", "sound/duke/cry01.wav",
         "duke", "sound/duke/duknuk14.wav",
         "doomed", "sound/duke/doomed16.wav",
         "eat shit", "sound/duke/eatsht01.wav",
         "suck", "sound/duke/guysuk01.wav",
         "holy cow", "sound/duke/holycw01.wav",
         "holyshit", "sound/duke/holysh02.wav",
         "im good", "sound/duke/imgood12.wav",
         "in hell", "sound/duke/inhell01.wav",
         "going in", "sound/duke/introc.wav",
         "jones", "sound/duke/jones04.wav",
         "kick ass", "sound/duke/kick01-i.wav",
         "ktitx", "sound/duke/ktitx.wav",
         "let god", "sound/duke/letgod01.wav",
         "lets rock", "sound/duke/letsrk03.wav",
         "looking good", "sound/duke/lookin01.wav",
         "make my day", "sound/duke/makeday1.wav",
         "play myself", "sound/duke/myself3a.wav",
         "duke nukem", "sound/duke/name01.wav",
         "needed that", "sound/duke/needed03.wav",
         "groovy", "sound/duke/groovy02.wav",
         "difference", "sound/duke/face01.wav",
         "nobody steals", "sound/duke/nobody01.wav",
         "only one", "sound/duke/onlyon03.wav",
         "party", "sound/duke/party03.wav",
         "piece of cake", "sound/duke/piece02.wav",
         "pisses me", "sound/duke/pisses01.wav",
         "go postal", "sound/duke/postal01.wav",
         "no quake", "sound/duke/quake06.wav",
         "ready for action", "sound/duke/ready2a.wav",
         "rip em", "sound/duke/ripem08.wav",
         "slacker", "sound/duke/slacker1.wav",
         "smack ass", "sound/duke/smack02.wav",
         "so help me", "sound/duke/sohelp02.wav",
         "suck it", "sound/duke/suckit01.wav",
         "terminated", "sound/duke/termin01.wav",
         "waiting for", "sound/duke/waitin03.wav",
         "this sucks", "sound/duke/thsuk13a.wav",
         "wants some", "sound/duke/wansom4a.wav",
         "freak", "sound/duke/whipyu01.wav",
         "yippie", "sound/duke/yippie01.wav",
         "yohoho", "sound/duke/yohoho01.wav",
         "bitchn", "sound/duke/bitchn04.wav",
         "come on", "sound/duke/comeon02.wav",
         "scream", "sound/duke/dscrem04.wav",
         "ajaijai", "sound/duke/dscrem38.wav",
         "escape", "sound/duke/escape01.wav",
         "force", "sound/duke/force01.wav",
         "get some", "sound/duke/getsom1a.wav",
         "game over", "sound/duke/gmeovr05.wav",
         "hurt", "sound/duke/gothrt01.wav",
         "hail", "sound/duke/hail01.wav",
         "shit happens", "sound/duke/happen01.wav",
         "independence", "sound/duke/indpnc01.wav",
         "rip", "sound/duke/rip01.wav",
         "walk", "sound/duke/yohoho09.wav",
         "shake", "sound/duke/shake2a.wav",
         #funnysounds
         "silence", "sound/funnysounds/silence",
         "allahuakbar", "sound/funnysounds/allahuakbar",
         "amazing", "sound/funnysounds/amazing",
         "ave", "sound/funnysounds/ave",
         "burns", "sound/funnysounds/burnsburns",
         "countdown", "sound/funnysounds/countdown",
         "damnit", "sound/funnysounds/damnit",
         "dead soon", "sound/funnysounds/deadsoon",
         "defeated", "sound/funnysounds/defeated",
         "for you", "sound/funnysounds/foryou",
         "fucking", "sound/funnysounds/fuckingburger",
         "crowbar", "sound/funnysounds/getcrowbar",
         "i bet", "sound/funnysounds/ibet",
         "hate all", "sound/funnysounds/ihateall",
         "my life", "sound/funnysounds/itsmylife",
         "jump", "sound/funnysounds/jumpmotherfucker",
         "ohnoe", "sound/funnysounds/ohnoe",
         "ohno", "sound/funnysounds/ohno",
         "humor", "sound/funnysounds/senseofhumor",
         "criminal", "sound/funnysounds/smoothcriminal",
         "unicorn", "sound/funnysounds/spaceunicorn",
         "stay alive", "sound/funnysounds/stayinalive",
         "surprise", "sound/funnysounds/surprise",
         "scotish", "sound/funnysounds/talkscotish",
         "tuturu", "sound/funnysounds/tuturu",
         "valkyries", "sound/funnysounds/valkyries",
         "hiding", "sound/funnysounds/whereareyou",
         "applepie", "sound/funnysounds/wouldyoulike",
         "ymca", "sound/funnysounds/ymca",
         "fucked", "sound/funnysounds/youfuckedmywife",
         "america", "sound/funnysounds/america",
         "ass kicking", "sound/funnysounds/asskicking",
         "back", "sound/funnysounds/beback",
         "headshot", "sound/funnysounds/boomheadshot",
         "devil", "sound/funnysounds/devil",
         "gotcha", "sound/funnysounds/gotcha",
         "kung fu", "sound/funnysounds/kungfu",
         "get ready", "sound/funnysounds/letsgetready",
         "live to win", "sound/funnysounds/livetowin",
         "retard", "sound/funnysounds/retard",
         "teamwork", "sound/funnysounds/teamwork",
         "realise", "sound/funnysounds/yourealise",
         "adams", "sound/funnysounds/adamsfamily",
         "things", "sound/funnysounds/allthethings",
         "bullshit", "sound/funnysounds/bullshitter",
         "cameltoe", "sound/funnysounds/cameltoe",
         "chicken", "sound/funnysounds/chicken",
         "chocolate", "sound/funnysounds/chocolaterain",
         "come", "sound/funnysounds/come",
         "cunt", "sound/funnysounds/cunt",
         "gangnam", "sound/funnysounds/gangnam",
         "imperial", "sound/funnysounds/imperial",
         "get low", "sound/funnysounds/low",
         "mario", "sound/funnysounds/mario",
         "message", "sound/funnysounds/message",
         "moan", "sound/funnysounds/moan",
         "my name is", "sound/funnysounds/myname",
         "nobody", "sound/funnysounds/nobodylikesyou",
         "numanuma", "sound/funnysounds/numanuma",
         "nyan cat", "sound/funnysounds/nyancat",
         "oh my god", "sound/funnysounds/ohmygod",
         "rocky", "sound/funnysounds/rocky",
         "starwars", "sound/funnysounds/starwars",
         "wahwahwah", "sound/funnysounds/wahwahwah",
         "wazzup", "sound/funnysounds/wazzup",
         "whistle", "sound/funnysounds/whistle",
         "wimba", "sound/funnysounds/wimbaway",
         "windows", "sound/funnysounds/windows",
         "yes master", "sound/funnysounds/yesmaster",
         "007", "sound/funnysounds/007",
         "animals", "sound/funnysounds/animals",
         "bennyhill", "sound/funnysounds/bennyhill",
         "booo", "sound/funnysounds/booo",
         "boring", "sound/funnysounds/boring",
         "cccp", "sound/funnysounds/cccp",
         "coin", "sound/funnysounds/coin",
         "cowards", "sound/funnysounds/cowards",
         "crazy", "sound/funnysounds/crazy",
         "education", "sound/funnysounds/education",
         "elementary", "sound/funnysounds/elementary",
         "fatality", "sound/funnysounds/fatality",
         "ganjaman", "sound/funnysounds/ganjaman",
         "gay", "sound/funnysounds/gay",
         "ghostbusters", "sound/funnysounds/ghostbusters",
         "god damn right", "sound/funnysounds/goddamnright",
         "holy", "sound/funnysounds/holy",
         "how are you", "sound/funnysounds/howareyou",
         "incoming", "sound/funnysounds/incoming",
         "indiana", "sound/funnysounds/indianajones",
         "its not", "sound/funnysounds/itsnot",
         "jackpot", "sound/funnysounds/jackpot",
         "jesus", "sound/funnysounds/jesus",
         "love me", "sound/funnysounds/loveme",
         "luck", "sound/funnysounds/luck",
         "mortal kombat", "sound/funnysounds/mortalkombat",
         "move ass", "sound/funnysounds/moveass",
         "nightmare", "sound/funnysounds/nightmare",
         "pacman", "sound/funnysounds/pacman",
         "pick me up", "sound/funnysounds/pickmeup",
         "pikachu", "sound/funnysounds/pikachu",
         "pinkie pie", "sound/funnysounds/pinkiepie",
         "pipe", "sound/funnysounds/pipe",
         "piss me off", "sound/funnysounds/pissmeoff",
         "powerpuff", "sound/funnysounds/powerpuff",
         "samba", "sound/funnysounds/samba",
         "say my name", "sound/funnysounds/saymyname",
         "scatman", "sound/funnysounds/scatman",
         "senora", "sound/funnysounds/shakesenora",
         "so stupid", "sound/funnysounds/sostupid",
         "story", "sound/funnysounds/story",
         "tsunami", "sound/funnysounds/tsunami",
         "tututu", "sound/funnysounds/tututu",
         "what is love", "sound/funnysounds/whatislove",
         "wtf", "sound/funnysounds/wtf",
         "yeee", "sound/funnysounds/yeee",
         "mimimi", "sound/funnysounds/mimimi",
         "mahna", "sound/funnysounds/mahnamahna",
         "soco", "sound/funnysounds/socobatevira",
         "lol", "sound/funnysounds/babylaughing",
         "amerika", "sound/funnysounds/amerika",
         "matters", "sound/funnysounds/andnothingelse",
         "du bist", "sound/funnysounds/dubist",
         "du hast", "sound/funnysounds/duhast",
         "schrei", "sound/funnysounds/einschrei",
         "engel", "sound/funnysounds/engel",
         "erst wenn", "sound/funnysounds/erstwenn",
         "exit light", "sound/funnysounds/exitlight",
         "paradise", "sound/funnysounds/gnrguitar",
         "hush", "sound/funnysounds/hush",
         "lately", "sound/funnysounds/lately",
         "lights", "sound/funnysounds/lightsout",
         "lust", "sound/funnysounds/lust",
         "muppets", "sound/funnysounds/muppetopening",
         "radioactive", "sound/funnysounds/radioactive",
         "renegade", "sound/funnysounds/renegade",
         "sail", "sound/funnysounds/sail",
         "take me", "sound/funnysounds/takemedown",
         "thunder", "sound/funnysounds/thunderstruck",
         "church", "sound/funnysounds/tochurch",
         "want you", "sound/funnysounds/wantyou",
         "never seen", "sound/funnysounds/neverseen",
         "nooo", "sound/funnysounds/nooo",
         "hello", "sound/funnysounds/hello",
         "hakuna matata", "sound/funnysounds/hakunamatata",
         "baby baby", "sound/funnysounds/babybaby",
         "im your father", "sound/funnysounds/imyourfather",
         "spierdalaj", "sound/funnysounds/spierdalaj",
         "boze", "sound/funnysounds/boze",
         "ameno", "sound/funnysounds/ameno",
         "champions", "sound/funnysounds/champions",
         "dump ways", "sound/funnysounds/dumpways",
         "john cena", "sound/funnysounds/johncena",
         "keep on fighting", "sound/funnysounds/keeponfighting",
         "no time for loosers", "sound/funnysounds/notimeforloosers",
         "rock your guitar", "sound/funnysounds/rockyourguitar",
         "sandstorm", "sound/funnysounds/sandstorm",
         "swedish chef", "sound/funnysounds/swedishchef",
         "lion king", "sound/funnysounds/lionking",
         "hammer time", "sound/funnysounds/hammertime",
         "cant touch this", "sound/funnysounds/canttouchthis",
         "bright side of life", "sound/funnysounds/brightsideoflife",
         "stoning", "sound/funnysounds/stoning",
         "sell you all", "sound/funnysounds/sellyouall",
         "girly", "sound/funnysounds/girly",
         "a scratch", "sound/funnysounds/ascratch",
         "flesh wound", "sound/funnysounds/fleshwound",
         "sweet dreams", "sound/funnysounds/sweetdreams",
         "soslow", "sound/funnysounds/socobateviraslow",
         "sofast", "sound/funnysounds/socobatevirafast",
         "soend", "sound/funnysounds/socobatevirasend",
         "losing my religion", "sound/funnysounds/losingmyreligion",
         "in your head zombie", "sound/funnysounds/inyourheadzombie",
         "when angels", "sound/funnysounds/whenangels",
         "so give me reason", "sound/funnysounds/sogivemereason",
         "dead people", "sound/funnysounds/iseedeadpeople",
         "smile", "sound/funnysounds/letsputasmile",
         "und der haifish", "sound/funnysounds/undderhaifish",
         "riff", "sound/funnysounds/rammsteinriff",
         "ich tue die weh", "sound/funnysounds/ichtuedieweh",
         "buck dich", "sound/funnysounds/buckdich",
         "benzin", "sound/funnysounds/benzin",
         "mein land", "sound/funnysounds/meinland",
         "weh mir oh weh", "sound/funnysounds/mehmirohweh",
         "ohne dich", "sound/funnysounds/ohnedich",
         "kommt die sonne", "sound/funnysounds/kommtdiesonne",
         "o fuck", "sound/funnysounds/ofuck",
         "get out the way", "sound/funnysounds/getouttheway",
         "yhehe he", "sound/funnysounds/yhehehe",
         "doesnt love you", "sound/funnysounds/doesntloveyou",
         "i cant believe", "sound/funnysounds/icantbelieve",
         "i do parkour", "sound/funnysounds/idoparkour",
         "shut your mouth", "sound/funnysounds/shutyourfuckingmouth",
         "shut the fuck up", "sound/funnysounds/shutthefuckup",
         "technology", "sound/funnysounds/technology",
         "pooping", "sound/funnysounds/pooping",
         "laugh", "sound/funnysounds/babyevillaugh",
         "kids", "sound/funnysounds/fuckingkids",
         "fuck fuck", "sound/funnysounds/fuckfuck",
         "red wins", "sound/funnysounds/redwins",
         "gg", "sound/funnysounds/goodbyesarah",
         "bg", "sound/funnysounds/goodbyeandrea",
         "kurwa", "sound/funnysounds/nonie"]

izi_sounds = [
    "lionking", "sound/izi_tunes/lionking.ogg",
    "lion king", "sound/izi_tunes/lionking.ogg",
    "redwins", "sound/izi_tunes/redwins.ogg",
    "shiet", "sound/izi_sounds/shieeeet.ogg",
    "red wins", "sound/izi_tunes/redwins.ogg",
    "bluewins", "sound/izi_tunes/bluewins.ogg",
    "blue wins", "sound/izi_tunes/bluewins.ogg",
    "ugly", "sound/izi_sounds/uglymofo.ogg",
    "10forstyle", "sound/izi_sounds/10forstyle.ogg",
    "aaaaa", "sound/izi_sounds/aaaaa.ogg",
    "aarrgghh", "sound/izi_sounds/scream.ogg",
    "aahoww", "sound/izi_sounds/aahoww.ogg",
    "abusive", "sound/izi_sounds/abusive.ogg",
    "ahyes", "sound/izi_sounds/ahyes.ogg",
    "areyouready", "sound/izi_sounds/areyouready.ogg",
    "assholes", "sound/izi_sounds/assholes.ogg",
    "asskicking", "sound/izi_sounds/asskicking.ogg",
    "awesome", "sound/izi_sounds/awesome.ogg",
    "analcream", "sound/izi_sounds/analcream.ogg",
    "akbar", "sound/izi_sounds/akbar.ogg",
    "annoying", "sound/izi_sounds/annoying.ogg",
    "babylaugh", "sound/izi_sounds/baby.ogg",
    "backstabbing", "sound/izi_sounds/backstabbing.ogg",
    "badass", "sound/izi_sounds/badass.ogg",
    "badfeeling", "sound/izi_sounds/badfeeling.ogg",
    "bamba", "sound/izi_sounds/bamba.ogg",
    "bananas", "sound/izi_sounds/bananas.ogg",
    "bazooka", "sound/izi_sounds/bazooka.ogg",
    "bb", "sound/izi_sounds/bb.ogg",
    "bendover", "sound/izi_sounds/bendover.ogg",
    "bestyoucando", "sound/izi_sounds/bestyoucando.ogg",
    "blablabla", "sound/izi_sounds/blablabla.ogg",
    "bloodonmysuit", "sound/izi_sounds/bloodonmysuit.ogg",
    "bombhasbeenplanted", "sound/izi_sounds/bombhasbeenplanted.ogg",
    "boohoo", "sound/izi_sounds/boohoo.ogg",
    "boomheadshot", "sound/izi_sounds/boomheadshot.ogg",
    "brutal", "sound/izi_sounds/brutal.ogg",
    "bugme", "sound/izi_sounds/bugme.ogg",
    "bullshitter", "sound/izi_sounds/bullshitter.ogg",
    "bullshit", "sound/izi_sounds/bullshit.ogg",
    "cameltoe", "sound/izi_sounds/cameltoe.ogg",
    "camper", "sound/izi_sounds/camper.ogg",
    "choppa", "sound/izi_sounds/choppa.ogg",
    "claxon", "sound/izi_sounds/claxon.ogg",
    "combobreaker", "sound/izi_sounds/combobreaker.ogg",
    "comehere", "sound/izi_sounds/comehere.ogg",
    "come", "sound/izi_sounds/come.ogg",
    "countdown", "sound/izi_sounds/countdown.ogg",
    "crap", "sound/izi_sounds/crap.ogg",
    "cutiepie", "sound/izi_sounds/cutiepie.ogg",
    "damnyou", "sound/izi_sounds/damnyou.ogg",
    "daddy", "sound/izi_sounds/daddy.ogg",
    "deadsoon", "sound/izi_sounds/deadsoon.ogg",
    "digthis", "sound/izi_sounds/digthis.ogg",
    "donald duck", "sound/izi_sounds/donaldduck.ogg",
    "dropthebeat", "sound/izi_sounds/dropthebeat.ogg",
    "dontthinkso", "sound/izi_sounds/donthtinkso.ogg",
    "tooot", "sound/izi_sounds/deeptoot.ogg",
    "dinohowl", "sound/izi_sounds/dinohowl.ogg",
    "dominating", "sound/izi_sounds/dominating.ogg",
    "dontmake", "sound/izi_sounds/dontmake.ogg",
    "eatme", "sound/izi_sounds/eatme.ogg",
    "eight", "sound/izi_sounds/eight.ogg",
    "english", "sound/izi_sounds/english.ogg",
    "explosions", "sound/izi_sounds/explosions.ogg",
    "faceripoff", "sound/izi_sounds/faceripoff.ogg",
    "fail", "sound/izi_sounds/fail.ogg",
    "fatality", "sound/izi_sounds/fatality.ogg",
    "fatbastard", "sound/izi_sounds/fatbastard.ogg",
    "toasty", "sound/izi_sounds/feelthepoweroftoasty.ogg",
    "fightme", "sound/izi_sounds/fightme.ogg",
    "firefight", "sound/izi_sounds/firefight.ogg",
    "kungfufighting", "sound/izi_tunes/kungfu.ogg",
    "fight", "sound/izi_sounds/fight.ogg",
    "finishher", "sound/izi_sounds/finishher.ogg",
    "finishhim", "sound/izi_sounds/finishhim.ogg",
    "five", "sound/izi_sounds/five.ogg",
    "flawlessvictory", "sound/izi_sounds/flawlessvictory.ogg",
    "fool", "sound/izi_sounds/fool.ogg",
    "four", "sound/izi_sounds/four.ogg",
    "freaks", "sound/izi_sounds/freaks.ogg",
    "freshair", "sound/izi_sounds/freshair.ogg",
    "fun", "sound/izi_sounds/laugh6.ogg",
    "fuckyourface", "sound/izi_sounds/fuckyourface.ogg",
    "fuckout", "sound/izi_sounds/fuckout.ogg",
    "fuckyouall", "sound/izi_sounds/fuckyouall.ogg",
    "fuckyouup", "sound/izi_sounds/fuckyouup.ogg",
    "fuck", "sound/izi_sounds/fuck.ogg",
    "gameover", "sound/izi_sounds/gameover.ogg",
    "gangbang", "sound/izi_sounds/gangbang.ogg",
    "gargl", "sound/izi_sounds/gargl.ogg",
    "gay", "sound/izi_sounds/gay.ogg",
    "geronimo", "sound/izi_sounds/geronimo.ogg",
    "getoffscum", "sound/izi_sounds/getoffscum.ogg",
    "getout", "sound/izi_sounds/getout.ogg",
    "givemeorders", "sound/izi_sounds/givemeorders.ogg",
    "goddamn", "sound/izi_sounds/goddammit.ogg",
    "gong", "sound/izi_sounds/gong.ogg",
    "gogogo", "sound/izi_sounds/gogogo.ogg",
    "good2go", "sound/izi_sounds/good2go.ogg",
    "goosebumps", "sound/izi_sounds/goosebumps.ogg",
    "gotcha", "sound/izi_sounds/gotcha.ogg",
    "imove4noman", "sound/izi_sounds/imove4noman.ogg",
    "gottamove", "sound/izi_sounds/gottamove.ogg",
    "monsterkill", "sound/izi_sounds/monsterkill.ogg",
    "greatshot", "sound/izi_sounds/greatshot.ogg",
    "growl", "sound/izi_sounds/growl.ogg",
    "guarentee", "sound/izi_sounds/guarentee.ogg",
    "hairy", "sound/izi_sounds/hairy.ogg",
    "headshot", "sound/izi_sounds/headshot.ogg",
    "hakuna", "sound/izi_sounds/hakunamatata.ogg",
    "heavenly", "sound/izi_sounds/heavenly.ogg",
    "hehehe", "sound/izi_sounds/hehehe.ogg",
    "hellobabe", "sound/izi_sounds/hellobabe.ogg",
    "holyshit", "sound/izi_sounds/holyshit.ogg",
    "heyyyy", "sound/izi_sounds/heyyyy.ogg",
    "holy", "sound/izi_sounds/holy.ogg",
    "horsie", "sound/izi_sounds/horsie.ogg",
    "hothothot", "sound/izi_sounds/hothothot.ogg",
    "howl", "sound/izi_sounds/howl.ogg",
    "huhuha", "sound/izi_sounds/huhuha.ogg",
    "hurensohn", "sound/izi_sounds/hurensohn.ogg",
    "hurtmyfeelings", "sound/izi_sounds/hurtmyfeelings.ogg",
    "ibet", "sound/izi_sounds/ibet.ogg",
    "idontthinkso", "sound/izi_sounds/idontthinkso.ogg",
    "ihateall", "sound/izi_sounds/ihateall.ogg",
    "ikilledyou", "sound/izi_sounds/ikilledyou.ogg",
    "iluvu2", "sound/izi_sounds/iluvu2.ogg",
    "imgood", "sound/izi_sounds/imgood.ogg",
    "imwaiting", "sound/izi_sounds/imwaiting.ogg",
    "incoming", "sound/izi_sounds/incoming.ogg",
    "ishedead", "sound/izi_sounds/ishedead.ogg",
    "itoldyou", "sound/izi_sounds/itoldyouiwouldfindyou.ogg",
    "itson", "sound/izi_sounds/itson.ogg",
    "iwillkillyou", "sound/izi_sounds/iwillkillyou.ogg",
    "izipizi", "sound/izi_sounds/izipizi.ogg",
    "jesus", "sound/izi_sounds/jesus.ogg",
    "justdie", "sound/izi_sounds/justdie.ogg",
    "justdoit", "sound/izi_sounds/justdoit.ogg",
    "kaboom", "sound/izi_sounds/kaboom.ogg",
    "killer", "sound/izi_sounds/killer.ogg",
    "killingmachine", "sound/izi_sounds/killingmachine.ogg",
    "killyourself", "sound/izi_sounds/killyourself.ogg",
    "letsgetready", "sound/izi_sounds/letsgetready.ogg",
    "licklead", "sound/izi_sounds/licklead.ogg",
    "lifesux", "sound/izi_sounds/lifesux.ogg",
    "lion", "sound/izi_sounds/lion.ogg",
    "longforcombat", "sound/izi_sounds/longforcombat.ogg",
    "lost", "sound/izi_sounds/lost.ogg",
    "loudnoises", "sound/izi_sounds/loudnoises.ogg",
    "low", "sound/izi_sounds/low.ogg",
    "lukang", "sound/izi_sounds/lukang.ogg",
    "mario", "sound/izi_sounds/mario.ogg",
    "mewins", "sound/izi_sounds/mewins.ogg",
    "medic", "sound/izi_sounds/medic.ogg",
    "meepmeep", "sound/izi_sounds/meepmeep.ogg",
    "milkshake", "sound/izi_sounds/milkshake.ogg",
    "missiles", "sound/izi_sounds/missiles.ogg",
    "motherlessgoat", "sound/izi_sounds/motherlessgoat.ogg",
    "mouahaha", "sound/izi_sounds/mouahaha.ogg",
    "nasty", "sound/izi_sounds/nasty.ogg",
    "neverlearn", "sound/izi_sounds/neverlearn.ogg",
    "neverstop", "sound/izi_sounds/neverstopkillingyou.ogg",
    "nine", "sound/izi_sounds/nine.ogg",
    "noson", "sound/izi_sounds/noson.ogg",
    "nowisthetime", "sound/izi_sounds/nowisthetime.ogg",
    "numnut", "sound/izi_sounds/numnut.ogg",
    "oeh", "sound/izi_sounds/oeh.ogg",
    "ohno", "sound/izi_sounds/ohno.ogg",
    "okletsgo", "sound/izi_sounds/okletsgo.ogg",
    "overhere", "sound/izi_sounds/overhere.ogg",
    "owned", "sound/izi_sounds/owned.ogg",
    "pacman", "sound/izi_sounds/pacman.ogg",
    "pancakes", "sound/izi_sounds/pancakes.ogg",
    "pathetic", "sound/izi_sounds/pathetic.ogg",
    "paydenough", "sound/izi_sounds/paydenough.ogg",
    "pieceofme", "sound/izi_sounds/pieceofme.ogg",
    "plasma", "sound/izi_sounds/plasma.ogg",
    "playagame", "sound/izi_sounds/playaGame.ogg",
    "prepare", "sound/izi_sounds/prepare.ogg",
    "proud", "sound/izi_sounds/proud.ogg",
    "r2d2scream", "sound/izi_sounds/r2d2scream.ogg",
    "r2d2", "sound/izi_sounds/r2d2.ogg",
    "raaaah", "sound/izi_sounds/raaaah.ogg",
    "raaah", "sound/izi_sounds/raaah.ogg",
    "ready", "sound/izi_sounds/ready.ogg",
    "retard", "sound/izi_sounds/retard.ogg",
    "resistance", "sound/izi_sounds/resistance.ogg",
    "rooster", "sound/izi_animals/rooster1.ogg",
    "roar", "sound/izi_sounds/roar.ogg",
    "runningback", "sound/izi_sounds/runningback.ogg",
    "run", "sound/izi_sounds/runbitchrun.ogg",
    "ruuuuh", "sound/izi_sounds/ruuuuh.ogg",
    "saidsmth", "sound/izi_sounds/saidsmth.ogg",
    "seeuinhell", "sound/izi_sounds/seeuinhell.ogg",
    "serioushurting", "sound/izi_sounds/serioushurting.ogg",
    "seven", "sound/izi_sounds/seven.ogg",
    "shitonmyface", "sound/izi_sounds/shitonmyface.ogg",
    "shockwave", "sound/izi_sounds/shockwave.ogg",
    "spell", "sound/izi_sounds/spell.ogg",
    "run", "sound/izi_sounds/runbitchrun.ogg",
    "shootthatfool", "sound/izi_sounds/shootthatfool.ogg",
    "shutup", "sound/izi_sounds/shutup.ogg",
    "six", "sound/izi_sounds/six.ogg",
    "skinflute", "sound/izi_sounds/skinflute.ogg",
    "smth2shoot", "sound/izi_sounds/smth2shoot.ogg",
    "snake", "sound/izi_sounds/snake.ogg",
    "sonofabitch", "sound/izi_sounds/sonofabitch.ogg",
    "suckyourself", "sound/izi_sounds/suckyourself.ogg",
    "surprise", "sound/izi_sounds/surprise.ogg",
    "suspence", "sound/izi_sounds/suspence.ogg",
    "takeit", "sound/izi_sounds/takeit.ogg",
    "teamwork", "sound/izi_sounds/teamwork.ogg",
    "ten", "sound/izi_sounds/ten.ogg",
    "thatsright", "sound/izi_sounds/thatstight.ogg",
    "three", "sound/izi_sounds/three.ogg",
    "tralala", "sound/izi_sounds/tralala.ogg",
    "two", "sound/izi_sounds/two.ogg",
    "ultimate", "sound/izi_sounds/ultimate.ogg",
    "underwear", "sound/izi_sounds/underwear.ogg",
    "uuuh", "sound/izi_sounds/uuuh.ogg",
    "verywell", "sound/izi_sounds/verywell.ogg",
    "violentcontent", "sound/izi_sounds/violentcontent.ogg",
    "wazzup", "sound/izi_sounds/wazzup.ogg",
    "wet", "sound/izi_sounds/wet.ogg",
    "winning", "sound/izi_sounds/winning.ogg",
    "win", "sound/izi_sounds/win.ogg",
    "windows", "sound/izi_sounds/windows.ogg",
    "victorious", "sound/izi_sounds/win.ogg",
    "wtf", "sound/izi_sounds/wtf.ogg",
    "yehaw", "sound/izi_sounds/yehaw.ogg",
    "yesmaster", "sound/izi_sounds/yesmaster.ogg",
    "master", "sound/izi_sounds/master.ogg",
    "yessir", "sound/izi_sounds/yessir.ogg",
    "yourdaddy", "sound/izi_sounds/yourdaddy.ogg",
    "yourself", "sound/izi_sounds/yourself.ogg",
    "yousuck", "sound/izi_sounds/yousuck.ogg",
    "youthinkimabitch", "sound/izi_sounds/youthinkimabitch.ogg",
    "youwantmore", "sound/izi_sounds/youwantmore.ogg",
    "yummi", "sound/izi_sounds/yummi.ogg",
    "zero", "sound/izi_sounds/zero.ogg",
    "007", "sound/izi_tunes/007.ogg",
    "adamsfamily", "sound/izi_tunes/adamsfamily.ogg",
    "adams family", "sound/izi_tunes/adamsfamily.ogg",
    "allstar", "sound/izi_tunes/allstar.ogg",
    "ameno", "sound/izi_tunes/ameno.ogg",
    "avemaria", "sound/izi_tunes/ave.ogg",
    "ave maria", "sound/izi_tunes/ave.ogg",
    "bennyhill", "sound/izi_tunes/bennyhill.ogg",
    "bonkers", "sound/izi_tunes/bonkers.ogg",
    "canttouchthis", "sound/izi_tunes/canttouchthis.ogg",
    "cant touch this", "sound/izi_tunes/canttouchthis.ogg",
    "chacaron", "sound/izi_tunes/chacaron.ogg",
    "champions", "sound/izi_tunes/champions.ogg",
    "chickentune", "sound/izi_tunes/chicken.ogg",
    "cunt", "sound/izi_tunes/cunt.ogg",
    "devil", "sound/izi_tunes/devil.ogg",
    "education", "sound/izi_tunes/education.ogg",
    "electro", "sound/izi_tunes/electro.ogg",
    "freestyler", "sound/izi_tunes/freestyler.ogg",
    "gangnam", "sound/izi_tunes/gangnam.ogg",
    "ganjaman", "sound/izi_tunes/ganjaman.ogg",
    "getouttheway", "sound/izi_tunes/getouttheway.ogg",
    "get out the way", "sound/izi_tunes/getouttheway.ogg",
    "ghostbusters", "sound/izi_tunes/ghostbusters.ogg",
    "girly", "sound/izi_tunes/girly.ogg",
    "goodbye", "sound/izi_tunes/goodbyesarah.ogg",
    "hukuna", "sound/izi_tunes/hakunamatata.ogg",
    "imperial", "sound/izi_tunes/imperial.ogg",
    "sexy", "sound/izi_tunes/imsexy.ogg",
    "indiana", "sound/izi_tunes/indianajones.ogg",
    "mahna", "sound/izi_tunes/mahnamahna.ogg",
    "mimi", "sound/izi_tunes/mimimi.ogg",
    "missionimpossible", "sound/izi_tunes/mission.ogg",
    "muppet", "sound/izi_tunes/muppetopening.ogg",
    "nobody", "sound/izi_tunes/nobodylikesyou.ogg",
    "nyan", "sound/izi_tunes/nyancat.ogg",
    "pinkpanther", "sound/izi_tunes/pinkpanther.ogg",
    "sandstorm", "sound/izi_tunes/sandstorm.ogg",
    "scatman", "sound/izi_tunes/scatman.ogg",
    "shake", "sound/izi_tunes/shakesenora.ogg",
    "sleepy", "sound/izi_tunes/sleepy.ogg",
    "zzz", "sound/izi_tunes/sleepy.ogg",
    "unicorn", "sound/izi_tunes/spaceunicorn.ogg",
    "stamp", "sound/izi_tunes/stampon.ogg",
    "starwars", "sound/izi_tunes/starwars.ogg",
    "story", "sound/izi_tunes/story.ogg",
    "neverending", "sound/izi_tunes/story.ogg",
    "scotish", "sound/izi_tunes/talkscotish.ogg",
    "tsunami", "sound/izi_tunes/tsunami.ogg",
    "tutu", "sound/izi_tunes/tututu.ogg",
    "typewriter", "sound/izi_tunes/typewriter.ogg",
    "love", "sound/izi_tunes/whatislove.ogg",
    "wimbaway", "sound/izi_tunes/wimbaway.ogg",
]

izi_sounds_random = [
    ":|", "sound/izi_sounds/omg{}.ogg", 2,
    ":(", "sound/izi_sounds/omg{}.ogg", 2,
    ":o", "sound/izi_sounds/omg{}.ogg", 2,
    "hahaha", "sound/izi_sounds/laugh{}.ogg", 6,
    "babycry", "sound/izi_sounds/babycry{}.ogg", 2,
    "kungfu", "sound/izi_sounds/kungfu{}.ogg", 3,
    "horse", "sound/izi_animals/horse{}.ogg", 5,
    "issexy", "sound/izi_sounds/issexy{}.ogg", 2,
    "idiot", "sound/izi_sounds/idiot{}.ogg", 6,
    "goat", "sound/izi_animals/goat{}.ogg", 2,
    "stfu", "sound/izi_sounds/stfu{}.ogg", 2,
    "fart", "sound/izi_sounds/fart{}.ogg", 8,
    "duck", "sound/izi_animals/duck{}.ogg", 4,
    "dude", "sound/izi_sounds/dude{}.ogg", 2,
    "dingeling", "sound/izi_sounds/dingeling{}.ogg", 3,
    "dog", "sound/izi_animals/dog{}.ogg", 7,
    "donkey", "sound/izi_animals/donkey{}.ogg", 2,
    "meow", "sound/izi_animals/cat{}.ogg", 3,
    "chicken", "sound/izi_animals/chicken{}.ogg", 4,
    "cow", "sound/izi_animals/cow{}.ogg", 7,
    "burp", "sound/izi_sounds/burp{}.ogg", 3,
    "boing", "sound/izi_sounds/boing{}.ogg", 3,
    "omg", "sound/izi_sounds/omg{}.ogg", 2,
    "orgasm", "sound/izi_sounds/orgasm{}.ogg", 6,
    "outstanding", "sound/izi_sounds/outstanding{}.ogg", 2,
    "punch", "sound/izi_sounds/punch{}.ogg", 4,
    "sheep", "sound/izi_animals/sheep{}.ogg", 4,
    "slap", "sound/izi_sounds/slap{}.ogg", 9,
    "squeek", "sound/izi_sounds/squeek{}.ogg", 2,
    "welldone", "sound/izi_sounds/welldone{}.ogg", 2,
    "wickedsick", "sound/izi_sounds/wickedsick{}.ogg", 2,
]

class fun(minqlx.Plugin):
    database = Redis

    def __init__(self):
        super().__init__()
        self.add_hook("chat", self.handle_chat)
        self.add_command("cookies", self.cmd_cookies)
        self.last_sound = None
        self.set_cvar_once("qlx_funSoundDelay", "3")
        self.add_command("beer", self.cmd_beer)
        self.add_command("tissue", self.cmd_tissue, usage="<name>")
        self.add_command("love", self.cmd_love, usage="<name>")
        self.add_command("slaps", self.cmd_slap, usage="<name>")
        self.add_command("<3", self.cmd_heart)
        self.add_command("buttplug", self.cmd_buttplug)
        self.add_command("soundlist", self.cmd_soundlist)
        self.add_command("izi_list", self.cmd_iziSoundlist)
        self.add_command("izi_list_multi", self.cmd_iziRandomSoundlist)
        self.add_command("randomsound", self.cmd_randomsound)

    def handle_chat(self, player, msg, channel):
        if channel != "chat":
            return

        msg = self.clean_text(msg)
        msglower = msg.lower()

        slen = len(my_sounds)
        for i in range(0, slen, 2):
           if msglower.find(my_sounds[i]) >= 0:
              self.play_sound(my_sounds[i + 1])
              break

        slen = len(izi_sounds)
        for i in range(0, slen, 2):
           if msglower.find(izi_sounds[i]) >= 0:
              self.play_sound(izi_sounds[i + 1])
              break

        slen = len(izi_sounds_random)
        for i in range(0, slen, 3):
           if msglower.find(izi_sounds_random[i]) >= 0:
              self.play_sound(izi_sounds_random[i + 1].format(random.randint(1, izi_sounds_random[i + 2])))
              break

    def play_sound(self, path):
        if not self.last_sound:
            pass
        elif time.time() - self.last_sound < self.get_cvar("qlx_funSoundDelay", int):
            return

        self.last_sound = time.time()
        for p in self.players():
            if self.db.get_flag(p, "essentials:sounds_enabled", default=True):
                super().play_sound(path, p)

    def cmd_cookies(self, player, msg, channel):
        x = random.randint(0, 100)
        if not x:
            channel.reply("^6♥ ^7Here you go, {}. I baked these just for you! ^6♥".format(player))
        elif x == 1:
            channel.reply("What, you thought ^6you^7 would get cookies from me, {}? Hah, think again.".format(player))
        elif x < 50:
            channel.reply("For me? Thank you, {}!".format(player))
        else:
            channel.reply("I'm out of cookies right now, {}. Sorry!".format(player))

    def cmd_beer(self, player, msg, channel):
        beers= ["Warsteiner", "Budweiser", "Guinness", "Paulaner", "Heineken", "Grolsch", "Pilsner Urquell", "Beck's", "Bitburger"]
        prost= ["Prost!", "Cheers!", "Skoal!", "Na zdravi!", "Kippis!"]
        s = random.choice(beers)
        p = random.choice(prost)
        channel.reply("{} ^7hands a ^1{} ^7to everyone. ^3{}".format(player, s, p))

    def cmd_tissue(self, player, msg, channel):
        tissue= ["{} ^7hands ^7{} a bag of tissues.", "{} ^7hands ^7{} an old used handkerchief."]
        s = random.choice(tissue)

        if len(msg) < 2:
             return minqlx.RET_USAGE

        n = self.find_player(msg[1])
        if n:
             channel.reply(s.format(player, n[0].name))
        else:
             channel.reply("^7I do not know '{}'.".format(msg[1]))

    def cmd_love(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE

        n = self.find_player(msg[1])
        if n:
            channel.reply("{} ^7is in ^1LOVE ^7with {}^7!".format(player, n[0].name))
        else:
            channel.reply("^7I do not know '{}'.".format(msg[1]))

    def cmd_slap(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE

        slaps= ["{} ^7slaps ^7{} around a bit with a large trout.",
                "{} ^7slaps ^7{} around a bit with used tissue papers.",
                "{} ^7slaps ^7{} around a bit with a space monkey.",
                "{} ^7slaps ^7{} around a bit with a barracouda.",
                "{} ^7slaps ^7{} around a bit with a rubber chicken.",
                "{} ^7slaps ^7{} around a bit with a bag full of slimy snails.",
                "{} ^7slaps ^7{} around a bit with a ton of bricks."]

        s = random.choice(slaps)
        n = self.find_player(msg[1])
        if n:
            channel.reply(s.format(player, n[0].name))
        else:
            channel.reply("^7I do not know '{}'.".format(msg[1]))

    def cmd_heart(self, player, msg, channel):
        s = ("^1\r oo   oo"
             "\no  o o  o"
             "\no   o   o"
             "\n o     o"
             "\n  o   o"
             "\n   o o"
             "\n    o")
        channel.reply(s.replace("o", "\x08"))

    def cmd_buttplug(self, player, msg, channel):
        channel.reply("{} ^7has been ^1BUTTPLUGGED^7!".format(player))

    def cmd_soundlist(self, player, msg, channel):
        slen = len(my_sounds)
        slist = "Sounds: "
        j = 0
        c = 0
        for i in range(0, slen, 2):
           slist = slist + "^1" + my_sounds[i] +"^7,"
           j = j + 1
           c = c + 1
           if j == 5:
              slist = slist + "\n"
              j = 0
        slist = slist + "\n^7Number of Sounds: ^1{}"
        player.tell(slist.format(c))

    def cmd_iziSoundlist(self, player, msg, channel):
        slen = len(izi_sounds)
        slist = "Izi sounds: "
        j = 0
        c = 0
        for i in range(0, slen, 2):
           slist = slist + "^1" + izi_sounds[i] + "^7,"
           j = j + 1
           c = c + 1
           if j == 5:
              slist = slist + "\n"
              j = 0
        slist = slist + "\n^7Number of Sounds: ^1{}"
        player.tell(slist.format(c))

    def cmd_iziRandomSoundlist(self, player, msg, channel):
        slen = len(izi_sounds_random)
        slist = "Izi multi-sounds: "
        j = 0
        c = 0
        for i in range(0, slen, 3):
           slist = slist + "^1" + izi_sounds_random[i] + "^7,"
           j = j + 1
           c = c + 1
           if j == 5:
              slist = slist + "\n"
              j = 0
        slist = slist + "\n^7Number of Sounds: ^1{}"
        player.tell(slist.format(c))

    def cmd_randomsound(self, player, msg, channel):
        slen = len(my_sounds) / 2
        n = randint(0, slen) * 2
        self.play_sound(my_sounds[n + 1])
        s = "^7Playing Sound: ^1{}"
        channel.reply(s.format(my_sounds[n]))

