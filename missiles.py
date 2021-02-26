import constants
import math, random
from utils import *
from explosions import *
from tkinter import *
from PIL import ImageTk, Image
from copy import copy

class Bullet():
  def __init__( self, p, v, oType=OBJECT_TYPE_WEAPON, wDamage=WEAPON_DAMAGE_BULLET ):
    self.oType = oType # OBJECT_TYPE_WEAPON or OBJECT_TYPE_E_WEAPON if sourced from an enemy.
    self.wDamage = wDamage
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -.5, -.5, .5, .5 )
    self.time = 0
    self.v = copy( v )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      e.addObject( SmokeA( Point( self.p.x, self.p.y, self.p.z ) ) )
      self.time = BULLET_LIFETIME + 1

  def update( self, e ):
    self.time += 1
    if self.time > BULLET_LIFETIME:
      return False

    self.p.move( self.v )
    if self.p.y < 0.0:
      e.addObject( SmokeA( Point( self.p.x, self.p.y, self.p.z ) ) )
      return False

    return True

  def draw( self, e, p ):
    e.canvas.create_line( p.x, p.y, p.x + self.v.dx() * 4, p.y - self.v.dy() * 4, fill="black", width=2 )

# Base class for missiles
class MissileBase():
  def __init__( self, p, v, d, oType=OBJECT_TYPE_WEAPON ):
    self.oType = oType
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -1, .5, 1, -.5 )
    self.v = copy( v ) # Initial velocity Vector
    self.d = d # desired direction. Initial velocity may not be in that direction.
    self.fuel = 100
    self.time = 0
    self.thrust = False

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      self.time = -1 # trick to make it disappear rather than use another flag
      e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.time < 0:
      return False
    self.time += 1

    if self.time > 3 and self.fuel > 0.0:
      self.thrust = True
      self.fuel -= 1
    else:
      self.thrust = False

    if self.thrust == False: # Thrust off, fall.
      self.v.add( Vector( - PI / 2, .05 ) ) # gravity
    else:
      vx = self.v.dx() # work with components for this
      vy = self.v.dy()
      vy *= .8

      if self.d == DIRECTION_LEFT and vx > -2:
        vx -= .1
      elif self.d == DIRECTION_RIGHT and vx < 2:
        vx += .1
      self.v = vecFromComps( vx, vy )

    self.p.move( self.v )

    if self.p.y <= 0.0: # hit the ground ?
      e.addObject( Explosion( self.p ) )
      return False

class MissileSmall( MissileBase ):
  missileImagesS = []
  exhaustImagesS = []

  def __init__( self, p, v, d, oType=OBJECT_TYPE_WEAPON ):
    MissileBase.__init__( self, p, v, d, oType )
    self.v.maxLen = 4.0
    self.wDamage = WEAPON_DAMAGE_MISSLE_S

    if len( MissileSmall.missileImagesS ) == 0:
      img = Image.open( "images/chopper/missileB_L.gif" )
      MissileSmall.missileImagesS.append( ImageTk.PhotoImage( img ) )
      img = Image.open( "images/chopper/missileB_R.gif" )
      MissileSmall.missileImagesS.append( ImageTk.PhotoImage( img ) )

      for lr in( "L.gif", "R.gif" ):
        img = Image.open( "images/chopper/exhaust" + lr )
        img = img.resize( ( 10, 7 ) )
        img = ImageTk.PhotoImage( img )
        MissileSmall.exhaustImagesS.append( img )

  def update( self, e ):
    return MissileBase.update( self, e )

  def draw( self, e, p ):
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )
    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT

    e.canvas.create_image( p.x, p.y, image=MissileSmall.missileImagesS[ d ] )
    if self.thrust:
      xOff = -30 if d else 30
      e.canvas.create_image( p.x + xOff, p.y, image=MissileSmall.exhaustImagesS[ d ] )
    e.canvas.create_rectangle( p.x - 10, projShadow.y, p.x + 10, projShadow.y, outline="black" )

class MissileLarge( MissileBase ):
  missileImagesL = []
  exhaustImagesL = []

  def __init__( self, p, v, d, oType=OBJECT_TYPE_WEAPON ):
    MissileBase.__init__( self, p, v, d, oType )
    self.wDamage = WEAPON_DAMAGE_MISSLE_L
    self.v.maxLen = 2.5

    if len( MissileLarge.missileImagesL ) == 0:
      img = Image.open( "images/chopper/missileA_L.gif" )
      MissileLarge.missileImagesL.append( ImageTk.PhotoImage( img ) )
      img = Image.open( "images/chopper/missileA_R.gif" )
      MissileLarge.missileImagesL.append( ImageTk.PhotoImage( img ) )

      for lr in( "L.gif", "R.gif" ):
        img = Image.open( "images/chopper/exhaust" + lr )
        img = img.resize( ( 20, 7 ) )
        img = ImageTk.PhotoImage( img )
        MissileLarge.exhaustImagesL.append( img )

  def update( self, e ):
    return MissileBase.update( self, e )

  def draw( self, e, p ):
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    e.canvas.create_image( p.x, p.y, image=MissileLarge.missileImagesL[ self.d ] )
    if self.thrust:
      xOff = -40 if self.d else 40
      e.canvas.create_image( p.x + xOff, p.y, image=MissileLarge.exhaustImagesL[ self.d ] )
    e.canvas.create_rectangle( p.x - 20, projShadow.y, p.x + 20, projShadow.y, outline="black" )

class Bomb():
  bombImage = None

  def __init__( self, p, v=None, oType=OBJECT_TYPE_WEAPON ):
    self.oType = oType
    self.p = Point( p.x, p.y, p.z )
    self.wDamage = WEAPON_DAMAGE_BOMB
    self.colRect = ( -.5, 1, .5, 0 )
    self.v = copy( v )
    self.active = True

    if not Bomb.bombImage:
      bombImage = Image.open( "images/chopper/bomb.gif" )
      bombImage = bombImage.resize( ( 10, 30 ) )
      Bomb.bombImage = ImageTk.PhotoImage( bombImage )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      self.active = False
      e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.active == False:
      return False

    self.v.add( Vector( -PI / 2, .05 ) ) # gravity
    self.p.move( self.v )

    if self.p.y <= 0.0:
      e.addObject( BombExplosion( self.p ) )
      return False

  def draw( self, e, p ):
    ps = projection( e.camera, Point( self.p.x, 0, self.p.z ) ) # Shadow
    e.canvas.create_image( p.x, p.y, image=Bomb.bombImage )
    e.canvas.create_rectangle( p.x - 5, ps.y, p.x + 5, ps.y, outline="black" )