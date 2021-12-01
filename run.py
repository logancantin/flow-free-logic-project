
# Native imports
import pprint

# Project imports
from utils import Point, LineSegment


# Third party imports
from bauhaus import Encoding, proposition, constraint
from bauhaus.utils import count_solutions, likelihood

#Visualization import
import turtle

# Encoding that will store all of your constraints
E = Encoding()

# To create propositions, create classes for them first, annotated with "@proposition" and the Encoding

# TOP RIGHT IS ORIGIN, x increases to the right, y increases down
SIZE = 5
COLS = ['red', 'green', 'blue', 'yellow', 'orange']

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
endpoints_by_location = dict() #list of all colour endpoint props

# Dict: Col -> List[EndpointPropn]
endpoints_by_col = {col: list() for col in COLS} #list of all enpoints of a single colour

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
            raise ValueError(f'Line segment is not valid! The endpoint')
        
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

#comment

#An endpoint at (x,y) must have the same colour as the cell where it is located.​
# If there is an endpoint at (x,y), (x,y) is filled with that endpoint's colour
for pt in endpoints_by_location.keys():
    for ep_prop, fill_prop in zip(endpoints_by_location[pt], fill_by_point[pt]):
        E.add_constraint(ep_prop >>fill_prop)

#Exactly 1 ep per colour
for col in COLS:
    constraint.add_exactly_one(E, *endpoints_by_col[col])

#There can’t be two line segments of different colors connecting the same two cells.​
for ls in line_segment_propns_by_line_segment.keys():
    constraint.add_at_most_one(E, *line_segment_propns_by_line_segment[ls] )



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

 #VISUALIZATION 
  # make a grid 
w, h = SIZE, SIZE
grid = [ ['x' for x in range(w)] for y in range(h)]

for x in grid:
    for y in grid:
        for col in COLS:
          #  if colour is at point (x,y), then grid[x][y] = colour
          # How to get colour of a point?
            pass
    pass

def draw_board(size, arr):

    #SCREEN SET UP
    
    grid_w = 600
    cell_w = grid_w /size #width of each cell

    turtle.screensize(canvwidth=(grid_w), canvheight=(grid_w), bg="black")
    turtle.title("Flow Logic Project")
    turtle.speed(0)
    
    tr = turtle.Turtle()
    tr.ht()
    X_START = -300
    Y_START = 300
    tr.speed(0)
    tr.color("white")
    tr.penup()
    tr.goto(X_START, Y_START) #top left corner. 
    tr.pendown()

    #Draws the edges of the board
    for i in range (4):
        tr.forward(cell_w * size)
        tr.right(90)
    #Draws the horizontal grid lines
    for i in range (size):
        tr.goto(tr.xcor(), tr.ycor()-cell_w)
        tr.forward(cell_w*size)
        tr.goto(tr.xcor() - cell_w*size, tr.ycor()) 

    #resets the turtle
    tr.goto(tr.xcor(), tr.ycor()+cell_w*size)
    tr.right(90)

    #Draws the vertical grid lines
    for i in range (size):
       tr.goto(tr.xcor()+cell_w, tr.ycor())
       tr.forward(cell_w*size)
       tr.goto(tr.xcor(), tr.ycor() + cell_w*size) 

    #Reset Turtle position to start drawing propositions
    tr.penup()
    tr.goto( (X_START + cell_w/2), (Y_START - cell_w/2))
    tr.speed(0)

    #Fill the board with the endpoints 
    for x in range(size):
        for y in range(size):
            prop = arr[x][y]
            if "EndpointPropn" in (str(type(prop))): #repr(ep) contains "endpoint"
                tr.color(prop.col)
                tr.pensize(cell_w/3)
                tr.dot()
            tr.forward(cell_w)
        tr.goto((tr.xcor() + cell_w), Y_START - cell_w/2)

    #Reset Turtle position to start drawing line segments
    tr.penup()
    tr.goto( (X_START + cell_w/2), (Y_START - cell_w/2))
    
    for x in range(size):
        for y in range(size):
            prop = arr[x][y]
            if "LineSegmentPropn" in (str(type(prop))): #repr(ep) contains "endpoint"
                tr.color(prop.col)
                tr.pensize(cell_w / 3)
                
                xpos = (X_START + cell_w/2) + cell_w * prop.line_segment.p1.x 
                ypos = (Y_START - cell_w/2) - cell_w * prop.line_segment.p1.y
                tr.goto(xpos, ypos)
                tr.pendown()
                xpos = (X_START + cell_w/2) + cell_w * prop.line_segment.p2.x 
                ypos = (Y_START - cell_w/2) - cell_w * prop.line_segment.p2.y
                tr.goto(xpos, ypos)
                tr.penup()
            
        tr.goto((tr.xcor() + cell_w), Y_START - cell_w/2)
           

    
    

    turtle.done()

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
    
    solved = T.solve()
    print(type(solved))
    pprint.pprint(solved)
    for f in solved.keys():
        if  "LineSegmentPropn" in (str(type(f))): #repr(f) contains "FilledPropn"
            if (solved[f]):
                col = f.col
                x = f.line_segment.p2.x
                y = f.line_segment.p2.y
                grid[x][y] = f

        elif  "EndpointPropn" in (str(type(f))): #repr(ep) contains "endpoint"
            if (solved[f]):
                col = f.col
                x = f.loc.x
                y = f.loc.y
                grid[x][y] = f
                
    print(grid[1][1])
    pprint.pprint(grid)

    draw_board(len(grid), grid)

