from flask import render_template
from flask.views import MethodView


class Error(MethodView):
    def get(self):
        return render_template('error.html',url="hehe")


