import spotipy
import spotipy.util as util
import rumps

username = 'misternate'
redirect_uri = 'http://localhost:8888/callback/'
scope = 'user-read-playback-state'

# create a config file where the user enters their username
# write environment variable

class App(rumps.App):
    def __init__(self):
        super(App, self).__init__('Loading...')
        self.token = util.prompt_for_user_token(username, scope, redirect_uri=redirect_uri)
        self.state_prev = ''
        self.state = ''
        self.pause_count = 0

        rumps.debug_mode(True)
    
    def set_state(self, state, track=None, band=None):
        print(f'Prev: {self.state_prev}')
        print(f'Current: {self.state}')

        self.state = state
    
        if self.state != self.state_prev: #do not unneccesarily change icon
            self.icon = f'./resources/{state}.png'
    
        if state == 'active':
            self.title = str(band) + ' · ' + track
        else:
            self.title = str.capitalize(f'{state}')

        if self.state and self.state_prev == 'paused':
            self.pause_count += 1
            print(self.pause_count)
            # cool_down method (change update track to every 30, 60, 120, etc. seconds)
            # this requires using thread timer instead of rumps timer

    #check if a song is playing
    @rumps.timer(10)
    def update_track(self, sender):
        if self.token:
            spotify = spotipy.Spotify(auth=self.token)
            track_data = spotify.current_user_playing_track()
            
            if track_data is not None:
                is_playing = track_data['is_playing']
                
                if is_playing is True:
                    self.state_prev = self.state
                    track = track_data['item']['name']
                    artists = track_data['item']['artists']
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
        else: # No token available
            self.set_state('error')

if __name__ == '__main__':
    app = App()
    app.run()