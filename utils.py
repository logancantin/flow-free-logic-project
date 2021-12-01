from itertools import combinations
from functools import reduce
from pprint import pprint as pp

def exactly_k_contraint(k: int, *propns):
    '''Returns a list of constraints where each of the contraints has exaclty k
    of the propositions set to true.'''

    constraints = []

    # Iterate over all possible k combinations from propns
    for true_propns in combinations(propns, k):

        # Create a list of the negated propns (the ones that are not true)
        false_propns = [~x for x in propns if x not in true_propns]

        # Put the lists together
        all_propns = [*true_propns, *false_propns]

        # "and" all of the propositions together and append to the list of contraints
        constraints.append(reduce(lambda x, y: x & y, all_propns))
    
    # "Or" together all constraints
    return reduce(lambda x, y: x | y, constraints)

class Point:
    
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point({self.x}, {self.y})'

    def __hash__(self):
        return 32 * hash(self.x) + hash(self.y)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def in_bounds(self, max_x, max_y):
        '''Returns true if 0 <= self.x < max_x and 0 <= self.y < max_y.'''

        return 0 <= self.x < max_x and 0 <= self.y < max_y

class LineSegment:

    def __init__(self, p1, p2):
        if not (isinstance(p1, Point) and isinstance(p2, Point)):
            raise ValueError('p1 and p2 must be of type Point')
        
        self.p1 = p1
        self.p2 = p2
    
    def __repr__(self):
        return f'Line segment: endpoints {self.p1}, {self.p2}'

    def __hash__(self):
        return hash(self.p1) + hash(self.p2)
    
    def __eq__(self, other):
        return self.p1 == other.p1 and self.p2 == other.p2

    def manhattan_distance(self) -> int:
        return abs(self.p1.x - self.p2.x) + abs(self.p1.y - self.p2.y)
    
    def in_bounds(self, max_x, max_y):
        '''Returns true if both endpoints are inside the bounds 0 <= x < max_x and 0 <= y < max_y'''
        return self.p1.in_bounds(max_x, max_y) and self.p2.in_bounds(max_x, max_y)
        

    