#
# adapted from http://stackoverflow.com/a/7150594
#

class ComparableMixin(object):

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
