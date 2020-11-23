import constants
import math, random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image

##########################
##########################
##########################
class Jet():
  jetImages = []

  def __init__( self, p, d=DIRECTION_LEFT, jType=2 ):
    self.jType = jType
    self.time = 0
    self.d = d
    self.p = Point( p.x, p.y, p.z )

    if len( Jet.jetImages ) == 0:
      images = []
      img = Image.open( "images/vehicles/Jet1.png" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 133 ) )
        crop = crop.resize( ( SW / 2, 133 / 2 ) )
        crop = ImageTk.PhotoImage( crop )
        images.append( crop )
      Jet.jetImages.append( images )

      images = []
      img = Image.open( "images/vehicles/Jet2.gif" )
      SW = 256
      for y in range( 0, 2 ):
        crop = img.crop( ( 0, y * SW, 640, y * SW + SW ) )
        crop = crop.resize( ( 640 / 2, 256 / 2 ) )
        crop = ImageTk.PhotoImage( crop )
        images.append( crop )
      Jet.jetImages.append( images )

      images = []
      img = Image.open( "images/vehicles/Jet3.gif" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 154 ) )
        crop = crop.resize( ( SW / 2, 154 / 2 ) )
        crop = ImageTk.PhotoImage( crop )
        images.append( crop )
      Jet.jetImages.append( images )

  def update( self, e ):
    self.time += 1
    if self.time > 500:
      return False

    jetDelta = [ .4, .4, 1.2 ]
    d = jetDelta[ self.jType ]

    self.p.x += d if self.d == DIRECTION_RIGHT else -d

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    e.canvas.create_image( proj.x, proj.y, image=Jet.jetImages[ self.jType ][ self.d ] )
    e.canvas.create_rectangle( proj.x - 60, projShadow.y, proj.x + 60, projShadow.y, outline="black" )
