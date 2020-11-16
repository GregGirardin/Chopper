import constants
import math, random
from utils import *
from PIL import ImageTk, Image

heloImages = {} # Dictionary of chopper images

class Helicopter():
  def __init__( self, x, y, z ):
    self.fuel = 100
    self.thrust = THRUST_NONE
    self.angle = 0.0 # + is facing up
    self.p = Point( x, y, z )
    self.rotorTheta = 0.0
    self.loadImages()
    self.images = heloImages
    self.vertVelocity = 0
    self.velocity = 0

  def loadImages( self ):
    global heloImages

    if len( heloImages ) == 0:
      heloImages[ "bodyF" ] = ImageTk.PhotoImage( Image.open( "images/chopper/bodyForward.gif" ) )

      heloImages[ "bodyLeft" ] = ImageTk.PhotoImage( Image.open( "images/chopper/bodyLeft.gif" ) )
      heloImages[ "bodyLeftD5" ] = ImageTk.PhotoImage( Image.open( "images/chopper/bodyLeftD5.gif" ) )
      heloImages[ "bodyLeftD10" ] = ImageTk.PhotoImage( Image.open( "images/chopper/bodyLeftD10.gif" ) )
      heloImages[ "bodyLeftU5" ] = ImageTk.PhotoImage( Image.open( "images/chopper/bodyLeftU5.gif" ) )

      heloImages[ "rotorA" ] = ImageTk.PhotoImage( Image.open( "images/chopper/rotorA.gif" ) )
      heloImages[ "rotorRearA" ] = ImageTk.PhotoImage( Image.open( "images/chopper/rotorRearA.gif" ) )
    self.images = heloImages

  def update( self, e ):
    self.rotorTheta += self.thrust / 2.0
    if self.rotorTheta > 2 * PI:
      self.rotorTheta -= 2 * PI

    self.thrust = THRUST_LOW

    self.p.y += self.vertVelocity
    if self.p.y > MAX_ALTITUDE:
      self.p.y = MAX_ALTITUDE
      self.vertVelocity = 0
    elif self.p.y < 0:
      self.p.y = 0
      self.vertVelocity = 0
      self.thrust = THRUST_NONE

    if self.vertVelocity > 0:
      self.thrust = THRUST_HIGH

    self.p.x += self.velocity

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )
    img = self.images[ "bodyLeft" ]
    # body
    e.canvas.create_image( proj.x + 30, proj.y - 20, image=img ) # puts 0,0 where the body hits the rotor
    # rotor
    rotorLen = 70 * math.cos( self.rotorTheta )
    e.canvas.create_rectangle( proj.x - rotorLen, proj.y - 34, proj.x + rotorLen, proj.y - 34, outline="black" )
    # tail rotor
    e.canvas.create_line( ( proj.x + 94 ) + 20 * math.cos( self. rotorTheta ),
                          ( proj.y - 37 ) + 20 * math.sin( self. rotorTheta ),
                          ( proj.x + 94 ) + 20 * math.cos( self. rotorTheta + 3.14 ),
                          ( proj.y - 37 ) + 20 * math.sin( self. rotorTheta + 3.14 ) )

    # shadow
    e.canvas.create_rectangle( proj.x - 40, projShadow.y, proj.x + 80, projShadow.y, outline="black" )
