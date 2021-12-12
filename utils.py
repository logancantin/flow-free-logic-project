from itertools import combinations
from functools import reduce
from pprint import pprint as pp
from propositions import LineSegmentPropn, EndpointPropn, FilledPropn

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
        return hash((self.x, self.y))
    
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
        

def _fill_propns_init(size: int, colors: list[str]):
    """Initializes the FilledPropositions for the given board.

    Arguments
    ---------
    size : int
        width / height of the board
    colors : list[str]
        valid colors for this board

    Returns
    -------
    dict[Point, List[FilledPropn]]
        Returns a dictionary mapping a point (location on the board) to all the
        filled propositions at that location.
    """

    fill_by_point = dict()
    for x in range(size):
        for y in range(size):
            loc = Point(x, y)
            fill_by_point[loc] = [FilledPropn(loc, col) for col in colors]
    return fill_by_point

def _endpoint_propns_init(size: int, colors: List[str]):
    """Initializes the EndpointPropositions for the given board.

    Arguments
    ---------
    size : int
        width / height of the board
    colors : list[str]
        valid colors for this board

    Returns
    -------
    tuple[dict[Point, list[EndpointPropn]], dict[str, list[EndpointPropn]]]
        Returns a tuple. First object is a dictionary mapping a point on the
        board to a list of endpoint propositions at that location. Second 
        object is dictionary mapping a color to all the endpoints of that
        color.
    """

    endpoints_by_location = dict() #list of all colour endpoint props
    endpoints_by_col = {col: list() for col in colors} #list of all enpoints of a single colour

    for x in range(size):
        for y in range(size):
            loc = Point(x, y)
            propns = list()
            for col in colors:
                propn = EndpointPropn(loc, col)
                endpoints_by_col[col].append(propn)
                propns.append(propn)
            endpoints_by_location[loc] = propns

    return endpoints_by_location, endpoints_by_col

def _line_segment_propns_init(size: int, colors: list[str]):
    """Initializes the LineSegmentPropositions for the given board.

    Arguments
    ---------
    size : int
        width / height of the board
    colors : list[str]
        valid colors for this board

    Returns
    -------
    tuple[dict[LineSegment, list[LineSegmentPropn]], dict[str, list[LineSegmentPropn]]]
        Returns a tuple. First object is a dictionary mapping a line segment
        on the board to a list of line segments at the same location. Second 
        object is dictionary mapping a point to all the endpoints that touch
        that point.
    """

    line_segment_propns_by_line_segment = dict()
    line_segment_propns_by_point = {Point(0, 0):[]}

    for x in range(size):
        for y in range(size):
            loc1 = Point(x, y)

            for loc2 in [Point(x + 1, y), Point(x, y + 1)]:
                ls = LineSegment(loc1, loc2)
                if not ls.in_bounds(size, size):
                    continue
                propns = [LineSegmentPropn(ls, col) for col in colors]
                line_segment_propns_by_line_segment[ls] = propns
                line_segment_propns_by_point[loc1].extend(propns)
                if loc2 in line_segment_propns_by_point.keys():
                    line_segment_propns_by_point[loc2].extend(propns)
                else:
                    line_segment_propns_by_point[loc2] = list(propns)
    return line_segment_propns_by_line_segment, line_segment_propns_by_point
  