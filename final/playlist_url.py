from flask import render_template
from flask.views import MethodView


class PlaylistUrl(MethodView):
    def get(self):
        return render_template('playlist_url.html',url="hehe")


