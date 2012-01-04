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
import pickle

skyblock = Flask(__name__)

# make open_instance_resource Flask 0.7 compatible
open_instance_resource = None
if 'open_instance_resource' not in dir(skyblock):
    from os.path import join
    skyblock.open_instance_resource = lambda file, mode="rb": open(join("instance", file), mode)



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
        return self.__str__() + " [" + str(self.completed) + "]" + "(" + str(self.current_amount) + "/" + str(self.amount) + ")" if self.has_amount else ""

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
    return render_template('index.jhtml', challenges=challenges, version="2.1", completed=len([c for c in challenges if c.completed ]), total=len(challenges))

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

def create_app():
    init_challenges()
    load_challenges()
    return skyblock

if __name__ == "__main__":
    create_app().run(debug=True)
