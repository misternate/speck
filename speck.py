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
    # pylint: disable=too-many-instance-attributes
    """Main app with rumps sub"""

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
            "Devices"
        ]
        self.authorize_spotify()

        self.devices = [device for device in self.spotify.devices()["devices"]]
        for device in self.devices:
            self.menu["Devices"].add(device["name"])
            self.device_titles = self.menu["Devices"][device["name"]].title
            self.menu["Devices"][device["name"]].set_callback(self.select_device)

    def select_device(self, sender):
        device_title = sender.title

        for device in self.devices:
            if device["name"] == device_title:
                device_id = device["id"]
                self.device_selected = device_id
                for item in self.menu["Devices"]:
                    self.menu["Devices"][item].state = 0
                sender.state = 1
                print(device_id)

    def authorize_spotify(self) -> None:
        """Authorization method used in stand up and checks"""
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

    def __shorten_text(self, text: str) -> str:
        if len(text) > MAX_TRACK_LENGTH:
            text = text[0:MAX_TRACK_LENGTH] + "..."
        return text

    def __get_active_device(self) -> list:
        devices = self.spotify.devices()["devices"]
        active_devices = [device for device in devices if device["is_active"] is True]
        computer_device = [device["id"] for device in devices if device["type"].lower() == "computer"]

        """This checks for an active session and then falls back to
        your current computer, which is often the case."""
        # TODO Add multi-device support or add first active device to ini (https://stackoverflow.com/questions/8884188/how-to-read-and-write-ini-file-with-python3)
        if active_devices:
            active_device = active_devices[0]["id"]
        elif computer_device:
            active_device = computer_device[0]
        else:
            rumps.alert(
                title="No active sessions",
                message="Start playing music on one of your devices and Speck will start up!",
            )
            active_device = None

        return active_device

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
        self.state = state

        if self.state != self.state_prev:
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

    @rumps.clicked("Pause/Play")
    def pause_play_track(self, sender) -> None:
        """Pause or play track based on playback status"""
        try:
            if self.track_data is None or self.track_data["is_playing"] is False:
                # self.spotify.transfer_playback(device_id=self.__get_active_device(), force_play=True)
                self.spotify.start_playback(self.__get_active_device())
            else:
                self.spotify.pause_playback()
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
        """Previous track"""
        try:
            self.spotify.previous_track()
            time.sleep(0.25)
            self.update_track()
        except SpotifyException:
            self.authorize_spotify()

    @rumps.timer(UPDATE_INTERVAL)
    def update_track(self, sender=None) -> None:
        """Update the track data listed in menubar"""
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
                    band.append(self.__shorten_text(artist["name"]))
                    track = self.__shorten_text(self.track_data["item"]["name"])
                band = ", ".join(band)

                if is_playing is True:
                    time_left = (
                        int(self.track_data["item"]["duration_ms"]) / 1000
                        - int(self.track_data["progress_ms"]) / 1000
                    )  # currently unused; TBU for better tracking without polling

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
