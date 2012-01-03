#!/usr/bin/python
from flask import Flask, render_template, request, redirect, url_for
import pickle

from os.path import abspath, dirname
from os.path import join as pathjoin
WD=abspath(dirname(__file__))

class Challenge(object):
    def __init__(self, id, desc, checked):
        self.id = id
        self.desc = desc
        self.checked = checked
        pass

    def __str__(self):
        return str(self.id+1) + ") " + self.desc

    def __repr__(self):
        return self.__str__() + " [" + str(self.checked) + "]"


skyblock = Flask(__name__)

challenges = [None] * 50

# read challenge descriptions
def init_challenges():
    with open(pathjoin(WD, "challenges.txt")) as cfile:
        chtxts = map(str.strip, cfile.readlines())
    for i in xrange(50):
        challenges[i] = Challenge(i, chtxts[i], False)

def save_challenges():
    checked = [ c.id for c in challenges if c.checked ]
    with open(pathjoin(WD, "store.txt"), "w") as f:
        pickle.dump(checked, f)

def load_challenges():
    try:
        with open(pathjoin(WD, "store.txt")) as f:
            checked = pickle.load(f)
    except:
        checked = []
    for i in checked:
        challenges[i].checked = True

@skyblock.route("/favicon.ico")
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

@skyblock.route("/")
def index():
    return render_template('index.jhtml', challenges=challenges, version="2.1")

@skyblock.route("/store", methods=['POST'])
def store():
    if request.method == "POST":
        try:
            checked_boxes = map(int, request.data.split(',')[:-1])
            checked_challenges = [ c.id for c in challenges if c.checked ]
            to_check = [ i for i in checked_boxes if i in checked_challenges ]
            to_uncheck = [ i for i in checked_challenges if i not in checked_boxes ]
            for i in to_check:
                challenges[i].checked = True
            for i in to_uncheck:
                challenges[i].checked = False

            save_challenges()

            return "Saving succeeded"
        except Exception, e:
            print e
            return str(e)
    else:
        return "Only accepts POST"

if __name__ == "__main__":
    init_challenges()
    load_challenges()
    skyblock.run(debug=True)
