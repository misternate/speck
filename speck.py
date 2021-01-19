#!/usr/bin/env python3
import time

import spotipy
import spotipy.util as util
from spotipy import SpotifyException
import rumps

REDIRECT_URI = "http://localhost:8888/callback/"
SCOPE = "user-read-playback-state,user-library-modify,user-modify-playback-state,user-library-read"
MAX_TRACK_LENGTH = 32
MAX_RETRIES = 24
UPDATE_INTERVAL = 5

USERNAME = ""
CLIENT_ID = ""
CLIENT_SECRET = ""

class App(rumps.App):
    rumps.debug_mode(True)

    def __init__(self):
        super(App, self).__init__("Speck")
        self.token = ""
        self.spotify = ""
        self.state_prev = ""
        self.state = ""
        self.pause_count = 0
        self.track_data = {}
        self.menu = [
            "Pause/Play",
            None,
            "Next",
            "Previous",
            None,
            "Save to your Liked Songs",
            None,
        ]
        self.authorize_spotify()

    def authorize_spotify(self):
        self.token = util.prompt_for_user_token(
            USERNAME,
            scope=SCOPE,
            redirect_uri=REDIRECT_URI,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
        )
        self.spotify = spotipy.Spotify(
            auth=self.token, retries=MAX_RETRIES, status_retries=MAX_RETRIES
        )

        self.update_track()

    def __shorten_text(self, track_title):
        if len(track_title) > MAX_TRACK_LENGTH:
            track_title = track_title[0:MAX_TRACK_LENGTH] + "..."
        return track_title

    def __get_active_device(self):
        devices = self.spotify.devices()["devices"]
        active_devices = [device for device in devices if device["is_active"] is True]

        if active_devices:
            active_device = active_devices[0]["id"]
        else:
            rumps.alert(
                title="No active sessions",
                message="Start playing music on one of your devices and Speck will start up!",
            )
            active_device = None

        return active_device

    def __set_saved_track(self, track_id):
        menu_item = self._menu["Save to your Liked Songs"]

        if self.spotify.current_user_saved_tracks_contains([track_id])[0] is True:
            menu_item.title = "Remove from your Liked Songs"
        else:
            menu_item.title = "Save to your Liked Songs"
            menu_item.set_callback(self.add_remove_saved_track)

    def __get_playback_state(self):
        menu_item = self._menu["Pause/Play"]

        if self.track_data["is_playing"] is True:
            menu_item.title = "Pause"
        else:
            menu_item.title = "Play"
            menu_item.set_callback(self.pause_play_track)

    def __set_menu_playback_state(self, state, track=None, band=None):
        self.state = state

        if self.state != self.state_prev:
            self.icon = f"./resources/{state}.png"
        if state == "active":
            self.title = track  + " · " + str(band)
            self.pause_count = 0
        elif state == "paused":
            self.title = track  + " · " + str(band)
        else:
            self.title = str.capitalize(f"{state}")
        if self.state and self.state_prev == "paused":
            self.pause_count += 1

    @rumps.clicked("Save to your Liked Songs")
    def add_remove_saved_track(self, sender):
        track_id = self.track_data["item"]["id"]
        if self.spotify.current_user_saved_tracks_contains([track_id])[0] is False:
            try:
                self.spotify.current_user_saved_tracks_add(tracks=[track_id])
                rumps.notification(
                    title="Saved to your liked songs",
                    subtitle=None,
                    message=f'{self.track_data["item"]["artists"][0]["name"]} - {self.track_data["item"]["name"]}',
                )
            except SpotifyException:
                self.authorize_spotify()
        else:
            self.spotify.current_user_saved_tracks_delete([track_id])

    # TODO fix nonetype error on 115
    @rumps.clicked("Pause/Play")
    def pause_play_track(self, sender):
        try:
            if self.track_data is None or self.track_data['is_playing'] is False:
                self.spotify.start_playback(self.__get_active_device())
            else:
                self.spotify.pause_playback()
            self.update_track(self)
        except SpotifyException:
            self.authorize_spotify()

    @rumps.clicked("Next")
    def next_track(self, sender):
        try:
            self.spotify.next_track()
            time.sleep(0.25)
            self.update_track()
        except SpotifyException:
            self.authorize_spotify()

    @rumps.clicked("Previous")
    def prev_track(self, sender):
        try:
            self.spotify.previous_track()
            time.sleep(0.25)
            self.update_track()
        except SpotifyException:
            self.authorize_spotify()

    @rumps.timer(UPDATE_INTERVAL)
    def update_track(self, sender=None):
        if self.token:
            try:
                self.track_data = self.spotify.current_user_playing_track()
            except SpotifyException:
                self.authorize_spotify()
                self.update_track()

            if self.track_data is not None:
                is_playing = self.track_data["is_playing"]
                artists = self.track_data["item"]["artists"]
                track_id = self.track_data["item"]["id"]
                band = []

                self.__get_playback_state()
                self.__set_saved_track(track_id)

                for artist in artists:
                    band.append(artist["name"])
                band = self.__shorten_text(", ".join(band))
                track = self.__shorten_text(self.track_data["item"]["name"])

                if is_playing is True:
                    time_left = (
                        int(self.track_data["item"]["duration_ms"]) / 1000
                        - int(self.track_data["progress_ms"]) / 1000
                    )
                    self.state_prev = self.state
                    self.state = "active"

                else:  # Spotify is Paused
                    self.state_prev = self.state
                    self.state = "paused"

                self.__set_menu_playback_state(self.state, track, band)

            else:
                self.state = "sleeping"
                self.__set_menu_playback_state(self.state)
        else:
            self.__set_menu_playback_state("error")


if __name__ == "__main__":
    app = App()
    app.run()
