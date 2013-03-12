#
# Copyright (c) 2012 Simon Gerber <gesimu@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from flask_login import UserMixin
import pickle
from util import ComparableMixin

class User(UserMixin, ComparableMixin):
    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.auth_ok = False

    def get_id(self):
        return unicode(self.name)

    def is_authenticated(self):
        return self.auth_ok

    @property
    def challenge_file(self):
        return "store-" + self.name + ".txt"

    @property
    def prefs_file(self):
        return "prefs-" + self.name + ".txt"

    @classmethod
    def get(klass, users, userid):
        return users[userid]

    @classmethod
    def register(klass, users, name, password):
        if users.has_key(name):
            return None
        u = User(name, password)
        users[name] = u
        return u

    def __repr__(self):
        return "[ " + self.name + " (" + str(self.auth_ok) + ") ]"

    def __lt__(self, other):
        return self.__hash__() < other.__hash__()

    def __hash__(self):
        return hash(self.name)

def load_users(app):
    try:
        with app.open_instance_resource("users.txt") as u:
            users = pickle.load(u)
            app.users = dict( [ (name, User(name, password)) for (name, password) in users ] )
    except Exception as e:
        print e
        app.users = dict()

def save_users(app):
    try:
        with app.open_instance_resource("users.txt", "w") as u:
            pickle.dump([ (x.name, x.password) for x in app.users.values() ], u)
    except:
        raise
