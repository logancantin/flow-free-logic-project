
# Native imports
import pprint
from functools import reduce
from sys import argv

# Project imports
from utils import Point, LineSegment, exactly_k_contraint, draw_board

# Third party imports
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

COLMAP = {
    'R':'red',
    'G':'green',
    'B':'blue',
    'Y':'yellow',
    'P':'pink'
}

E = Encoding()

@proposition(E)
class FilledPropn:
    '''Proposition that represents whether or not a cell is filled. '''

    def __init__(self, loc: Point, col):
        '''Creates a filled proposition for the cell at `loc` of color `col`. '''
        
        self.loc = loc
        self.col = col
    
    def __repr__(self):
        return f'FILLED: position {self.loc}, colour {self.col}'

@proposition(E)
class EndpointPropn:
    '''Proposition that represents an endpoint of a flow. '''

    def __init__(self, loc, col):
        '''Creates an endpoint proposition at location `loc` and of color `col`. '''
        self.loc = loc
        self.col = col

    def __repr__(self):
        return f'ENDPOINT: position {self.loc}, color {self.col}'


@proposition(E)
class LineSegmentPropn:
    '''Proposition that represents a line segment. '''

    def __init__(self, line_segment: LineSegment, col):
        '''Creates a line segment proposition between the cells specified by 
        `line_segment` of color `col`. '''
        
        if line_segment.manhattan_distance() != 1:
            raise ValueError(f'Line segment must have manhattan distance of 1.')
        
        self.line_segment = line_segment
        self.col = col
        
    def __repr__(self):
        return f'LINE SEGMENT: line segment {self.line_segment}, col {self.col}'

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

def _endpoint_propns_init(size: int, colors: list[str]):
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
  

def load_board(board_file='boards/level1.txt'):
    """Loads a board from a board file.

    Arguments
    ---------
    board_file : Optional[str]
        path to the board file. If not supplied, loads the default board,
        boards/level1.txt.

    Returns
    -------
    tuple[Encoding, tuple[int, int], list[str]]
        tuple containing the encoding, the size of the board (width, height),
        and the list of colors
    """

    # Read the board from the file
    try:
        with open(board_file, 'r') as f:
            lines = f.readlines()
    except IOError as err:
        print(f"Could not read supplied board file {board_file}")
        exit(1)
    
    board = []
    width = None
    for i, line in enumerate(lines):
        line = line.strip()
        if line == '':
            break
        if width is None:
            width = len(line)
        elif len(line) != width:
            print(f"Supplied board file {board_file} has inconsistent line widths.")
            exit(1)
        board.append(line)
    height = len(board)
    size = 5

    if width != 5 or height != 5:
        print('Only the board size 5x5 is supported. Please supply a 5x5 board.')
        exit(1)
    
    # Get all colors that are used in this board
    colors = set()
    for line in board[:5]:
        for c in line[:5]:
            if c == '.':
                continue
            elif c in COLMAP.keys() and COLMAP[c] not in colors:
                colors.add(COLMAP[c])
    colors = list(colors)

    # Generate the propositions
    fill_by_point = _fill_propns_init(size=size, colors=colors)
    endpoints_by_location, \
        endpoints_by_col = _endpoint_propns_init(size=size, colors=colors)
    line_segment_propns_by_line_segment, \
        line_segment_propns_by_point = _line_segment_propns_init(size=size, colors=colors)

    # Add constraints given from the boardfile
    for y, line in enumerate(board[:5]):
        for x, c in enumerate(line[:5]):
            if c in COLMAP.keys():

                # Find endpoint constraint of this color at this point
                p = Point(x, y)
                all_endpoints = endpoints_by_location[p]
                correct_endpoint = None
                for ep in all_endpoints:
                    if ep.col == COLMAP[c]:
                        correct_endpoint = ep
                        break
                E.add_constraint(correct_endpoint)

    # Generate the constraints:
    # Every tile must have exactly one color
    for pt in fill_by_point.keys():
        constraint.add_exactly_one(E, *(fill_by_point[pt]))

    #An endpoint at (x,y) must have the same colour as the cell where it is located.​
    # If there is an endpoint at (x,y), (x,y) is filled with that endpoint's colour
    for pt in endpoints_by_location.keys():
        for ep_prop, fill_prop in zip(endpoints_by_location[pt], fill_by_point[pt]):
            E.add_constraint(ep_prop >> fill_prop)

    #Exactly 2 endpoints per colour
    for col in colors:
        E.add_constraint(exactly_k_contraint(2, *endpoints_by_col[col]))

    
    #There must be exactly one line segment coming out of an endpoint
    endpoint_at_location = {
        Point(x, y): reduce(lambda x, y: x | y, endpoints_by_location[Point(x, y)])
        for x in range(size)
        for y in range(size)
    }
    for pt in line_segment_propns_by_point.keys():
        E.add_constraint(endpoint_at_location[pt] >> exactly_k_contraint(1, *line_segment_propns_by_point[pt]))

    # There must be exactly two line segments coming out of a non-endpoint cell
    for pt in line_segment_propns_by_point.keys():
        E.add_constraint(~endpoint_at_location[pt] >> exactly_k_contraint(2, *line_segment_propns_by_point[pt]))

    # A line segment on a location implies that the cells underneath it are filled with the same colour
    for x in range(size):
        for y in range(size):
            loc1 = Point(x, y)

            for loc2 in [Point(x + 1, y), Point(x, y + 1)]:
                if not loc2.in_bounds(size, size):
                    continue
                ls = LineSegment(loc1, loc2)
                
                for ls_propn, fill1_propn, fill2_propn in zip(
                        line_segment_propns_by_line_segment[ls], fill_by_point[loc1], fill_by_point[loc2]):
                    E.add_constraint(ls_propn >> (fill1_propn & fill2_propn))

    return E, size, colors

if __name__ == "__main__":

    E, size, colors = load_board() if len(argv) < 2 else load_board(argv[1])

    # Compile and solve the theory
    T = E.compile()
    solved = T.solve()

    # Size is 5 since we have restricted boards to 5x5
    size = 5

    if solved is not None:
        draw_board(size, solved)
    else:
        print("No solution")

