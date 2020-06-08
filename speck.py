import spotipy
import spotipy.util as util
from spotipy import SpotifyException
import rumps
import requests

username = 'misternate'
redirect_uri = 'http://localhost:8888/callback/'
scope = 'user-read-playback-state,user-library-modify,user-modify-playback-state'

max_track_length = 32

# ---- PORTABILITY UPDATES
# create a config file where the user enters their username
# write environment variable

# ---- Convenience
# favorite song from menu (if not already like, if liked Add remove)> pop notification when favorited
# Pause / Play
    # if paused, set a cooldown state until the user plays again
# auto skip commercials

class App(rumps.App):
    def __init__(self):
        super(App, self).__init__('Speck', icon='./resources/active.png')
        self.token = self.authorization_token()
        self.spotify = spotipy.Spotify(auth=self.token)
        self.state_prev = ''
        self.state = ''
        self.pause_count = 0
        self.track_data = {}
        self.menu = ['Pause/Play', 'Previous', 'Next', 'Like', '']
        
        rumps.debug_mode(True)

    def authorization_token(self):
        token = util.prompt_for_user_token(username, scope=scope, redirect_uri=redirect_uri)
        return token
        
    def download_album_art(self, url):
        r = requests.get(url, allow_redirects=True)
        open('./resources/artist.jpg', 'wb').write(r.content)

    def shorten_text(self, string):
        if len(string) > max_track_length:
            string = string[0:max_track_length] + '...'
        return string

    def set_state(self, state, track=None, band=None):
        self.state = state
    
        if self.state != self.state_prev:
            self.icon = f'./resources/{state}.png'
    
        if state == 'active':
            self.title = str(band) + ' · ' + track
            self.pause_count = 0
        elif state == 'paused':
            self.title = f'{str.capitalize(state)} | {self.track_data["item"]["name"]}'
        else:
            self.title = str.capitalize(f'{state}')

        if self.state and self.state_prev == 'paused':
            self.pause_count += 1
            print(f'Pause count: {self.pause_count}')
            # cool_down method (change update track to every 30, 60, 120, etc. seconds)
            # this requires using thread timer instead of rumps timer


    @rumps.clicked('Like')
    def like_song(self, sender):
        self.download_album_art(self.track_data['item']['album']['images'][2]['url'])
        rumps.notification(icon='./resources/artist.jpg', title='Saved to your liked songs', subtitle=None, message=f'{self.track_data["item"]["artists"][0]["name"]} - {self.track_data["item"]["name"]}')
        track_id = self.track_data['item']['id']
        self.spotify.current_user_saved_tracks_add(tracks=[track_id])

    @rumps.clicked('Pause/Play')
    def pause_play_track(self, sender):
        if self.track_data['is_playing'] == False or self.track_data['is_playing'] is None:
            self.spotify.start_playback()
        else:
            self.spotify.pause_playback()
        self.update_track(self)

    @rumps.clicked('Next')
    def next_track(self, sender):
        self.spotify.next_track()

    @rumps.clicked('Previous')
    def prev_track(self, sender):
        self.spotify.previous_track()

    @rumps.timer(10)
    def update_track(self, sender):
        # 1. Break up auth and update_track() 2.Add Try/Except https://github.com/plamere/spotipy/issues/83 on update_track() if auth fails auth function
        # 3. Look at using OAuth instead :/
        if self.token:
            try:
                self.track_data = self.spotify.current_user_playing_track()
            except SpotifyException:
                self.token = self.authorization_token()
                self.spotify = spotipy.Spotify(auth=self.token)
                
            if self.track_data is not None:
                is_playing = self.track_data['is_playing']
                
                if is_playing is True:
                    self.state_prev = self.state
                    artists = self.track_data['item']['artists']
                    band = []
        
                    for artist in artists:
                        band.append(artist['name'])
                    band = self.shorten_text(', '.join(band))
                    track = self.shorten_text(self.track_data['item']['name'])

                    self.state = 'active'
                    self.set_state(self.state, track, band)   

                else: # Spotify is Paused
                    self.state_prev = self.state
                    self.state = 'paused'
                    self.set_state(self.state)

            else: # No track, Spotify is most likely not running
                self.state = 'sleeping'
                self.set_state(self.state)
        else:
            self.set_state('error')


if __name__ == '__main__':
    app = App()
    app.run()