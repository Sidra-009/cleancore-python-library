
from .linear_datatypes import Vector, Matrix
from .coordinate_geometry import (
    Point2D, Line2D, Circle, Triangle, 
    GeometryError, InvalidPointError, DegenerateLineError, InvalidShapeError
)
from .physics_visuals import Visualizer, TerminalPlotter, PhysicsEngine

__version__ = "0.2.1"