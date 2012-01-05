#!/usr/bin/python
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

from flask import Flask, render_template, request, redirect, url_for
from flaskext.login import LoginManager, login_user, logout_user, AnonymousUser
from user import load_users, save_users, User
import pickle

# skyblock version
version="2.1"

skyblock = Flask(__name__)
skyblock.secret_key = "seeeecret"
skyblock.error_msg = None
anoynmous = AnonymousUser()
skyblock.current_user = anoynmous
login_mgr = LoginManager()
login_mgr.setup_app(skyblock)

# setup user loader for login manager
@login_mgr.user_loader
def load_user(userid):
    User.get(skyblock.users, userid)

# make open_instance_resource Flask 0.7 compatible
open_instance_resource = None
if 'open_instance_resource' not in dir(skyblock):
    from os.path import join, abspath, dirname
    package = abspath(dirname(__file__))
    skyblock.open_instance_resource = lambda file, mode="rb": \
        open(join(package, "instance", file), mode)



class Challenge(object):
    def __init__(self, id, desc, amount):
        self.id = id
        self.desc = desc
        self.current_amount = 0
        self.amount = amount
        pass

    def __str__(self):
        return str(self.id+1) + ") " + self.desc

    def __repr__(self):
        return self.__str__() + " [" + str(self.completed) + "]" + "(" + \
                str(self.current_amount) + "/" + str(self.amount) + ")" if self.has_amount else ""

    @property
    def completed(self):
        return self.current_amount >= self.amount

    @property
    def has_amount(self):
        return self.amount > 1


challenges=[]
# read challenge descriptions
def init_challenges():
    with skyblock.open_resource("challenges.txt") as cfile:
        chtxts = map(str.strip, cfile.readlines())
    for i in xrange(len(chtxts)):
        text,amount = chtxts[i].split('|')
        challenges.append(Challenge(i, text, int(amount)))

def save_challenges():
    data = [ c.current_amount for c in challenges ]
    with skyblock.open_instance_resource("store.txt", "w") as f:
        pickle.dump(data, f)

def load_challenges():
    try:
        with skyblock.open_instance_resource("store.txt") as f:
            data = pickle.load(f)
    except:
        data = [0] * len(challenges)
    for c,v in zip(challenges, data):
        c.current_amount = v

@skyblock.route("/favicon.ico")
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

@skyblock.route("/")
def index():
    return render_template('index.jhtml', challenges=challenges, version=version,
                completed=len([c for c in challenges if c.completed ]), total=len(challenges),
                error_msg=None, logged_in=skyblock.current_user.is_authenticated())

@skyblock.route("/store.js")
def storejs():
    return render_template('store.jjs')

@skyblock.route("/store", methods=['POST'])
def store():
    if request.method == "POST":
        try:
            data = map(int, request.data.split(',')[:-1])
            if len(data) != len(challenges):
                return "size mismatch"
            fades=[]
            for c,v in zip(challenges, data):
                old_completed = c.completed
                c.current_amount = v
                if old_completed != c.completed:
                    fades.append("%d=%.1f"%(c.id, 0.4 if c.completed else 1))

            save_challenges()

            fades.insert(0, str(len([ c for c in challenges if c.completed ])))
            fades.insert(0, "Saving succeeded")
            return ",".join(fades)
        except Exception, e:
            print e
            return str(e)
    else:
        return "Only accepts POST"

@skyblock.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST": # process login form
        skyblock.error_msg = None
        import sha
        user = skyblock.users.get(request.form.get('username'), None)
        print skyblock.users
        if user is None:
            skyblock.error_msg = "No such user"
            return redirect(url_for("login"))
        password = request.form.get('password')
        pwhash = sha.new(password).hexdigest()
        if user.password != pwhash:
            skyblock.error_msg = "Wrong password"
            return redirect(url_for("login"))
        #remember = request.form.get('remember', False)
        remember = False
        if not login_user(user, remember):
            skyblock.error_msg = "login failed"
            return redirect(url_for("login"))
        skyblock.current_user = user
        return redirect(url_for("index"))
    else:
        error_msg = skyblock.error_msg
        skyblock.error_msg = None
        return render_template('login.jhtml',version=version,  error_msg=error_msg)

@skyblock.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST": # process registration form
        import sha
        if request.form.get('pw') != request.form.get('pw2'):
            skyblock.error_msg = "Password mismatch"
            skyblock.form = request.form
            return redirect(url_for("register"))
        print skyblock.users
        user = User.register(skyblock.users, request.form.get('username'), sha.new(request.form.get('pw')).hexdigest())
        print user
        if user is None:
            skyblock.error_msg = "Username exists already"
            skyblock.form = request.form
            return redirect(url_for("register"))
        save_users(skyblock)
        if not login_user(user):
            skyblock.error_msg = "login failed"
            return redirect(url_for("login"))
        skyblock.current_user = user
        return redirect(url_for("index"))
    else:
        error_msg = skyblock.error_msg
        skyblock.error_msg = None
        return render_template('register.jhtml', version=version, error_msg=error_msg)

@skyblock.route("/logout")
def logout():
    logout_user()
    skyblock.current_user = anoynmous
    return redirect(url_for("index"))

def create_app():
    init_challenges()
    #load_challenges()
    load_users(skyblock)
    return skyblock

if __name__ == "__main__":
    create_app().run(debug=True)
