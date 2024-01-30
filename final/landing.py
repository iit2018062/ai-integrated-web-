from flask import render_template
from flask.views import MethodView


class Landing(MethodView):
    def get(self):
        return render_template('landing.html')
