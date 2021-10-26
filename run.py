
# Native imports
import pprint

# Project imports
from utils import Point, LineSegment

# Third party imports
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

# Encoding that will store all of your constraints
E = Encoding()

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding

# TOP RIGHT IS ORIGIN, x increases to the right, y increases down
SIZE = 5
COLS = ['red', 'green', 'blue', 'yellow', 'pink']

@proposition(E)
class FilledPropn:

    def __init__(self, loc: Point, col):
        self.loc = loc
        self.col = col
    
    def __repr__(self):
        return f'FILLED: position {self.loc}, colour {self.col}'


# Dict: Point -> List[Filled]
fill_by_point = dict()
for x in range(SIZE):
    for y in range(SIZE):
        loc = Point(x, y)
        fill_by_point[loc] = [FilledPropn(loc, col) for col in COLS]


@proposition(E)
class EndpointPropn:

    def __init__(self, loc, col):
        self.loc = loc
        self.col = col

    def __repr__(self):
        return f'ENDPOINT: position {self.loc}, color {self.col}'

# Dict: Point -> List[EndpointPropn]
endpoints_by_location = dict()

# Dict: Col -> List[EndpointPropn]
endpoints_by_col = {col: list() for col in COLS}

for x in range(SIZE):
    for y in range(SIZE):
        loc = Point(x, y)
        propns = list()
        for col in COLS:
            propn = EndpointPropn(loc, col)
            endpoints_by_col[col].append(propn)
            propns.append(propn)
        endpoints_by_location[loc] = propns


@proposition(E)
class LineSegmentPropn:

    def __init__(self, line_segment: LineSegment, col):
        
        if line_segment.manhattan_distance() != 1:
            raise ValueError(f'Line segment is not valid! The endpoints must be adjacent (manhattan distance of 1)')
        if not line_segment.in_bounds(SIZE, SIZE):
            raise ValueError(f'Line segment {line_segment} is not in bounds.')
        
        self.line_segment = line_segment
        self.col = col

    def __repr__(self):
        return f'LINE SEGMENT: line segment {self.line_segment}, col {self.col}'

# Dict: LineSegment -> List[LineSegmentPropn]
line_segment_propns_by_line_segment = dict()

# Dict: Point -> List[LineSegmentPropn]
line_segment_propns_by_point = dict()

def update_line_segment_propns_by_point(loc, propns):
    if loc not in line_segment_propns_by_point.keys():
        line_segment_propns_by_point[loc] = propns.copy()
    else:
        line_segment_propns_by_point[loc].append(propns)

for x in range(SIZE):
    for y in range(SIZE):
        loc1 = Point(x, y)

        for loc2 in [Point(x + 1, y), Point(x, y + 1)]:
            ls = LineSegment(loc1, loc2)
            if not ls.in_bounds(SIZE, SIZE):
                continue
            propns = [LineSegmentPropn(ls, col) for col in COLS]
            line_segment_propns_by_line_segment[ls] = propns
            update_line_segment_propns_by_point(loc1, propns)
            update_line_segment_propns_by_point(loc2, propns)


# CONSTRAINT

# Every tile must have exactly one color
for pt in fill_by_point.keys():
    constraint.add_exactly_one(E, *(fill_by_point[pt]))
    


# Build an example full theory for your setting and return it.
#
#  There should be at least 10 variables, and a sufficiently large formula to describe it (>50 operators).
#  This restriction is fairly minimal, and if there is any concern, reach out to the teaching staff to clarify
#  what the expectations are.
def example_theory():
    # Add custom constraints by creating formulas with the variables you created. 
    E.add_constraint((a | b) & ~x)
    # Implication
    E.add_constraint(y >> z)
    # Negate a formula
    E.add_constraint((x & y).negate())
    # You can also add more customized "fancy" constraints. Use case: you don't want to enforce "exactly one"
    # for every instance of BasicPropositions, but you want to enforce it for a, b, and c.:
    constraint.add_exactly_one(E, a, b, c)

    return E


if __name__ == "__main__":

    '''
    T = example_theory()
    # Don't compile until you're finished adding all your constraints!
    T = T.compile()
    # After compilation (and only after), you can check some of the properties
    # of your model:
    print("\nSatisfiable: %s" % T.satisfiable())
    print("# Solutions: %d" % count_solutions(T))
    print("   Solution: %s" % T.solve())

    print("\nVariable likelihoods:")
    for v,vn in zip([a,b,c,x,y,z], 'abcxyz'):
        # Ensure that you only send these functions NNF formulas
        # Literals are compiled to NNF here
        print(" %s: %.2f" % (vn, likelihood(T, v)))
    print()
    '''

    T = E.compile()
    print("\nSatisfiable: %s" % T.satisfiable())
    #print("# Solutions: %d" % count_solutions(T))
    #print("   Solution: %s" % T.solve())
    pprint.pprint(T.solve())

