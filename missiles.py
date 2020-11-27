import constants
import math, random
from utils import *
from explosions import *
from Tkinter import *
from PIL import ImageTk, Image

BULLET_LIFETIME = 100

class Bullet():
  def __init__( self, p, v, d, oType=OBJECT_TYPE_WEAPON ):
    self.oType = oType # can be OBJECT_TYPE_WEAPON or OBJECT_TYPE_E_WEAPON if sourced from an enemy.
    self.wDamage = WEAPON_DAMAGE_BULLET
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( 0, 0, 1, 1 )
    self.time = 0
    self.v = v
    self.d = d
    self.vx = self.v * math.cos( self.d )
    self.vy = self.v * math.sin( self.d )

  def processMessage( self, e, message, param=None ):

    if message == MSG_COLLISION_DET:
      e.addObject( SmokeA( Point( self.p.x, self.p.y, self.p.z ) ) )
      self.time = BULLET_LIFETIME + 1

  def update( self, e ):
    if self.time > BULLET_LIFETIME:
      return False

    self.time += 1
    self.p.x += self.vx
    self.p.y += self.vy

    if self.p.y < 0.0:
      e.addObject( SmokeA( Point( self.p.x, self.p.y, self.p.z ) ) )
      return False

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 100 or proj.x < -100:
      return

    e.canvas.create_line( proj.x, proj.y,
                          proj.x + 4.0 * math.cos( self.d ),
                          proj.y + 4.0 * math.sin( self.d ),
                          fill="black",
                          width=2 )

# Base class for missiles
class MissileBase():
  def __init__( self, p, vx, vy, d, oType=OBJECT_TYPE_WEAPON ):
    self.oType = oType
    self.colRect = ( -1, 1, 1, 0 )
    self.p = Point( p.x, p.y, p.z )
    self.vx = vx # Velocity x and y
    self.vy = vy
    self.fuel = 60
    self.time = 0
    self.thrust = False
    self.d = d # Direction

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      e.addObject( Explosion( self.p ) )
      self.time = -1 # trick to make it disappear rather than use another flag

  def update( self, e ):
    if self.time < 0:
      return False
    self.time += 1

    if self.time > 3 and self.fuel > 0.0:
      self.thrust = True
      self.fuel -= 1
    else:
      self.thrust = False

    if self.thrust == True:
      if self.vy < 0.0:
        self.vy += .1
        if self.vy > -.1:
          self.vy = 0
      if self.d == DIRECTION_LEFT:
        if self.vx > -self.maxVelocity:
          self.vx -= .1
      else:
        if self.vx < self.maxVelocity:
          self.vx += .1
    else: # Thrust off, fall.
      if self.vy > -1.0:
        self.vy -= .05
      self.vx *= .95

    self.p.x += self.vx
    self.p.y += self.vy

    if self.p.y <= 0.0: # hit the ground ?
      e.addObject( Explosion( self.p ) )
      return False

class MissileSmall( MissileBase ):
  missileImagesS = []
  exhaustImagesS = []

  def __init__( self, p, vx, vy, d,oType=OBJECT_TYPE_WEAPON ):
    MissileBase.__init__( self, p, vx, vy, d, oType )
    self.wDamage = WEAPON_DAMAGE_MISSLE_S
    self.maxVelocity = 4.0

    if len( MissileSmall.missileImagesS ) == 0:
      img = Image.open( "images/chopper/missileB_L.gif" )
      MissileSmall.missileImagesS.append( ImageTk.PhotoImage( img ) )
      img = Image.open( "images/chopper/missileB_R.gif" )
      MissileSmall.missileImagesS.append( ImageTk.PhotoImage( img ) )

      for lr in ( "L.gif", "R.gif" ):
        img = Image.open( "images/chopper/exhaust" + lr )
        img = img.resize( ( 10, 7 ) )
        img = ImageTk.PhotoImage( img )
        MissileSmall.exhaustImagesS.append( img )

  def update( self, e ):
    return MissileBase.update( self, e )

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )
    e.canvas.create_image( proj.x, proj.y, image=MissileSmall.missileImagesS[ self.d ] )
    if self.thrust:
      xOff = -30 if self.d else 30
      e.canvas.create_image( proj.x + xOff, proj.y, image=MissileSmall.exhaustImagesS[ self.d ] )
    e.canvas.create_rectangle( proj.x - 10, projShadow.y, proj.x + 10, projShadow.y, outline="black" )

class MissileLarge( MissileBase ):
  missileImagesL = []
  exhaustImagesL = []

  def __init__( self, p, vx, vy, d, oType=OBJECT_TYPE_WEAPON ):
    MissileBase.__init__( self, p, vx, vy, d, oType )
    self.wDamage = WEAPON_DAMAGE_MISSLE_L
    self.maxVelocity = 2.5

    if len( MissileLarge.missileImagesL ) == 0:
      img = Image.open( "images/chopper/missileA_L.gif" )
      MissileLarge.missileImagesL.append( ImageTk.PhotoImage( img ) )
      img = Image.open( "images/chopper/missileA_R.gif" )
      MissileLarge.missileImagesL.append( ImageTk.PhotoImage( img ) )

      for lr in ( "L.gif", "R.gif" ):
        img = Image.open( "images/chopper/exhaust" + lr )
        img = img.resize( ( 20, 7 ) )
        img = ImageTk.PhotoImage( img )
        MissileLarge.exhaustImagesL.append( img )

  def update( self, e ):
    return MissileBase.update( self, e )

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    e.canvas.create_image( proj.x, proj.y, image=MissileLarge.missileImagesL[ self.d ] )
    if self.thrust:
      xOff = -40 if self.d else 40
      e.canvas.create_image( proj.x + xOff, proj.y, image=MissileLarge.exhaustImagesL[ self.d ] )
    e.canvas.create_rectangle( proj.x - 20, projShadow.y, proj.x + 20, projShadow.y, outline="black" )

class Bomb():
  bombImage = None

  def __init__( self, p, vx, vy, oType=OBJECT_TYPE_WEAPON ):
    self.oType = oType
    self.wDamage = WEAPON_DAMAGE_BOMB
    self.colRect = ( -.5, 1, .5, 0 )
    self.p = Point( p.x, p.y, p.z )
    self.vx = vx
    self.vy = vy
    self.time = 0

    if not Bomb.bombImage:
      bombImage = Image.open( "images/chopper/bomb.gif" )
      bombImage = bombImage.resize( ( 10, 30 ) )
      Bomb.bombImage = ImageTk.PhotoImage( bombImage )

  def processMessage( self, e, message, param=None ):

    if message == MSG_COLLISION_DET:
      e.addObject( BombExplosion( self.p ) )
      self.time = -1  # trick to make it disappear rather than use another flag

  def update( self, e ):
    if self.time < 0:
      return False
    self.time += 1

    if self.vy > -1.0:
      self.vy -= .05
    self.vx *= .95

    self.p.y += self.vy
    self.p.x += self.vx

    if self.p.y <= 0.0:
      e.addObject( BombExplosion( self.p ) )
      return False

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    ps = projection( e.camera, Point( self.p.x, 0, self.p.z ) ) # Shadow
    e.canvas.create_image( proj.x, proj.y, image=Bomb.bombImage )
    e.canvas.create_rectangle( proj.x - 5, ps.y, proj.x + 5, ps.y, outline="black" )
