from setuptools import setup

APP = ["speck.py"]
DATA_FILES = [
    "./resources",
    "./resources/active.png",
    "./resources/error.png",
    "./resources/paused.png",
    "./resources/sleeping.png",
    "speck.ini",
]
OPTIONS = {
    "argv_emulation": True,
    "iconfile": "speck.icns",
    "plist": {
        "LSUIElement": True,
    },
    "packages": ["rumps"],
}


setup(
    name="Speck",
    app=APP,
    data_files=DATA_FILES,
    options={
        "py2app": OPTIONS,
    },
    setup_requires=["py2app"],
)
