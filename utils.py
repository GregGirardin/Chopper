'''
Utilities / Classes

Point
  include x,y,z but some functions ignore Z

Vector

For now we'll stick with 2D
'''

import math
from constants import *

class Point():
  def __init__( self, x=0, y=0, z=0 ):
    self.x = x
    self.y = y
    self.z = z

  def distanceTo( self, p ):
     return math.sqrt( ( self.x - p.x ) ** 2 + ( self.y - p.y ) ** 2 + self.z - p.z )

  def directionTo( self, p ):
    cx = p.x - self.x
    cy = p.y - self.y

    magnitude = math.sqrt( cx ** 2 + cy ** 2 )

    if magnitude < EFFECTIVE_ZERO:
      direction = 0
    else:
      if math.fabs( cx ) < EFFECTIVE_ZERO:
        if cy > 0:
          direction = -PI / 2
        else:
          direction = PI / 2
      elif cx > 0:
        direction = math.atan( -cy / cx )
      else:
        direction = PI + math.atan( -cy / cx )

    return direction

  def move( self, v ): # v is a Vector PI/2 is up (-y)
    self.x += v.magnitude * math.cos( v.direction )
    self.y -= v.magnitude * math.sin( v.direction )
    return self

  def translate( self, p, theta ): # p is location, theta is orientation.
    xr =  self.x * math.cos( theta ) - self.y * math.sin( theta ) + p.x
    yr = -self.y * math.cos( theta ) - self.x * math.sin( theta ) + p.y
    return Point( xr, yr, self.z )

class Vector():
  def __init__( self, m, d ):
    self.magnitude = m
    self.direction = d # 0 is right, PI/2 is up, PI is left, -PI/2 is down

  # add vector v
  def add( self, v, mod=True, factor=1.0 ):
    cx = self.dx() + v.magnitude * math.cos( v.direction ) * factor
    cy = self.dy() - v.magnitude * math.sin( v.direction ) * factor
    magnitude = math.sqrt( cx ** 2 + cy ** 2 )
    direction = dir( cx, cy )
    if mod:
      self.magnitude = magnitude
      self.direction = direction
    return Vector( magnitude, direction )

  def dx( self ): # x component of vector
    return self.magnitude * math.cos( self.direction )

  def dy( self ): # y component of vector
    return -self.magnitude * math.sin( self.direction )

  def flipx( self ):
    self.direction = dir( -self.dx(), self.dy() )

  def flipy( self ):
    self.direction = dir( self.dx(), -self.dy() )

  def dot( self, angle ):
    theta = math.fabs( self.direction - angle )
    return self.magnitude * math.cos( theta )

# Compute angle of a vector (dx, dy)
def dir( dx, dy ):
  magnitude = math.sqrt( dx ** 2 + dy ** 2 )

  if magnitude < EFFECTIVE_ZERO:
    direction = 0
  else:
    if math.fabs( dx ) < EFFECTIVE_ZERO:
      if dy > 0:
        direction = -PI / 2
      else:
        direction = PI / 2
    elif dx > 0:
      direction = math.atan( -dy / dx )
    else:
      direction = PI + math.atan( -dy / dx )

  return direction

# Given vectors f and t (from, to) return a vector that would connect f to t
def vectorDiff( f, t ):
  dx = t.dx() - f.dx()
  dy = t.dy() - f.dy()

  m = math.sqrt( dx ** 2 + dy ** 2 )
  d = dir( dx, dy )
  return Vector( m, d )

# Base class for all objects in the world
class WorldObject():
  # Attributes every object has.
  def __init__( self, type, p, a=0.0, v=None, colRadius=0, mass=1.0, weapon=False ):
    if not v:
      v = Vector( 0, 0 )
    self.v = v
    self.spin = 0.0
    self.p = p # position
    self.a = a # angle
    self.type = type
    self.accel = 0.0
    self.weapon = weapon # Explode even on slow contact
    self.colRadius = colRadius
    self.colList = [] # a list of CollisionObject
    self.mass = mass

  def offScreen( self ):
    if self.p.x < -SCREEN_BUFFER or self.p.x > SCREEN_WIDTH + SCREEN_BUFFER or \
       self.p.y < -SCREEN_BUFFER or self.p.y > SCREEN_HEIGHT + SCREEN_BUFFER:
      return True
    else:
      return False

  def update( self, e ):
    self.a += self.spin
    if self.a < 0:
      self.a += TAU
    elif self.a > TAU:
      self.a -= TAU
    self.p.move( self.v )
    self.v.add( Vector( self.accel, self.a ) )

'''
Given a Camera at c and a point at p, compute the screen coordinates

See projection.jpg
'''

def projection( c, p ):
  assert c.z > 1, "Camera in front of projection plane"

  x1 = p.x - c.x # translate to camera coords (like camera is at 0,0)
  y1 = p.y - c.y
  zTot = p.z + c.z # Distance from camera to the plane p is on

  thetaX = math.atan( float( x1 )/ zTot )
  thetaY = math.atan( float( y1 )/ zTot )

  # If camera Z never changes make into constants..
  projEdgeX = c.z * math.tan( CAM_FOV_X / 2 ) # X value of edge of screen at proj plane
  projEdgeY = c.z * math.tan( CAM_FOV_Y / 2 ) # Y value of edge of screen

  pProjX = c.z * math.tan( thetaX ) # where p is on the projection plane
  pProjY = c.z * math.tan( thetaY )

  xNorm = pProjX / projEdgeX # Normalized coords. +1 to -1 mean screen edges
  yNorm = pProjY / projEdgeY

  # (0, 0) is the pixel at (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2). +y is up, so flip y
  xRaster = ( SCREEN_WIDTH / 2 ) + ( SCREEN_WIDTH / 2 ) * xNorm
  yRaster = ( SCREEN_HEIGHT / 2 ) - ( SCREEN_HEIGHT / 2 ) * yNorm

  return Point( xRaster, yRaster, 0 )