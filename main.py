import spotipy
import spotipy.util as util
import rumps

username = 'misternate'
redirect_uri = 'http://localhost:8888/callback/'
scope = 'user-read-playback-state'

class App(rumps.App):
    def __init__(self):
        super(App, self).__init__('Loading...')
        self.icon = './resources/active_48x48.png'
        self.token = util.prompt_for_user_token(username, scope, redirect_uri=redirect_uri)
        rumps.debug_mode(True)
    
    def set_state(self, state, track=None, band=None):
        if state == 'active':
            self.icon = './resources/active_48x48.png'
            self.title = str(band) + ' - ' + track
        elif state == 'inactive':
            self.icon = './resources/inactive_48x48.png'
        elif state == 'paused':
            self.icon = './resources/paused_48x48.png'
            self.title = 'Paused'

    #check if a song is playing
    @rumps.timer(10)
    def update_track(self, sender):
        if self.token:
            spotify = spotipy.Spotify(auth=token)
            track_data = spotify.current_user_playing_track()
            
            if track_data is not None:
                is_playing = track_data['is_playing']
                
                if is_playing is True:                    
                    track = track_data['item']['name']
                    artists = track_data['item']['artists']
                    band = []
        
                    for artist in artists:
                        band.append(artist['name'])
                        band = ', '.join(band)
                    
                    self.set_state('active', track, band)   

                else: # Spotify is Paused
                    self.set_state('paused')

            else: # No track, Spotify is most likely not running
                self.set_state('inactive')
        else: # No token available
            self.set_state('inactive', No Token)

if __name__ == '__main__':
    app = App()
    app.run()