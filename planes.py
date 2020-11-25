import constants
import math, random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image

##########################
##########################
##########################
class Bomber():
  images = []

  def __init__( self, p, d=DIRECTION_LEFT ):
    self.oType = OBJECT_TYPE_JET
    self.colRect = ( -6, 2, 6, 0 )
    self.time = 0
    self.d = d
    self.p = Point( p.x, p.y, p.z )

    if len( Bomber.images ) == 0:
      img = Image.open( "images/vehicles/Jet1.png" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 133 ) )
        crop = crop.resize( ( int( SW / 1.5 ), int( 133 / 1.5 ) ) )
        crop = ImageTk.PhotoImage( crop )
        Bomber.images.append( crop )

  def processMessage( self, message, param=None ):
    pass

  def update( self, e ):
    if e.debugCoords:
      return True

    self.time += 1
    if self.time > 500:
      return False

    self.p.x += BOMBER_DELTA if self.d == DIRECTION_RIGHT else -BOMBER_DELTA
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    e.canvas.create_image( proj.x, proj.y - 20,
                           image=Bomber.images[ self.d ] )
    e.canvas.create_rectangle( proj.x - 60, projShadow.y,
                               proj.x + 60, projShadow.y, outline="black" )

class Transporter():
  images = []

  def __init__( self, p, d=DIRECTION_LEFT ):
    self.oType = OBJECT_TYPE_JET
    self.colRect = ( -4, 2,4, 0 )
    self.time = 0
    self.d = d
    self.p = Point( p.x, p.y, p.z )

    if len( Transporter.images ) == 0:
      img = Image.open( "images/vehicles/Jet2.gif" )
      SW = 256
      for y in range( 0, 2 ):
        crop = img.crop( ( 0, y * SW, 640, y * SW + SW ) )
        crop = crop.resize( ( 640 / 3, 256 / 3 ) )
        crop = ImageTk.PhotoImage( crop )
        Transporter.images.append( crop )

  def processMessage( self, message, param=None ):
    pass

  def update( self, e ):
    if e.debugCoords:
      return True

    if self.time > 500:
      return False

    self.p.x += BOMBER_DELTA if self.d == DIRECTION_RIGHT else -BOMBER_DELTA
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    e.canvas.create_image( proj.x, proj.y - 40,
                           image=Transporter.images[ self.d ] )
    e.canvas.create_rectangle( proj.x - 60, projShadow.y,
                               proj.x + 60, projShadow.y, outline="black" )

class Fighter():
  images = []

  def __init__( self, p, d=DIRECTION_LEFT ):
    self.oType = OBJECT_TYPE_JET
    self.colRect = ( -4, 2, 4, 0 )
    self.time = 0
    self.d = d
    self.p = Point( p.x, p.y, p.z )

    if len( Fighter.images ) == 0:
      img = Image.open( "images/vehicles/Jet3.gif" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 154 ) )
        crop = crop.resize( ( SW / 3, 154 / 3 ) )
        crop = ImageTk.PhotoImage( crop )
        Fighter.images.append( crop )

  def processMessage( self, message, param=None ):
    pass

  def update( self, e ):
    if e.debugCoords:
      return True

    self.time += 1
    if e.time > 500:
      return False

    self.p.x += FIGHTER_DELTA if self.d == DIRECTION_RIGHT else -FIGHTER_DELTA
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    e.canvas.create_image( proj.x, proj.y - 25, image=Fighter.images[ self.d ] )
    e.canvas.create_rectangle( proj.x - 60, projShadow.y,
                               proj.x + 60, projShadow.y, outline="black" )