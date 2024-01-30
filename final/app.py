import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from landing import Landing
from playlist import Playlist

# from playlist import PlaylistUrl
load_dotenv(dotenv_path='config.env')

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.add_url_rule('/',
                 view_func=Landing.as_view('landing'),
                 methods=["GET"])

app.add_url_rule('/playlist',
                 view_func=Playlist.as_view('playlist'),
                 methods=['GET', 'POST'])


if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 8080)),host='0.0.0.0',debug=True)
