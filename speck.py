#!/usr/bin/env python3

import sys
import os

import spotipy
import spotipy.util as util
from spotipy import SpotifyException
import rumps
# import requests only need for album art

USERNAME = 'misternate'
REDIRECT_URI = 'http://localhost:8888/callback/'
SCOPE = 'user-read-playback-state,user-library-modify,user-modify-playback-state'
CLIENT_SECRET = ''
CLIENT_ID = ''
MAX_TRACK_LENGTH = 32
MAX_RETRIES = 24

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
        super(App, self).__init__('Speck')
        self.token = ''
        self.spotify = ''
        self.state_prev = ''
        self.state = ''
        self.pause_count = 0
        self.track_data = {}
        self.menu = [
            'Like',
            None,
            'Pause/Play',
            'Next',
            'Previous',
            'Refresh',
            None
            ]
        self.authorize_spotify()

        # rumps.debug_mode(True)

    def authorize_spotify(self):
        self.token = util.prompt_for_user_token(USERNAME, scope=SCOPE, redirect_uri=REDIRECT_URI, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        self.spotify = spotipy.Spotify(auth=self.token, retries=MAX_RETRIES, status_retries=MAX_RETRIES)
        self.update_track()        
        
    # def download_album_art(self, url):
    #     r = requests.get(url, allow_redirects=True)
    #     open('./resources/artist.jpg', 'wb').write(r.content)

    def __shorten_text(self, string):
        if len(string) > MAX_TRACK_LENGTH:
            string = string[0:MAX_TRACK_LENGTH] + '...'
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
        try:
            # self.download_album_art(self.track_data['item']['album']['images'][2]['url'])
            # rumps.notification(icon='./resources/artist.jpg', title='Saved to your liked songs', subtitle=None, message=f'{self.track_data["item"]["artists"][0]["name"]} - {self.track_data["item"]["name"]}')

            rumps.notification(title='Saved to your liked songs', subtitle=None, message=f'{self.track_data["item"]["artists"][0]["name"]} - {self.track_data["item"]["name"]}')
            track_id = self.track_data['item']['id']
            self.spotify.current_user_saved_tracks_add(tracks=[track_id])
        except SpotifyException:
            self.authorize_spotify()

    @rumps.clicked('Pause/Play')
    def pause_play_track(self, sender):
        try:
            if self.track_data['is_playing'] == False or self.track_data['is_playing'] is None:
                self.spotify.start_playback()
            else:
                self.spotify.pause_playback()
            self.update_track(self)
        except SpotifyException:
            self.authorize_spotify()

    @rumps.clicked('Next')
    def next_track(self, sender):
        try:
            self.spotify.next_track()
            self.update_track()
        except SpotifyException:
            self.authorize_spotify()

    @rumps.clicked('Previous')
    def prev_track(self, sender):
        try:
            self.spotify.previous_track()
            self.update_track()
        except SpotifyException:
            self.authorize_spotify()

    @rumps.clicked('Refresh')
    def restart(self, sender=None):
        os.execv(__file__, sys.argv)
    
    @rumps.timer(10)
    def update_track(self, sender=None):
        # 1. Break up auth and update_track() 2.Add Try/Except https://github.com/plamere/spotipy/issues/83 on update_track() if auth fails auth function
        # 3. Look at using OAuth instead :/
        
        if self.token:
            try:
                self.track_data = self.spotify.current_user_playing_track()
            except SpotifyException:
                self.authorize_spotify()
                self.update_track()
                
                
            if self.track_data is not None:
                is_playing = self.track_data['is_playing']
                
                if is_playing is True:
                    time_left = int(self.track_data['item']['duration_ms'])/1000 - int(self.track_data['progress_ms'])/1000
                    self.state_prev = self.state
                    artists = self.track_data['item']['artists']
                    band = []
        
                    for artist in artists:  
                        band.append(artist['name'])
                    band = self.__shorten_text(', '.join(band))
                    track = self.__shorten_text(self.track_data['item']['name'])

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