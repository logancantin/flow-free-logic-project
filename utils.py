from itertools import combinations
from functools import reduce
from pprint import pprint as pp
import turtle

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

def draw_board(size, solved):

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

    # Optimizations
    turtle.delay(0)
    tr.ht()
    

    def t(x, y):
        return (X_START + cell_w/2) + cell_w * x, (Y_START - cell_w/2) - cell_w * y 

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
    for prop in solved.keys():
        if not solved[prop]:
            continue
        
        elif "EndpointPropn" in (str(type(prop))): #repr(ep) contains "endpoint"
            tr.color(prop.col)
            tr.goto(*t(prop.loc.x, prop.loc.y))
            tr.pensize(cell_w/3)
            tr.dot()

        elif "LineSegmentPropn" in (str(type(prop))): #repr(ep) contains "endpoint"
            tr.color(prop.col)
            tr.pensize(cell_w / 3)

            ls = prop.line_segment
            
            tr.goto(*t(ls.p1.x, ls.p1.y))
            tr.pendown()
            tr.goto(*t(ls.p2.x, ls.p2.y))
            tr.penup()
            
    turtle.done()