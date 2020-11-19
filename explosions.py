import random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image

explosionImages = [] # List of lists

class Explosion():
  def __init__( self, p ):
    self.p = Point( p.x, p.y, p.z )
    self.time = 0
    self.explosionIx = random.randint( 0, 1 ) # Just make this random for now.
    self.imgIx = 0

    if not explosionImages:
      images = []
      img = Image.open( "images/explosions/Explosion1.gif" )
      for y in range( 0, 5 ):
        for x in range( 0, 5 ):
          SW = 64
          crop = img.crop( ( x * SW, y * SW, x * SW + SW, y * SW + SW ) )
          crop = ImageTk.PhotoImage( crop )
          images.append( crop )
      explosionImages.append( images )

      images = []
      img = Image.open( "images/explosions/Explosion2.gif" )
      for y in range( 0, 6 ):
        for x in range( 0, 8 ):
          SW = 100
          crop = img.crop( ( x * SW + 15, y * SW + 36, x * SW + 115, y * SW + 124 ) )
          crop = ImageTk.PhotoImage( crop )
          images.append( crop )
      explosionImages.append( images )

  def update( self, e ):
    self.time += 1

    self.imgIx = self.time
    if self.imgIx >= len( explosionImages[ self.explosionIx ] ):
      return False
    return True

  def draw( self, e ):
    img = explosionImages[ self.explosionIx ][ self.imgIx ]

    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 100 or proj.x < -100:
      return

    e.canvas.create_image( proj.x, proj.y, image=img )

bombImages = []
class BombExplosion(): # Explosion that looks like something fell vertically.
  def __init__( self, p ):
    self.p = Point( p.x, p.y + 10, p.z )
    self.time = 0
    self.imgIx = 0

    if not bombImages:
      img = Image.open( "images/explosions/Bomb.png" ) # TBD not quite perfect cropping
      for y in range( 0, 2 ):
        for x in range( 0, 7 ):
          SW = 82
          SH = 96
          crop = img.crop( ( x * SW, y * SH, x * SW + SW, y * SH + SH ) )
          # crop = crop.resize( ( 150, 150 ) )
          crop = ImageTk.PhotoImage( crop )
          bombImages.append( crop )
          if y == 1 and x == 3:
            break

  def update( self, e ):
    self.time += 1
    self.imgIx = self.time / 2
    if self.imgIx >= len( bombImages ):
      return False

    return True

  def draw( self, e ):
    img = bombImages[ self.imgIx ]

    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 100 or proj.x < -100:
      return

    e.canvas.create_image( proj.x, proj.y + 100, image=img )