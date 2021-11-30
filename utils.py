
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
        

    