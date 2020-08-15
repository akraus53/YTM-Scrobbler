from ytmusicapi import YTMusic
import pylast
import datetime
import time
import json
from strsimpy.jaro_winkler import JaroWinkler
logger = open('log.txt', 'a+')
logger.write('%s\n' % (datetime.datetime.now()))


#################### YTM ###############
ytmusic = YTMusic('headers_auth.json')

history = ytmusic.get_history()
#print(history[0])
title = history[0]['title']
artist = history[0]['artists'][0]['name']

try:
    album = history[0]['album']['name']
except TypeError:
    logger.write("   ATTN: Album is not set\n")


#################### LAST FM ################
with open('logindata.json', 'r') as f:
    lastFmCreds = json.loads(f.read())
    f.close()

API_KEY = lastFmCreds['apikey']
API_SECRET = lastFmCreds['apisecret']
username = lastFmCreds['username']
password_hash = pylast.md5(lastFmCreds['password'])

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)

logger.write("   YTM: Last song was %s by %s\n" % (title, artist))

#################### String Compare #########
jarowinkler = JaroWinkler()

# Get last scrobble by this program
with open('last_song.json', 'r') as f:
    last_song = json.loads(f.read())
    f.close()

logger.write('   JSON: Last song was %s by %s\n' % (last_song[0], last_song[1]))

if last_song[0] != title:  # Check, so that this program doesn't scrobble the song multiple times
    last_scrobble = network.get_user(username).get_recent_tracks(limit=1)

    logger.write('   LastFM: Last song was %s by %s\n' % (last_scrobble[0][0].title, last_scrobble[0][0].artist))

    if jarowinkler.similarity(str(last_scrobble[0][0].title.lower()), title.lower()) < 0.9: # check that "nobody else" scrobbled the song
        unix_timestamp = int(time.mktime(datetime.datetime.now().timetuple()))
        if "album" in locals():
            network.scrobble(artist=artist, title=title, timestamp=unix_timestamp, album=album)
            network.update_now_playing(artist=artist, title=title, album=album)

        else:
            network.scrobble(artist=artist, title=title, timestamp=unix_timestamp)
            network.update_now_playing(artist=artist, title=title)
        logger.write("   Scrobbled %s by %s\n" % (title, artist))
        with open('last_song.json', 'w') as f:
            f.write(json.dumps((title, artist)))
            f.close()
    else:
        logger.write("   Didn't double-scrobble because of lastFM\n")
else:
    logger.write("   Didn't double-scrobble because of JSON file\n")

logger.write('\n')
logger.close()
