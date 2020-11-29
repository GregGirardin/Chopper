import constants
import math, random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image
from explosions import *
from missiles import *

##############################################################################
class Bomber():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_JET
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -6, 2, 6, 0 )
    self.time = 0
    self.v = v if v else Vector( PI, BOMBER_DELTA )
    self.health = SI_BOMBER

    if len( Bomber.images ) == 0:
      img = Image.open( "images/vehicles/Jet1.png" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 133 ) )
        crop = crop.resize( ( int( SW / 1.5 ), int( 133 / 1.5 ) ) )
        crop = ImageTk.PhotoImage( crop )
        Bomber.images.append( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.health -= param.wDamage
        if self.health < 0:
          e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.health < 0.0:
      return False
    self.time += 1

    if self.p.x < MIN_WORLD_X - 50:
      e.cityBombed( 1 )
      self.p.y = random.randint( 20, 25 )
      self.v.flipx()
    elif self.p.x > MAX_WORLD_X:
      self.p.y = random.randint( 10, 15 )
      self.v.flipx()

    self.p.move( self.v )

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT

    e.canvas.create_image( proj.x, proj.y - 20, image=Bomber.images[ d ] )
    e.canvas.create_rectangle( proj.x - 60, projShadow.y, proj.x + 60, projShadow.y, outline="black" )

##############################################################################
class Bomber2():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_JET
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -4, 2,4, 0 )
    self.time = 0
    self.v = v if v else Vector( PI, BOMBER_DELTA )
    self.health = SI_BOMBER2

    if len( Bomber2.images ) == 0:
      img = Image.open( "images/vehicles/Jet2.gif" )
      SW = 256
      for y in range( 0, 2 ):
        crop = img.crop( ( 0, y * SW, 640, y * SW + SW ) )
        crop = crop.resize( ( 640 / 3, 256 / 3 ) )
        crop = ImageTk.PhotoImage( crop )
        Bomber2.images.append( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.health -= param.wDamage
        if self.health < 0:
          e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.health < 0.0:
      return False
    self.time += 1

    if self.p.x < MIN_WORLD_X - 50:
      e.cityBombed( 1 )
      self.v.flipx()  # change direction
    elif self.p.x > MAX_WORLD_X:
      self.v.flipx()  # change direction

    self.p.move( self.v )

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT

    e.canvas.create_image( proj.x, proj.y - 40, image=Bomber2.images[ d ] )
    e.canvas.create_rectangle( proj.x - 60, projShadow.y, proj.x + 60, projShadow.y, outline="black" )

##############################################################################
class Fighter():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_JET
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -4, 2, 4, 0 )
    self.time = 0
    self.v = v if v else Vector( PI, FIGHTER_DELTA)
    self.nextMissile = 200
    self.health = SI_FIGHTER

    if len( Fighter.images ) == 0:
      img = Image.open( "images/vehicles/Jet3.gif" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 154 ) )
        crop = crop.resize( ( SW / 3, 154 / 3 ) )
        crop = ImageTk.PhotoImage( crop )
        Fighter.images.append( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.health -= param.wDamage
        if self.health < 0:
          e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.health < 0.0:
      return False
    self.time += 1

    if math.fabs( self.p.x - e.chopper.p.x ) > 100:
      self.v.flipx() # change direction

    if self.nextMissile > 0:
      self.nextMissile -= 1
    else:
      if( ( self.v.dx() > 0 and e.chopper.p.x > self.p.x ) or
          ( self.v.dx() < 0 and e.chopper.p.x < self.p.x ) ):
        d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT

        e.addObject( MissileSmall( self.p, self.v, d, oType=OBJECT_TYPE_E_WEAPON ) )
        self.nextMissile = 50

    self.p.move( self.v )

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT
    e.canvas.create_image( proj.x, proj.y - 25, image=Fighter.images[ d ] )
    e.canvas.create_rectangle( proj.x - 60, projShadow.y, proj.x + 60, projShadow.y, outline="black" )