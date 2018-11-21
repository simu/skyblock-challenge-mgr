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


class ComparableMixin(object):
    #
    # adapted from http://stackoverflow.com/a/7150594
    #

    def __eq__(self, other):
        if type(self) == type(None):
            if type(other) == type(None):
                return True
            else:
                return False
        elif type(other) == type(None):
            return False
        else:
            return not self<other and not other<self

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return other<self

    def __ge__(self, other):
        return not self<other

    def __le__(self, other):
        return not other<self

def update_session(app, msg):
    from flask import make_response, session
    r = make_response(msg)
    app.save_session(session, r)
    return r

def login_successful(app, user, target="index"):
    from flask import session, flash, redirect, url_for
    from preferences import load_preferences
    session['user'] = user
    session['logged_in'] = True
    session['prefs'] = load_preferences(app, user)
    flash("Login successful")
    return redirect(url_for(target))

def changelog():
    import subprocess
    from os.path import abspath, dirname
    gitdir = abspath(dirname(__file__))
    log=subprocess.Popen([ "git", "log", "--pretty=oneline", "-n", "5" ], cwd=gitdir, stdout=subprocess.PIPE).communicate()[0].split('\n')
    return [ (x[0],x[1]) for x in [ e.split(' ', 1) for e in log[:-1] ] ]
