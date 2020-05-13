import spotipy
import spotipy.util as util
from spotipy import SpotifyException
import rumps

username = 'misternate'
redirect_uri = 'http://localhost:8888/callback/'
scope = 'user-read-playback-state,user-library-modify'

# ---- PORTABILITY UPDATES
# create a config file where the user enters their username
# write environment variable

# ---- Convenience
# favorite song from menu (if not already like, if liked Add remove)> pop notification when favorited
# Pause / Play
# auto skip commercials

class App(rumps.App):
    def __init__(self):
        super(App, self).__init__('Speck', icon='./resources/active.png')
        self.token = util.prompt_for_user_token(username, scope, redirect_uri=redirect_uri)
        self.state_prev = ''
        self.state = ''
        self.pause_count = 0
        self.track_data = {}

        self.menu = ['Add to Liked Songs', 'Skip Ads']
        
        rumps.debug_mode(True)

    @rumps.clicked('Add to Liked Songs')
    def like_song(self, sender):
        track_id = self.track_data['item']['id']
        spotify = spotipy.Spotify(auth=self.token)
        spotify.current_user_saved_tracks_add(tracks=[track_id])
        rumps.notification(icon='./resources/app.png', title='Speck', subtitle='', message=self.track_data['item']['name'] + ' added to Liked Songs.')

    def set_state(self, state, track=None, band=None):
        print(f'Prev: {self.state_prev}')
        print(f'Current: {self.state}')

        self.state = state
    
        if self.state != self.state_prev: #do not unneccesarily change icon
            self.icon = f'./resources/{state}.png'
    
        if state == 'active':
            self.title = str(band) + ' · ' + track
            self.pause_count = 0
        else:
            self.title = str.capitalize(f'{state}')

        if self.state and self.state_prev == 'paused':
            self.pause_count += 1
            print(f'Pause count: {self.pause_count}')
            # cool_down method (change update track to every 30, 60, 120, etc. seconds)
            # this requires using thread timer instead of rumps timer

    @rumps.timer(10)
    def update_track(self, sender):
        # 1. Break up auth and update_track() 2.Add Try/Except https://github.com/plamere/spotipy/issues/83 to update track auth function
        # 3. Look at using OAuth instead :/
        if self.token:
            spotify = spotipy.Spotify(auth=self.token)
            print('Trying spotify(auth=self.token)')
            try:
                self.track_data = spotify.current_user_playing_track()
            except SpotifyException:
                self.token = util.prompt_for_user_token(username, redirect_uri=redirect_uri)
                

            if self.track_data is not None:
                is_playing = self.track_data['is_playing']
                
                if is_playing is True:
                    self.state_prev = self.state
                    track = self.track_data['item']['name']
                    artists = self.track_data['item']['artists']
                    band = []
        
                    for artist in artists:
                        band.append(artist['name'])
                    band = ', '.join(band)
                    
                    self.state = 'active'
                    self.set_state(self.state, track, band)   

                else: # Spotify is Paused
                    self.state_prev = self.state
                    self.state = 'paused'
                    self.set_state(self.state)

            else: # No track, Spotify is most likely not running
                self.state = 'inactive'
                self.set_state(self.state)
        else:
            self.set_state('error')


if __name__ == '__main__':
    app = App()
    app.run()