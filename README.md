<h1 align="center">
    <br/>
    <img src="https://user-images.githubusercontent.com/1675353/103448666-531f5380-4c62-11eb-8249-fce021c897cb.png" alt="Speck logo" width="96px">
    <br/>
    Speck
    <br/>
</h1>

Speck is a little Spotify Mac menubar app that makes it easy to see what's playing at a glance, navigate your playlist, and like songs.

![Speck demo](https://user-images.githubusercontent.com/1675353/103448779-eefd8f00-4c63-11eb-89e9-7e61a33bda50.png)

## Launching the app
There's very little that's needed to get Speck running. To build locally:

### Install dependencies
```bash
$ pip install -r requirements.txt
```

### Add your Spotify credentials
These can be obtained from [Spotify Developer Dashboard](https://developer.spotify.com)).
```python
USERNAME = 'your username'
CLIENT_SECRET = 's0m3s3cr3t'
CLIENT_ID = 'cl13ntid'
```
### Build standalone app (optional)
Your .app will be built to `dist` in your Speck directory.
```bash
$ python build_app.py py2app
```

### License
Speck is provided under the [MIT License](https://github.com/misternate/speck/blob/master/LICENSE).

