class Node:
    count = 0
    nodelist = {}

    def __init__(self, v: int, l=None, r=None):
        self.v = v
        self.c1 = l
        self.c2 = r
        self._id = None
        self.nullable = None
        self.firstpos = set()
        self.lastpos = set()
        self.followpos = set()
        if v < 1e5 + 2:  # not operator
            Node.count += 1
            self._id = Node.count
            Node.nodelist[self._id] = self
