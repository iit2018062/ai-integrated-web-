from flask import request, render_template
from flask.views import MethodView
import playlist_generator
import os


# this will help to call the playlist generator api
class Playlist(MethodView):
    def get(self):
        """

        :return: renders the playlist template
        """
        return render_template('playlist.html')

    def post(self):
        """

        :return: render the playlist_url template with url
        """
        prompt = request.form['Prompt']
        length = request.form['Length']
        name = request.form['Name']
        client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        client_secrete = os.environ.get('SPOTIFY_CLIENT_SECRET')
        redirect_uri = os.environ.get('REDIRECT_URI')

        try:
            playlist = playlist_generator.SpotifyPlaylist(client_id, client_secrete, redirect_uri, prompt, length, name)
            response = (playlist.get_playlist())
            return render_template('playlist_url.html',
                                   url="https://open.spotify.com/playlist/" + response.split(":")[-1])
        except:
            return render_template('error.html', url="sorry try again!")
