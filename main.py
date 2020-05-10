from threading import Timer

import spotipy
import spotipy.util as util
import rumps

#check if a song is playing
    # get track duration and progress
    # run timer based on time + 3 seconds
# if paused
    # timeout and poll every 30 seconds

class App(rumps.App):
    def __init__(self):
        super(App, self).__init__('Loading...')
        self.icon = './resources/sleep_48x48.png'
        rumps.debug_mode(True)
        self.update_track()

    def update_track(self):
        scope = 'user-read-playback-state'
        username = 'misternate'
        redirect_uri = 'http://localhost:8888/callback/'
        token = util.prompt_for_user_token(username, scope, redirect_uri=redirect_uri)
        
        if token:
            self.icon = './resources/active_48x48.png'
            sp = spotipy.Spotify(auth=token)
            track_data = sp.current_user_playing_track()
            if track_data is not None:
                track = track_data['item']['name']
                
                artists = track_data['item']['artists']
                
                for artist in artists:
                    print(artist['name'])

                self.title = track
                time_left = int(track_data['item']['duration_ms'])/1000 - int(track_data['progress_ms'])/1000
                playing = track_data['is_playing']
                
                if playing is True:
                    print('PLAYING')
                    self.check_track_status(time_left)

            else:
                self.title = ' Not connected...'
        else:
            print("Can't get token for", username)
            self.icon = './resources/inactive_48x48.png'
    
    def check_track_status(self,duration):
        print(duration)
        t = Timer(duration, self.update_track).start()

if __name__ == '__main__':
    app = App()
    app.run()