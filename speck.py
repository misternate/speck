#!/usr/bin/env python3
import time
import webbrowser
from configparser import ConfigParser

import spotipy
from spotipy import util
from spotipy import SpotifyException
import rumps

# Config
config = ConfigParser()
config.read("speck.ini")

# Config > Secrets
CLIENT_ID = config["secrets"]["client_id"]
CLIENT_SECRET = config["secrets"]["client_secret"]
USERNAME = config["secrets"]["username"]

# Config > Settings
DEBUG = config["settings"]["debug"]
REDIRECT_URI = config["settings"]["redirect_uri"]
SCOPE = config["settings"]["scope"]
MAX_TRACK_LENGTH = int(config["settings"]["max_track_length"])
MAX_RETRIES = int(config["settings"]["max_retries"])
UPDATE_INTERVAL = float(config["settings"]["update_interval"])


class App(rumps.App):
    rumps.debug_mode(DEBUG)

    def __init__(self) -> None:
        super(App, self).__init__("Speck")
        self.token = ""
        self.spotify = ""
        self.state_prev = ""
        self.state = ""
        self.pause_count = 0
        self.track_data = {}
        self.device_selected = ""
        self.menu = [
            "Pause/Play",
            None,
            "Next",
            "Previous",
            None,
            "Save to your Liked Songs",
            None,
            "Track Info",
            None,
            "Devices",
            None,
        ]
        self.authorize_spotify()
        self.populate_menu_device()

    """ Devices """

    def populate_menu_device(self):
        self.devices = [device for device in self.spotify.devices()["devices"]]
        for device in self.devices:
            self.menu["Devices"].add(device["name"])
            self.device_titles = self.menu["Devices"][device["name"]].title
            self.menu["Devices"][device["name"]].set_callback(self.__set_active_device)

            if device["is_active"]:
                self.menu["Devices"][device["name"]].state = 1

    def __get_active_device(self) -> list:
        devices = self.spotify.devices()["devices"]
        active_devices = [device for device in devices if device["is_active"] is True]

        if self.device_selected:
            active_device = self.device_selected
        elif active_devices:
            active_device = active_devices[0]["id"]
        else:
            rumps.alert(
                title="No active devices",
                message="Select a device from the Devices menu.",
            )
            active_device = None

        return active_device

    def __set_active_device(self, sender):
        # TODO should also check on id from __get_active_device() on initial load and then set state
        device_title = sender.title
        for device in self.devices:
            if device["name"] == device_title:
                device_id = device["id"]
                self.device_selected = device_id
                for item in self.menu["Devices"]:
                    self.menu["Devices"][item].state = 0
                sender.state = 1
                self.pause_play_track(sender)

    """ Spotify """

    def authorize_spotify(self) -> None:
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

    """ Spotify > Functions """

    def __set_saved_track(self, track_id: str) -> None:
        menu_item = self._menu["Save to your Liked Songs"]

        if self.spotify.current_user_saved_tracks_contains([track_id])[0] is True:
            menu_item.title = "Remove from your Liked Songs"
        else:
            menu_item.title = "Save to your Liked Songs"
            menu_item.set_callback(self.add_remove_saved_track)

    def __get_playback_state(self) -> None:
        menu_item = self._menu["Pause/Play"]

        if self.track_data["is_playing"] is True:
            menu_item.title = "Pause"
        else:
            menu_item.title = "Play"
            menu_item.set_callback(self.pause_play_track)

    def __set_menu_playback_state(
        self, state: str, track: str = None, band: str = None
    ) -> None:
        if state != self.state_prev:
            self.icon = f"./resources/{state}.png"
        if state == "active":
            self.title = track + " · " + str(band)
            self.pause_count = 0
        elif state == "paused":
            self.title = track + " · " + str(band)
        else:
            self.title = str.capitalize(f"{state}")
        if self.state and self.state_prev == "paused":
            self.pause_count += 1

    """ Utils """

    def __shorten_text(self, text: str) -> str:
        if len(text) > MAX_TRACK_LENGTH:
            text = text[0:MAX_TRACK_LENGTH] + "..."
        return text
    
    def __get_bands(self, artists: str) -> str:
        band = []
        for artist in artists:
            band.append(self.__shorten_text(artist))
        band = ", ".join(band)

        return band

    """ Rumps Player """

    @rumps.clicked("Pause/Play")
    def pause_play_track(self, sender) -> None:
        """Pause or play track based on playback status"""
        try:
            if self.track_data is None:
                rumps.alert(
                    title="No active songs",
                    message="Play a song from the Spotify app.",
                )
            elif self.state == "active":
                self.spotify.pause_playback()
            else:
                self.spotify.transfer_playback(device_id=self.__get_active_device())
            self.update_track(self)
        except SpotifyException:
            self.authorize_spotify()

    @rumps.clicked("Next")
    def next_track(self, sender) -> None:
        """Next track"""
        try:
            self.spotify.next_track()
            time.sleep(0.25)
            self.update_track()
        except SpotifyException:
            self.authorize_spotify()

    @rumps.clicked("Previous")
    def prev_track(self, sender) -> None:
        try:
            self.spotify.previous_track()
            time.sleep(0.25)
            self.update_track()
        except SpotifyException:
            self.authorize_spotify()

    @rumps.clicked("Track Info")
    def open_browser(self, sender) -> None:
        """Open web browser to search track information"""
        webbrowser.open(
            f'https://google.com/search?q={self.track_data["item"]["name"]}+{self.track_data["item"]["artists"][0]["name"]}'
        )

    @rumps.clicked("Save to your Liked Songs")
    def add_remove_saved_track(self, sender) -> None:
        "Add or remove playing track to Liked playlist"
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

    """ Track Update """

    @rumps.timer(UPDATE_INTERVAL)
    def update_track(self, sender=None) -> None:
        if self.token:
            try:
                self.track_data = self.spotify.current_user_playing_track()
            except SpotifyException:
                self.authorize_spotify()
                self.update_track()

            if self.track_data is not None:
                is_playing = self.track_data["is_playing"]
                track_id = self.track_data["item"]["id"]
                track = self.__shorten_text(self.track_data["item"]["name"])
                band = self.__get_bands([self.track_data["item"]["artists"][0]["name"]])

                self.__get_playback_state()
                self.__set_saved_track(track_id)

                if is_playing is True:
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
