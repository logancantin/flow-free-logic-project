from utils import Point, LineSegment
from bauhaus import proposition

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