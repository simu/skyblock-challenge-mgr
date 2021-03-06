#!/usr/bin/python
#
# Copyright (c) 2012-2013 Simon Gerber <gesimu@gmail.com>
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

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from user import load_users, save_users, User, get_session_user, make_session_user
from challenges import load_challenges, get_challenges
from preferences import load_preferences, Preferences, get_session_prefs
from util import update_session, login_successful

# mc_challenge_mgr version
version="1.0"

# supported maps
avail_maps = [ "skyblock", "bp-ender-island" ]

mc_challenge_mgr = Flask(__name__)
mc_challenge_mgr.secret_key = "seeeecret"
login_mgr = LoginManager()
login_mgr.setup_app(mc_challenge_mgr)

# setup user loader for login manager
@login_mgr.user_loader
def load_user(userid):
    if userid not in mc_challenge_mgr.users:
        print ">>>>> load_user(%s) -> users = %r... reloading users" % (userid, mc_challenge_mgr.users)
        load_users(mc_challenge_mgr)
    u = User.get(mc_challenge_mgr.users, userid)
    if u is None:
        logout_impl()

# make open_instance_resource Flask 0.7 compatible
open_instance_resource = None
if 'open_instance_resource' not in dir(mc_challenge_mgr):
    from os.path import join, abspath, dirname
    package = abspath(dirname(__file__))
    mc_challenge_mgr.open_instance_resource = lambda file, mode="rb": \
        open(join(package, "instance", file), mode)

@mc_challenge_mgr.route("/")
def index():
    user = get_session_user(mc_challenge_mgr)
    if user is not None:
        if 'current_map' not in session:
            session['current_map'] = avail_maps[0]
        map = session['current_map']
        ch = get_challenges(user, map)
        if ch is None:
            ch = load_challenges(mc_challenge_mgr, user, map)
        if 'prefs' not in session:
            session['prefs'] = make_session_prefs(load_preferences(mc_challenge_mgr, user))
    else:
        ch = None
    return render_template('index.jhtml', version=version, challenges=ch, available_maps=avail_maps)

@mc_challenge_mgr.route("/ajax.js")
def ajaxjs():
    return render_template('ajax.jjs')

@login_required
@mc_challenge_mgr.route("/changemap", methods=['GET'])
def changemap():
    if request.method == "GET":
        new_map = request.args['mapname']
        if new_map not in avail_maps:
            return "Map %s not available" % new_map
        session['current_map'] = new_map
        return redirect(url_for("index"))
    else:
        return "Only accepts GET"

@login_required
@mc_challenge_mgr.route("/store", methods=['POST'])
def store():
    if request.method == "POST":
        mapname = session['current_map']
        user = get_session_user(mc_challenge_mgr)
        challenges = get_challenges(user, mapname)
        try:
            data = map(int, request.data.split(',')[:-1])
            # truncate data length if longer than challenges length
            if len(data) > challenges.count:
                data = data[:challenges.count]
            fades = challenges.update(data)
            with mc_challenge_mgr.open_instance_resource(user.challenge_file[mapname], "w") as f:
                challenges.save(f)

            fades.insert(0, str(len([ c for c in challenges if c.completed ])))
            fades.insert(0, "Saving succeeded")
            return ",".join(fades)
        except Exception, e:
            print e
            return str(e)
    else:
        return "Only accepts POST"

@login_required
@mc_challenge_mgr.route("/updateprefs", methods=['POST'])
def updateprefs():
    if request.method == "POST":
        user = get_session_user(mc_challenge_mgr)
        prefs = get_session_prefs()
        prefs.hide_completed = request.data=="1"
        with mc_challenge_mgr.open_instance_resource(user.prefs_file, "w") as f:
            prefs.save(f)
        session.modified = True
        return update_session(mc_challenge_mgr, "Preferences updated successfully")
    else:
        return "only POST"

@mc_challenge_mgr.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST": # process login form
        import hashlib
        user = mc_challenge_mgr.users.get(request.form.get('username'), None)
        remember = request.form.get('remember', False)
        if remember is not False:
            remember = True
        password = request.form.get('password')
        if user is not None:
            user.auth_ok =hashlib.sha1(password).hexdigest() == user.password
        if user is None:
            flash("No such user")
        elif not login_user(user, False):
            flash("login failed")
        else:
            return login_successful(mc_challenge_mgr, make_session_user(user))
    return render_template('login.jhtml',version=version)

@mc_challenge_mgr.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST": # process registration form
        import hashlib
        if request.form.get('pw') != request.form.get('pw2'):
            flash("Password mismatch")
            mc_challenge_mgr.form = request.form
            return redirect(url_for("register"))
        user = User.register(mc_challenge_mgr.users, request.form.get('username'), hashlib.sha1(request.form.get('pw')).hexdigest())
        if user is None:
            flash("Username exists already")
            mc_challenge_mgr.form = request.form
            return redirect(url_for("register"))
        save_users(mc_challenge_mgr)
        if not login_user(user):
            flash("login failed")
            return redirect(url_for("register"))
        return login_successful(mc_challenge_mgr, make_session_user(user))
    else:
        print version
        return render_template('register.jhtml', version=version)

def logout_impl():
    session.pop('user', None)
    session.pop('logged_in', None)
    session.pop('prefs', None)
    return redirect(url_for("index"))

@login_required
@mc_challenge_mgr.route("/logout")
def logout():
    logout_user()
    return logout_impl()

@mc_challenge_mgr.template_filter("shortcid")
def shortcid(s):
    return s[:8]

@mc_challenge_mgr.template_filter("tolower")
def tolower(s):
    return str(s).lower()

def create_app():
    load_users(mc_challenge_mgr)
    return mc_challenge_mgr

if __name__ == "__main__":
    create_app().run(debug=True, host='0.0.0.0')
