import constants
import math, random
from utils import *
from explosions import *
from Tkinter import *
from PIL import ImageTk, Image

# Base class for missiles
class MissileBase():
  def __init__( self, p, vx, vy, d ):
    self.p = Point( p.x, p.y, p.z )
    self.vx = vx # Velocity x and y
    self.vy = vy
    self.fuel = 60.0
    self.time = 0
    self.thrust = False
    self.d = d # Direction

  def update( self, e ):
    self.time += 1

    if self.time > 10 and self.fuel > 0.0:
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

missileImagesS = []
exhaustImagesS = []
class MissileSmall( MissileBase ):
  def __init__( self, p, vx, vy, d ):
    MissileBase.__init__( self, p, vx, vy, d )

    self.maxVelocity = 4.0

    if len( missileImagesS ) == 0:
      img = Image.open( "images/chopper/missileB_L.gif" )
      missileImagesS.append( ImageTk.PhotoImage( img ) )
      img = Image.open( "images/chopper/missileB_R.gif" )
      missileImagesS.append( ImageTk.PhotoImage( img ) )

      img = Image.open( "images/chopper/exhaustL.gif" )
      img = img.resize( ( 10, 7 ) )
      img = ImageTk.PhotoImage( img )
      exhaustImagesS.append( img )
      img = Image.open( "images/chopper/exhaustR.gif" )
      img = img.resize( ( 10, 7 ) )
      img = ImageTk.PhotoImage( img )
      exhaustImagesS.append( img )

  def update( self, e ):
    return MissileBase.update( self, e )

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )
    e.canvas.create_image( proj.x, proj.y, image=missileImagesS[ self.d ] )
    if self.thrust:
      xOff = -30 if self.d else 30
      e.canvas.create_image( proj.x + xOff, proj.y, image=exhaustImagesS[ self.d ] )
    e.canvas.create_rectangle( proj.x - 10,
                               projShadow.y,
                               proj.x + 10,
                               projShadow.y,
                               outline="black" )

missileImagesL = []
exhaustImagesL = []
class MissileLarge( MissileBase ):
  def __init__( self, p, vx, vy, d ):
    MissileBase.__init__( self, p, vx, vy, d )

    self.maxVelocity = 2.5

    if len( missileImagesL ) == 0:
      img = Image.open( "images/chopper/missileA_L.gif" )
      missileImagesL.append( ImageTk.PhotoImage( img ) )
      img = Image.open( "images/chopper/missileA_R.gif" )
      missileImagesL.append( ImageTk.PhotoImage( img ) )

      img = Image.open( "images/chopper/exhaustL.gif" )
      img = img.resize( ( 20, 7 ) )
      img = ImageTk.PhotoImage( img )
      exhaustImagesL.append( img )
      img = Image.open( "images/chopper/exhaustR.gif" )
      img = img.resize( ( 20, 7 ) )
      img = ImageTk.PhotoImage( img )
      exhaustImagesL.append( img )

  def update( self, e ):
    return MissileBase.update( self, e )

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    e.canvas.create_image( proj.x, proj.y, image=missileImagesL[ self.d ] )
    if self.thrust:
      xOff = -40 if self.d else 40
      e.canvas.create_image( proj.x + xOff, proj.y, image=exhaustImagesL[ self.d ] )

    e.canvas.create_rectangle( proj.x - 20, projShadow.y, proj.x + 20, projShadow.y, outline="black" )

bombImage = None
class Bomb():
  def __init__( self, p, vx, vy ):
    global bombImage
    self.p = Point( p.x, p.y, p.z )
    self.vx = vx
    self.vy = vy

    if not bombImage:
      bombImage = Image.open( "images/chopper/bomb.gif" )
      bombImage = bombImage.resize( ( 10, 30 ) )
      bombImage = ImageTk.PhotoImage( bombImage )

  def update( self, e ):
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
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    e.canvas.create_image( proj.x, proj.y, image=bombImage )
    e.canvas.create_rectangle( proj.x - 5, projShadow.y, proj.x + 5, projShadow.y, outline="black" )
