import pickle

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


# read challenge descriptions
def init_challenges(app):
    challenges = []
    with app.open_resource("challenges.txt") as cfile:
        chtxts = map(str.strip, cfile.readlines())
    for i in xrange(len(chtxts)):
        text,amount = chtxts[i].split('|')
        challenges.append(Challenge(i, text, int(amount)))
    return challenges

def save_challenges(app, user, challenges):
    data = [ c.current_amount for c in challenges ]
    with app.open_instance_resource(user.challenge_file, "w") as f:
        pickle.dump(data, f)

def load_challenges(app, user):
    challenges = init_challenges(app)
    try:
        with app.open_instance_resource(user.challenge_file) as f:
            data = pickle.load(f)
    except:
        data = [0] * len(challenges)
    for c,v in zip(challenges, data):
        c.current_amount = v

    return challenges

