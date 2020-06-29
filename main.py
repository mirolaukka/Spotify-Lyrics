import spotipy
import lyricsgenius
import sys
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtWidgets import * 
from PyQt5 import QtCore 
from PyQt5.QtGui import * 
from time import sleep
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth


# Setup Spotify API Side

# If you need help with these, visit https://developer.spotify.com/documentation/web-api/
CLIENT_ID = "CHANGE THIS" # Your client_id from spotify app
CLIENT_SECRET = "CHANGE THIS" # Your client_secret from spotify app

OAUTH_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
OAUTH_TOKEN_URL = 'https://accounts.spotify.com/api/token'
REDIRECT_URI = 'CHANGE THIS' # Your redirect uri from spotify app

scope = "user-read-playback-state"
username = "CHANGE THIS" # Your spotify username

auth_manager = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri = REDIRECT_URI, username=username, scope=scope)
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, auth_manager=auth_manager)


# Genius
# To get an API token, visit https://genius.com/api-clients and log in/sign up
GENIUS_API_TOKEN = "CHANGE THIS"
genius = lyricsgenius.Genius(GENIUS_API_TOKEN)



class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Spotify Lyrics')
        self.setGeometry(100,100,600,800) # (x,y,w,h)

        formLayout = QtWidgets.QFormLayout()
        groupBox = QtWidgets.QGroupBox("")


        self.lyrics = QtWidgets.QLabel("", self)
        self.title = QtWidgets.QLabel("Start listening to music on spotify", self)
        formLayout.addRow(self.title)

        formLayout.addRow(self.lyrics)
        
        #self.lyrics.move(10,20)
        self.lyrics.alignment()
        self.lyrics.setStyleSheet("font-size:16px;") #css
        self.title.setStyleSheet("font-size:24px;") #css
        self.lyrics.setWordWrap(True)
        self.lyrics.resize(600,800)
        groupBox.setLayout(formLayout)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(groupBox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(800)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(scroll)
        self.show()

    def update_lyrics(self, song_name, current_playback):
        song = genius.search_song(song_name, current_playback[0]['name'], False)
        if song.lyrics:
            self.title.setText(f"\"{song_name}\" by {', '.join([x['name'] for x in current_playback])}<hr>")
            self.lyrics.setText(song.lyrics)
        else:
            raise ValueError('Lyrics not found')
        
    def update_lyrics_failed(self, song_name, current_playback):
        self.title.setText(f"\"{song_name}\" by {', '.join([x['name'] for x in current_playback])}<hr>")
        self.lyrics.setText("Couldn't find lyrics for this song")

if __name__ == "__main__":

    App = QtWidgets.QApplication([])

    window = Window()

    last_playback = {'item':{'name':'asd'}} # Placeholder JSON to pass the first check in update()


    def update():
        global last_playback
        current_playback = sp.current_playback() # Get the current playback of the user

        if(current_playback): # Check if we get a song from sp.current_playback
            try:
                if current_playback['item']['name'] != last_playback['item']['name']: # Does not match the last get from current_playback()

                    artists = ', '.join([x['name'] for x in current_playback['item']['artists']])
                    song_name = current_playback['item']['name']
                    try:
                        window.update_lyrics(song_name, current_playback['item']['artists'])
                    except ValueError:
                        window.update_lyrics_failed(song_name, current_playback['item']['artists'])
                        print(f'Couldn\'t find lyrics for: {song_name} by {artists}')
                        

                    last_playback = current_playback
            except TypeError:
                pass
        else:
            pass

    # Loop update() every 2 seconds
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(2000)  # every 2000 milliseconds

sys.exit(App.exec_())
