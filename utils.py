'''
Utilities / Classes

Point
  include x,y,z but some functions ignore Z

Vector

For now we'll stick with 2D
'''

import math
from constants import *

def distance( x1, y1, x2, y2 ):
  return math.sqrt( ( x1 - x2 ) ** 2 + ( y1 - y2 ) ** 2 )

# given p1, p2, return p3 which is the point dis along the line from p1 to p2
def pointAlong( x1, y1, x2, y2, dis ):
  dis /= distance( x1, y1, x2, y2 ) # turn distance in units to a fraction
  x3 = x1 + ( x2 - x1 ) * dis
  y3 = y1 + ( y2 - y1 ) * dis
  return x3, y3

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

  def move( self, v ):
    self.x += v.dx()
    self.y += v.dy()

class Vector():
  def __init__( self, d, m, maxLen=None ):
    self.direction = d # 0 is right, PI/2 is up, PI is left, -PI/2 is down
    self.magnitude = m
    self.maxLen = maxLen

  # Add vector v
  def add( self, v ):
    cx = self.dx() + v.dx() #v.magnitude * math.cos( v.direction )
    cy = self.dy() + v.dy() #v.magnitude * math.sin( v.direction )
    magnitude = math.sqrt( cx ** 2 + cy ** 2 )
    direction = vec_dir( cx, cy )
    if self.maxLen:
      if self.magnitude > self.maxLen:
        self.magnitude = self.maxLen
    self.magnitude = magnitude
    self.direction = direction

  def direction( self ):
    return self.direction

  def dx( self ):
    return self.magnitude * math.cos( self.direction )

  def dy( self ):
    return self.magnitude * math.sin( self.direction )

  def flipx( self ):
    self.direction = vec_dir( -self.dx(), self.dy() )

  def flipy( self ):
    self.direction = vec_dir( self.dx(), -self.dy() )

  def dot( self, angle ):
    theta = math.fabs( self.direction - angle )
    return self.magnitude * math.cos( theta )

def vecFromComps( dx, dy ):
  direction = vec_dir( dx, dy )
  magnitude = math.sqrt( dx ** 2 + dy ** 2 )
  return Vector( direction, magnitude )

# Compute angle of a vector (dx, dy)
def vec_dir( dx, dy ):
  magnitude = math.sqrt( dx ** 2 + dy ** 2 )

  if magnitude < EFFECTIVE_ZERO:
    direction = 0
  else:
    if math.fabs( dx ) < EFFECTIVE_ZERO:
      if dy > 0:
        direction = PI / 2
      else:
        direction = -PI / 2
    elif dx > 0:
      direction = math.atan( dy / dx )
    else:
      direction = PI + math.atan( dy / dx )

  return direction

# Given vectors f and t (from, to) return a vector that would connect f to t
def vectorDiff( f, t ):
  dx = t.dx() - f.dx()
  dy = t.dy() - f.dy()

  m = math.sqrt( dx ** 2 + dy ** 2 )
  d = vec_dir( dx, dy )
  return Vector( m, d )

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

  # ( 0, 0 ) is the pixel at ( SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 ). +y is up, so flip y
  xRaster = ( SCREEN_WIDTH  / 2 ) + ( SCREEN_WIDTH  / 2 ) * xNorm
  yRaster = ( SCREEN_HEIGHT / 2 ) - ( SCREEN_HEIGHT / 2 ) * yNorm

  return Point( xRaster, yRaster, 0 )

# See if these two objects have collided. Objects have a Point p indicating
# their world position and a colRect tuple indicating the ( x left, y top, x right, y bottom )
# collision rectangle in relative world coords to p. We assume constant Z and ignore.
# Collision detection is done using screen coordinates since that's the player sees.
# and may not correspond perfectly based on sprite shape.

WarningFlag = True

def collisionCheck( e, obj1, obj2 ):
  global WarningFlag

  if WarningFlag:
    print "fix collisionCheck"
    WarningFlag = False

  # collision boxes in world coords
  l1x = obj1.p.x + obj1.colRect[ 0 ]
  l1y = obj1.p.y + obj1.colRect[ 1 ]
  r1x = obj1.p.x + obj1.colRect[ 2 ]
  r1y = obj1.p.y + obj1.colRect[ 3 ]

  l2x = obj2.p.x + obj2.colRect[ 0 ]
  l2y = obj2.p.y + obj2.colRect[ 1 ]
  r2x = obj2.p.x + obj2.colRect[ 2 ]
  r2y = obj2.p.y + obj2.colRect[ 3 ]

  if 0:
    # calc collision boxes in screen coords
    p = projection( e.camera, Point( l1x, l1y, obj1.p.z ) )
    l1x = p.x
    l1y = p.y
    p = projection( e.camera, Point( r1x, r1y, obj1.p.z ) )
    r1x = p.x
    r1y = p.y

    p = projection( e.camera, Point( l2x, l2y, obj2.p.z ) )
    l2x = p.x
    l2y = p.y
    p = projection( e.camera, Point( r2x, r2y, obj2.p.z ) )
    r2x = p.x
    r2y = p.y

  if l1x >= r2x or l2x >= r1x or l1y <= r2y or l2y <= r1y:
    return False
  # Rectangles overlap.

  # Currently collisions that matter are
  # 1) enemy weapon AND the chopper or city building
  # 2) Chopprer weapon AND enemy vehicle or building
  #
  # We don't care if two enemy vehicles collide, two friendly weapons collide weapons collide..

  if obj1.oType == OBJECT_TYPE_NONE or obj2.oType == OBJECT_TYPE_NONE:
    return False # Smoke etc, don't want to interact.

  weapon = 0
  eWeapon = 0
  if obj1.oType == OBJECT_TYPE_WEAPON:
    weapon += 1
  if obj2.oType == OBJECT_TYPE_WEAPON:
    weapon += 1

  if obj1.oType == OBJECT_TYPE_E_WEAPON:
    eWeapon += 1
  if obj2.oType == OBJECT_TYPE_E_WEAPON:
    eWeapon += 1

  if weapon == 2 or eWeapon == 2 or ( weapon == 0 and eWeapon == 0 ):
    return False

  chopper = True if( obj1.oType == OBJECT_TYPE_CHOPPER or obj2.oType == OBJECT_TYPE_CHOPPER ) else False
  if chopper and weapon: # Stop shooting yourself
    return False

  if( ( obj1.oType >= OBJECT_TYPE_FIRST_ENEMY and obj1.oType <= OBJECT_TYPE_LAST_ENEMY ) or
      ( obj1.oType >= OBJECT_TYPE_FIRST_ENEMY and obj1.oType <= OBJECT_TYPE_LAST_ENEMY ) ):
     enemy = True
  else:
     enemy = False

  if enemy and eWeapon: # enemy doesn't shoot itself
    return False

  isBuilding = True if( obj1.oType == OBJECT_TYPE_BUILDING or obj2.oType == OBJECT_TYPE_BUILDING ) else False
  isEBuilding = True if( obj1.oType == OBJECT_TYPE_E_BUILDING or obj2.oType == OBJECT_TYPE_E_BUILDING ) else False

  if( ( weapon and isBuilding ) or( eWeapon and isEBuilding ) ):
    return False

  return True

def displayColRect( e, o ): # Display the projection of the collision rectangle for debug.
  l1x = o.p.x + o.colRect[ 0 ]
  l1y = o.p.y + o.colRect[ 1 ]
  r1x = o.p.x + o.colRect[ 2 ]
  r1y = o.p.y + o.colRect[ 3 ]

  p1 = projection( e.camera, Point( l1x, l1y, o.p.z ) )
  p2 = projection( e.camera, Point( r1x, r1y, o.p.z ) )
  e.canvas.create_rectangle( p1.x, p1.y, p2.x, p2.y, outline="orange" )

# Horizontal distance to the nearest object of type oType
# + means it's in the +x direction, neg means -x direction
def distanceToObjectType( e, xPos, oType ):

  d = None

  for o in e.objects:
    if o.oType == oType:
      dis = o.p.x - xPos
      if not d:
        d = dis
      elif math.fabs( dis ) < math.fabs( d ):
        d = dis

  return d

# object has showSICount, si and siMax
def showSI( c, p, o ):
  if o.showSICount > 0:
    o.showSICount -= 1
    c.create_rectangle( p.x - 30, p.y - 32, p.x + 30, p.y - 28, fill="red" )
    c.create_rectangle( p.x - 30, p.y - 32, p.x - 30 + 60.0 * o.si / o.siMax, p.y - 28, fill="green" )

class dbgPoint(): # Debug point
  def __init__( self, p ):
    self.p = Point( p.x, p.y, p.z )
    self.oType = OBJECT_TYPE_NONE
    self.colRect = ( -1, -1, 1, 1 )

  def processMessage( self, message, param=None ):
    pass

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    e.canvas.create_rectangle( proj.x - 1, proj.y - 1, proj.x, proj.y, outline="red" )