import spotipy
import spotipy.util as util
from spotipy import SpotifyException
import rumps

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

def authorization_token():
    token = util.prompt_for_user_token(username, scope, redirect_uri=redirect_uri)

    return token


class App(rumps.App):
    def __init__(self):
        super(App, self).__init__('Speck', icon='./resources/active.png')
        self.token = authorization_token()
        self.state_prev = ''
        self.state = ''
        self.pause_count = 0
        self.track_data = {}
        self.menu = ['Pause/Play', 'Like Song', '']
        
        rumps.debug_mode(True)

    @rumps.clicked('Like Song')
    def like_song(self, sender):
        track_id = self.track_data['item']['id']
        spotify = spotipy.Spotify(auth=self.token)
        spotify.current_user_saved_tracks_add(tracks=[track_id])
        rumps.notification(icon='./resources/app.png', title=None, subtitle=None, message=f'{self.track_data["item"]["artists"][0]["name"]} - {self.track_data["item"]["name"]}')

    @rumps.clicked('Pause/Play')
    def pause_song(self, sender):
        spotify = spotipy.Spotify(auth=self.token)
        if self.track_data['is_playing'] == False or self.track_data['is_playing'] is None:
            spotify.start_playback()
        else:
            spotify.pause_playback()
        self.update_track(self)

    def shorten_text(self, string):
        print(string)
        if len(string) > max_track_length:
            string = string[0:max_track_length] + '...'
        return string

    def set_state(self, state, track=None, band=None):
        print(f'Prev: {self.state_prev}')
        print(f'Current: {self.state}')

        self.state = state
    
        if self.state != self.state_prev: #do not unneccesarily change icon
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

    @rumps.timer(10)
    def update_track(self, sender):
        # 1. Break up auth and update_track() 2.Add Try/Except https://github.com/plamere/spotipy/issues/83 on update_track() if auth fails auth function
        # 3. Look at using OAuth instead :/
        if self.token:
            spotify = spotipy.Spotify(auth=self.token)
            try:
                self.track_data = spotify.current_user_playing_track()
            except SpotifyException:
                self.token = authorization_token()
                
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