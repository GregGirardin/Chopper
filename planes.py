import constants
import math, random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image
from explosions import *

##############################################################################
class Bomber():
  images = []

  def __init__( self, p, d=DIRECTION_LEFT ):
    self.oType = OBJECT_TYPE_JET
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -6, 2, 6, 0 )
    self.time = 0
    self.d = d
    self.vy = 0
    self.structuralIntegrity = SI_BOMBER

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
        self.structuralIntegrity -= param.wDamage
        if self.structuralIntegrity < 0:
          e.addObject( BombExplosion( self.p ) )

  def update( self, e ):
    self.time += 1
    if self.structuralIntegrity < 0.0:
      return False

    self.p.x += BOMBER_DELTA if self.d == DIRECTION_RIGHT else -BOMBER_DELTA

    if self.p.x < MIN_WORLD_X - 50:
      e.addStatusMessage( "City has been bombed.", 25 )
      self.p.y = random.randint( 20, 25 )
      self.d = DIRECTION_RIGHT # fly back to base..
    elif self.p.x > MAX_WORLD_X:
      self.d = DIRECTION_LEFT
      self.p.y = random.randint( 10, 15 )

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    e.canvas.create_image( proj.x, proj.y - 20, image=Bomber.images[ self.d ] )
    e.canvas.create_rectangle( proj.x - 60, projShadow.y,
                               proj.x + 60, projShadow.y, outline="black" )

##############################################################################
class Bomber2():
  images = []

  def __init__( self, p, d=DIRECTION_LEFT ):
    self.oType = OBJECT_TYPE_JET
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -4, 2,4, 0 )
    self.time = 0
    self.d = d
    self.vy = 0
    self.structuralIntegrity = SI_BOMBER2

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
        self.structuralIntegrity -= param.wDamage
        if self.structuralIntegrity < 0:
          e.addObject( BombExplosion( self.p ) )

  def update( self, e ):
    self.time += 1
    if self.structuralIntegrity < 0.0:
      return False

    self.p.x += BOMBER_DELTA if self.d == DIRECTION_RIGHT else -BOMBER_DELTA

    if self.p.x < MIN_WORLD_X - 50:
      e.addStatusMessage( "City has been bombed.", 25 )
      self.d = DIRECTION_RIGHT # fly back to base..
    elif self.p.x > MAX_WORLD_X:
      self.d = DIRECTION_LEFT

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    e.canvas.create_image( proj.x, proj.y - 40, image=Bomber2.images[ self.d ] )
    e.canvas.create_rectangle( proj.x - 60, projShadow.y, proj.x + 60, projShadow.y, outline="black" )

##############################################################################
class Fighter():
  images = []

  def __init__( self, p, d=DIRECTION_LEFT ):
    self.oType = OBJECT_TYPE_JET
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -4, 2, 4, 0 )
    self.time = 0
    self.d = d
    self.vy = 0
    self.structuralIntegrity = SI_FIGHTER

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
        self.structuralIntegrity -= param.wDamage
        if self.structuralIntegrity < 0:
          e.addObject( BombExplosion( self.p ) )

  def update( self, e ):
    self.time += 1
    if self.structuralIntegrity < 0.0:
      return False

    self.p.x += FIGHTER_DELTA if self.d == DIRECTION_RIGHT else -FIGHTER_DELTA
    if self.p.x < e.chopper.p.x - 250:
      self.d = DIRECTION_RIGHT
    elif self.p.x > e.chopper.p.x + 250:
      self.d = DIRECTION_LEFT
    else:
      pass # tbd, fighter AI here.

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    e.canvas.create_image( proj.x, proj.y - 25, image=Fighter.images[ self.d ] )
    e.canvas.create_rectangle( proj.x - 60, projShadow.y, proj.x + 60, projShadow.y, outline="black" )