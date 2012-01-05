from flaskext.login import UserMixin
import pickle

class User(UserMixin):
    def __init__(self, name, password):
        self.name = name
        self.password = password

    def get_id(self):
        return unicode(self.name)

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
        u = User(name, password, users)
        users[name] = u
        return u

def load_users(app):
    try:
        with app.open_instance_resource("users.txt") as u:
            users = pickle.load(u)
            app.users = users
    except:
        app.users = dict()

def save_users(app):
    try:
        with app.open_instance_resource("users.txt", "w") as u:
            pickle.dump(app.users, u)
    except:
        raise
