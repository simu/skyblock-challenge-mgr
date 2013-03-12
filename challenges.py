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

import pickle

challenges = dict()

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
        return self.__str__() + " [" + str(self.completed) + "]" + \
                ("(" +str(self.current_amount) + "/" + str(self.amount) + ")"
                    if self.has_amount else "")

    @property
    def completed(self):
        return self.current_amount >= self.amount

    @property
    def has_amount(self):
        return self.amount > 1

class ChallengeSet(object):
    def __init__(self, challenges, mapname):
        self.challenges = challenges
        self._mapname = mapname

    @property
    def completed(self):
        return len([ c for c in self.challenges if c.completed ])

    @property
    def count(self):
        return len(self.challenges)

    @property
    def mapname(self):
        return self._mapname

    def update(self, data):
        fades = []
        if len(data) != self.count:
            return "size mismatch"
        for c,v in zip(self.challenges, data):
            old_completed = c.completed
            c.current_amount = v
            if old_completed != c.completed:
                fades.append("{0.id:d}={opacity:.1f}".format(c, opacity=0.4 if c.completed else 1))
        return fades

    def save(self, file):
        data = [ c.current_amount for c in self.challenges ]
        pickle.dump(data, file)

    def __iter__(self):
        return iter(self.challenges)

# read challenge descriptions
def init_challenges(app, mapname):
    challenges = []
    with app.open_resource("challenges-%s.txt" % mapname) as cfile:
        chtxts = map(str.strip, cfile.readlines())
    for i in xrange(len(chtxts)):
        text,amount = chtxts[i].split('|')
        challenges.append(Challenge(i, text, int(amount)))
    return challenges

def save_challenges(app, user, mapname):
    ch = challenges.get((user, mapname), None)
    if ch is None:
        return False
    with app.open_instance_resource(user.challenge_file[mapname], "w") as f:
        ch.save(f)
    return True

def load_challenges(app, user, mapname):
    ch = init_challenges(app, mapname)
    try:
        with app.open_instance_resource(user.challenge_file[mapname]) as f:
            data = pickle.load(f)
    except:
        data = [0] * len(ch)
    for c,v in zip(ch, data):
        c.current_amount = v

    ch = ChallengeSet(ch, mapname)
    challenges[(user,mapname)] = ch
    return ch

def get_challenges(user, mapname):
    ch = challenges.get((user,mapname), None)
    return ch

