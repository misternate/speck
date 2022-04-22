<h1 align="center">
    <br/>
    <img src="https://user-images.githubusercontent.com/1675353/103448666-531f5380-4c62-11eb-8249-fce021c897cb.png" alt="Speck logo" width="96px">
    <br/>
    Speck
    <br/>
</h1>

Speck is a little Spotify Mac menubar app that makes it easy to see what's playing at a glance, navigate your playlist, like songs, and find track information.

![Speck demo](https://user-images.githubusercontent.com/1675353/104856939-d71c4100-58da-11eb-8fd2-2246db055fab.gif)

# Launching the app
There's very little that's needed to get Speck running. To build locally:

## Install dependencies
```bash
$ pip install -r requirements.txt
```

## Add your Spotify credentials
Credentials and configs are stored in `speck.ini`. If you do not have credentials, you can obtain them from the [Spotify Developer Dashboard](https://developer.spotify.com).
```python
client_id = spotify_client_id
client_secret = spotify_client_secret
username = spotify_username
```
# Build standalone app (optional)
Note: You must add your secrets to `speck.ini`. Your .app will be built to `dist` in your repo directory.
```bash
$ python build_app.py py2app
```

### License
Speck is provided under the [MIT License](https://github.com/misternate/speck/blob/master/LICENSE).

