import openai
import json
import spotipy
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path='config.env')
openai.api_key = os.environ.get('OPENAI_API_KEY')


class SpotifyPlaylist:

    def __init__(self, client_id, client_secret, redirect_uri, prompt, length=10, name=None):
        """
         make SpotifyPlaylist object.
        :param prompt: The prompt for playlist.
        :param length: The length for playlist (default  10).
        :param name: The name for playlist (default is the provided prompt).
        :param client_id: Spotify API client ID.
        :param client_secret: Spotify API client secret.
        :param redirect_uri: Redirect URI for Spotify authorization.
        """
        self.client_secret = client_secret
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.prompt = prompt
        self.length = int(length)
        self.name = name if name is not None else prompt
        self.gpt_tracks = []
        self.blacklisted_artists = set() # artist are blacklisted
        self.blacklisted_songs = set() # songs that are blacklisted
        self.songs_in_playlist = set()

    def playlist_generator_gpt(self, gpt_model='t-3.5-turbogp'):
        """
        Playlist generation .
        :param gpt_model: default is 'gpt-3.5-turbo'.
        :return: A list of dictionaries representing songs and artists in the playlist.
        """
        example_for_playlist = """
        [
         {"song": "Bohemian Rhapsody", "artist": "Queen"},
         {"song": "Hotel California", "artist": "Eagles"},
         {"song": "Smells Like Teen Spirit", "artist": "Nirvana"},
         {"song": "Billie Jean", "artist": "Michael Jackson"},
         {"song": "Stairway to Heaven", "artist": "Led Zeppelin"}
         
         ]
         """
        user_content = f"Give me {self.length} songs matching this prompt: {self.prompt}"
        blacklist_songs = str(self.blacklisted_songs.union(self.songs_in_playlist))
        if blacklist_songs:
            user_content += f", which are not part of this list: {blacklist_songs}"
        self.messages = [
            {"role": "system", "content": """Your are a Spotify assistant helping the user create music playsists.
            You should generate a list of artists and songs you consider fit the text prompt.
            The output shoud be a JSON array formatted like this: {"song": <song_title>, "artist": <artist_name>}.
            Do not return anything else than the JSON array."""
             },
            {"role": "user", "content": "Give me 5 very sad songs"},
            {"role": "assistant", "content": example_for_playlist},
            {"role": "user", "content": user_content}
        ]
        gpt_response = openai.ChatCompletion.create(
            messages=self.messages,
            model=gpt_model,
            max_tokens=int(self.length * 20 + 250)
        )
        response = []
        try:
            response = json.loads(gpt_response["choices"][0]["message"]["content"])
        except json.decoder.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
        return response

    def login_to_spotify(self):
        """
        login into the user's spotify account user client id and client secret

        """
        self.sp = spotipy.Spotify(
            auth_manager=spotipy.SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope='user-read-playback-state,user-modify-playback-state,playlist-modify-private'
            )
        )
        self.current_user = self.sp.current_user()
        assert self.current_user is not None

    def get_playlist(self):
        """
        Creates a new Spotify playlist based on the provided data, adds songs into it,
        and returns the URI of the created playlist.
        :return: The URI of the newly created playlist
        """
        # Log in to Spotify
        self.login_to_spotify()

        # Retrieve all existing playlists of the user
        all_playlists = self.sp.user_playlists(self.current_user['id'])
        playlist_names = [p['name'].lower() for p in all_playlists['items']]
        # Generate a unique playlist name
        new_playlist_name = f'_{self.name}'
        playlist_name = new_playlist_name
        id = 1
        while playlist_name.lower() in playlist_names:
            id += 1
            playlist_name = f'{new_playlist_name} {str(id)}'
        # Create a new playlist on Spotify
        self.playlist = self.sp.user_playlist_create(self.current_user['id'], public=False, name=playlist_name)
        # Add songs into the created playlist
        self.add_songs_into_playlist()
        # Return the URI of the created playlist
        return self.playlist['uri']

    def add_songs_into_playlist(self):
        """
        Fills the Spotify playlist with songs generated using ChatGPT.
        The method generates a playlist of songs using the ChatGPT model.
        It extracts information about each song from the ChatGPT response and searches for
        the corresponding track on Spotify. The identified tracks are then added to the Spotify playlist.
        Note: The `gpt_tracks` attribute should be populated before calling this method.
        """
        # here the songs will be filled to the playlist using chat gpt
        self.gpt_tracks = self.playlist_generator_gpt(gpt_model='gpt-3.5-turbo')
        # extracting songs out of chatgpt response
        for i in self.gpt_tracks:
            artist_name = i['artist']  # artist names
            song_name = i['song']
            query = f"{artist_name} {song_name}"
            # Search for the track on Spotify
            search_results = self.sp.search(q=query, type='track', limit=10)
            song = search_results['tracks']['items'][0]
            track = self.sp.track(song['id'])
            track_id = track['id']
            # Add the track to the Spotify playlist
            self.sp.user_playlist_add_tracks(self.current_user['id'], self.playlist['id'], [track_id])





