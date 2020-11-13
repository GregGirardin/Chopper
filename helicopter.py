import constants
import math, random
from utils import *

class Helicopter():
  def __init__( self ):
    self.fuel = 100
    self.trust = 100
    self.angle = 0.0 # + is facing up
    self.p = Point( 0, 0, 100 )
    self.rotorTheta = 0.0
    # polys is a list of polygons for drawing the helo
    # (0,0) is the point where the rotor attaches to the body, we'll rotate around that.
    # a polygon is a tuple of a tuple of points, and a color
    # self.polys = []

  def update( self, e ):
    return True

  def draw( self, e ):
    pass