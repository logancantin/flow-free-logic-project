
# Native imports
import pprint
from functools import reduce

# Project imports
from utils import Point, LineSegment, exactly_k_contraint, \
    _endpoint_propns_init, _fill_propns_init, _line_segment_propns_init
from propositions import FilledPropn, EndpointPropn, LineSegmentPropn

# Third party imports
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

COLMAP = {'R':'red', 'G':'green', 'B':'blue', 'Y':'yellow', 'P':'pink'}

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

    # Encoding that will store all of the constraints
    E = Encoding()

    # Generate the constraints:
    # Every tile must have exactly one color
    for pt in fill_by_point.keys():
        constraint.add_exactly_one(E, *(fill_by_point[pt]))

    #An endpoint at (x,y) must have the same colour as the cell where it is located.​
    # If there is an endpoint at (x,y), (x,y) is filled with that endpoint's colour
    for pt in endpoints_by_location.keys():
        for ep_prop, fill_prop in zip(endpoints_by_location[pt], fill_by_point[pt]):
            E.add_constraint(ep_prop >>fill_prop)

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

    return E

if __name__ == "__main__":

    from sys import argv

    E, size, colors = load_board() if len(argv) < 2 else load_board(argv[1])
    T = E.compile()
    
    solved = T.solve()
    print(solved)

