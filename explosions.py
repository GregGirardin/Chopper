import random
from utils import *
from tkinter import *
from PIL import ImageTk, Image

class Explosion():
  images = []  # List of lists

  def __init__( self, p ):
    self.oType = OBJECT_TYPE_NONE
    self.p = Point( p.x, p.y, p.z )
    self.time = 0
    self.colRect = ( 0, 0, 0, 0 )
    self.explosionIx = random.randint( 0, 1 ) # Just make this random for now.

    if not Explosion.images:
      images = []
      img = Image.open( "images/explosions/Explosion1.gif" )
      for y in range( 0, 5 ):
        for x in range( 0, 5 ):
          SW = 64
          crop = img.crop( ( x * SW, y * SW, x * SW + SW, y * SW + SW ) )
          crop = ImageTk.PhotoImage( crop )
          images.append( crop )
      Explosion.images.append( images )

      images = []
      img = Image.open( "images/explosions/Explosion2.gif" )
      for y in range( 0, 6 ):
        for x in range( 0, 8 ):
          SW = 100
          crop = img.crop( ( x * SW + 15, y * SW + 36, x * SW + 115, y * SW + 124 ) )
          crop = ImageTk.PhotoImage( crop )
          images.append( crop )
      Explosion.images.append( images )

  def processMessage( self, e, message, param=None ):
    pass

  def update( self, e ):
    self.time += 1

    if self.time >= len( Explosion.images[ self.explosionIx ] ):
      e.addObject( SmokeA( self.p ) )
      return False
    return True

  def draw( self, e, p ):
    img = Explosion.images[ self.explosionIx ][ self.time ]
    e.canvas.create_image( p.x, p.y, image=img )

class BombExplosion(): # Explosion that looks like something fell vertically.
  images = [ ]

  def __init__( self, p ):
    self.oType = OBJECT_TYPE_NONE
    self.p = Point( p.x, p.y + 10, p.z )
    self.time = 0
    self.colRect = ( 0, 0, 0, 0 )
    self.vy = 0

    if not BombExplosion.images:
      img = Image.open( "images/explosions/Bomb.png" ) # TBD not quite perfect cropping
      for y in range( 0, 2 ):
        for x in range( 0, 7 ):
          SW = 82
          SH = 96
          crop = img.crop( ( x * SW, y * SH, x * SW + SW, y * SH + SH ) )
          crop = ImageTk.PhotoImage( crop )
          BombExplosion.images.append( crop )
          if y == 1 and x == 3:
            break

  def processMessage( self, e, message, param=None ):
    pass

  def update( self, e ):
    self.time += 1
    if self.time >= len( BombExplosion.images ):
      return False

    return True

  def draw( self, e, p ):
    img = BombExplosion.images[ self.time ]
    e.canvas.create_image( p.x, p.y + 100, image=img )

class SmokeA(): # Small puff of smoke
  images = []

  def __init__( self, p ):
    self.oType = OBJECT_TYPE_NONE
    self.p = Point( p.x, p.y, p.z )
    self.time = 0
    self.colRect = ( 0, 0, 0, 0 )

    if not SmokeA.images:
      img = Image.open( "images/explosions/SmokeA.gif" )
      for y in range( 0, 4 ):
        for x in range( 0, 8 ):
          SW = 64
          SH = 64
          crop = img.crop( ( x * SW, y * SH, x * SW + SW, y * SH + SH ) )
          crop = ImageTk.PhotoImage( crop )
          SmokeA.images.append( crop )

  def processMessage( self, e, message, param=None ):
    pass

  def update( self, e ):
    self.time += 1
    if self.time >= len( SmokeA.images ):
      return False

    return True

  def draw( self, e, p ):
    img = SmokeA.images[ self.time ]
    e.canvas.create_image( p.x, p.y - 20, image=img )

class SmokeB(): # Larger smoke puff
  images = []

  def __init__( self, p ):
    self.oType = OBJECT_TYPE_NONE
    self.p = Point( p.x, p.y, p.z )
    self.time = 0
    self.colRect = ( 0, 0, 0, 0 )

    if not SmokeB.images:
      img = Image.open( "images/explosions/SmokeB.gif" )
      for y in range( 0, 5 ):
        for x in range( 0, 8 ):
          SW = 64
          SH = 64
          crop = img.crop( ( x * SW + 1, y * SH, x * SW + SW - 1, y * SH + SH ) )
          crop = ImageTk.PhotoImage( crop )
          SmokeB.images.append( crop )

  def processMessage( self, e, message, param=None ):
    pass

  def update( self, e ):
    self.time += 1
    if self.time >= len( SmokeB.images ):
      return False
    return True

  def draw( self, e, p ):
    img = SmokeB.images[ self.time ]
    e.canvas.create_image( p.x, p.y, image=img )

class SmokeV(): # Vertical smoke
  images = []

  def __init__( self, p ):
    self.oType = OBJECT_TYPE_NONE
    self.p = Point( p.x, p.y, p.z )
    self.time = 0
    self.colRect = ( 0, 0, 0, 0 )

    if not SmokeV.images:
      SW = 37
      img = Image.open( "images/explosions/SmokeV.gif" )
      for x in range( 0, 10 ):
        crop = img.crop( ( x * SW, 20, 37 + x * SW, 220 ) )
        crop = crop.resize( ( 15 + x * 15, 15 + x * 15 ) )
        crop = ImageTk.PhotoImage( crop )
        SmokeV.images.append( crop )

      for x in range( 0, 10 ):
        crop = img.crop( ( x * SW, 20, 37 + x * SW, 220 ) )
        crop = ImageTk.PhotoImage( crop )
        SmokeV.images.append( crop )

  def processMessage( self, e, message, param=None ):
    pass

  def update( self, e ):
    self.time += 1
    if self.time >= len( SmokeV.images ):
      return False
    return True

  def draw( self, e, p ):
    img = SmokeV.images[ self.time ]
    e.canvas.create_image( p.x, p.y - 90, image=img )