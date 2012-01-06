from flaskext.login import UserMixin
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

    @classmethod
    def get(klass, users, userid):
        return users[userid]

    @classmethod
    def register(klass, users, name, password):
        print users
        print name
        print password
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
            users = map(User, pickle.load(u))
            app.users = dict(zip([ x.name for x in users ], users))
            print app.users
    except:
        app.users = dict()

def save_users(app):
    try:
        with app.open_instance_resource("users.txt", "w") as u:
            pickle.dump([ (x.name, x.password) for x in app.users.values() ], u)
    except:
        raise
