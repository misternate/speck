import spotipy
import spotipy.util as util
import rumps


class App(rumps.App):
    def __init__(self):
        super(App, self).__init__('Loading...')
        self.icon = './resources/active_48x48.png'
        rumps.debug_mode(True)


    #check if a song is playing
    @rumps.timer(10)
    def update_track(self, sender):
        scope = 'user-read-playback-state'
        username = 'misternate'
        redirect_uri = 'http://localhost:8888/callback/'
        token = util.prompt_for_user_token(username, scope, redirect_uri=redirect_uri)
        
        if token:
            sp = spotipy.Spotify(auth=token)
            track_data = sp.current_user_playing_track()
            if track_data is not None:
                track = track_data['item']['name']
                artist = track_data['item']['artists'][0]['name']
                self.title = artist + ' - ' + track
            else:
                self.title = ' Not connected...'
        else:
            print("Can't get token for", username)

if __name__ == '__main__':
    app = App()
    app.run()