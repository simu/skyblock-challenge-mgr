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

from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from flaskext.login import LoginManager, login_user, logout_user, AnonymousUser, login_required
from user import load_users, save_users, User
from challenges import load_challenges, save_challenges

# skyblock version
version="2.1"

skyblock = Flask(__name__)
skyblock.secret_key = "seeeecret"
anoynmous = AnonymousUser()
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

@skyblock.route("/")
def index():
    skyblock.open_session(request)
    print session
    return render_template('index.jhtml', version=version)

@skyblock.route("/store.js")
def storejs():
    return render_template('store.jjs')

@login_required
@skyblock.route("/store", methods=['POST'])
def store():
    if request.method == "POST":
        challenges = session['challenges']
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

            save_challenges(skyblock, session['user'], challenges)

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
        import sha
        print request.form
        user = skyblock.users.get(request.form.get('username'), None)
        remember = request.form.get('remember', False)
        if remember is not False:
            remember = True
        password = request.form.get('password')
        user.auth_ok = sha.new(password).hexdigest() == user.password
        if user is None:
            flash("No such user")
        elif not login_user(user, remember):
            flash("login failed")
        else:
            session['user'] = user
            session['user_id'] = user.get_id()
            session['challenges'] = load_challenges(skyblock, user)
            session['logged_in'] = True
            r = make_response(redirect(url_for("index")))
            print session
            skyblock.save_session(session, r)
            return r
    return render_template('login.jhtml',version=version)

@skyblock.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST": # process registration form
        import sha
        if request.form.get('pw') != request.form.get('pw2'):
            flash("Password mismatch")
            skyblock.form = request.form
            return redirect(url_for("register"))
        user = User.register(skyblock.users, request.form.get('username'), sha.new(request.form.get('pw')).hexdigest())
        print user
        if user is None:
            flash("Username exists already")
            skyblock.form = request.form
            return redirect(url_for("register"))
        save_users(skyblock)
        if not login_user(user):
            flash("login failed")
            return redirect(url_for("login"))
        session['user'] = user
        session['user_id'] = user.get_id()
        session['challenges'] = load_challenges(skyblock, user)
        session['logged_in'] = True
        return redirect(url_for("index"))
    else:
        return render_template('register.jhtml', version=version)

@login_required
@skyblock.route("/logout")
def logout():
    logout_user()
    user = session.pop('user', None)
    session.pop('user_id', None)
    ch = session.pop('challenges', None)
    save_challenges(skyblock, user, ch)
    session.pop('logged_in', None)
    return redirect(url_for("index"))

def create_app():
    load_users(skyblock)
    return skyblock

if __name__ == "__main__":
    create_app().run(debug=True)
