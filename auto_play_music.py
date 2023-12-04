import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

os.environ['SPOTIPY_CLIENT_ID'] = ''
os.environ['SPOTIPY_CLIENT_SECRET'] = ''
os.environ['SPOTIPY_REDIRECT_URI'] = ''


def play_music():
    scope = "user-library-read, user-read-playback-state, user-modify-playback-state"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    results = sp.current_user_playlists()
    uri = results['items'][5]['uri']

    devices = sp.devices()
    device_id = devices['devices'][0]['id']

    currently_playing = sp.currently_playing()
    is_playing = currently_playing['is_playing']

    if is_playing:
        return

    sp.start_playback(device_id=device_id, context_uri=uri)

    print("wsparcie psychiczne - Patryk Żyliński, bez niego ten projket by nie wyszedł poza plany")
