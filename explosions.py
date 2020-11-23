import random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image

class Explosion():
  explosionImages = []  # List of lists

  def __init__( self, p ):
    self.p = Point( p.x, p.y, p.z )
    self.time = 0
    self.explosionIx = random.randint( 0, 1 ) # Just make this random for now.
    self.imgIx = 0

    if not Explosion.explosionImages:
      images = []
      img = Image.open( "images/explosions/Explosion1.gif" )
      for y in range( 0, 5 ):
        for x in range( 0, 5 ):
          SW = 64
          crop = img.crop( ( x * SW, y * SW, x * SW + SW, y * SW + SW ) )
          crop = ImageTk.PhotoImage( crop )
          images.append( crop )
      Explosion.explosionImages.append( images )

      images = []
      img = Image.open( "images/explosions/Explosion2.gif" )
      for y in range( 0, 6 ):
        for x in range( 0, 8 ):
          SW = 100
          crop = img.crop( ( x * SW + 15, y * SW + 36, x * SW + 115, y * SW + 124 ) )
          crop = ImageTk.PhotoImage( crop )
          images.append( crop )
      Explosion.explosionImages.append( images )

  def update( self, e ):
    self.time += 1

    self.imgIx = self.time
    if self.imgIx >= len( Explosion.explosionImages[ self.explosionIx ] ):
      e.addObject( SmokeA( self.p ) )
      return False
    return True

  def draw( self, e ):
    img = Explosion.explosionImages[ self.explosionIx ][ self.imgIx ]

    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 100 or proj.x < -100:
      return

    e.canvas.create_image( proj.x, proj.y, image=img )

class BombExplosion(): # Explosion that looks like something fell vertically.
  bombImages = [ ]

  def __init__( self, p ):
    self.p = Point( p.x, p.y + 10, p.z )
    self.time = 0
    self.imgIx = 0

    if not BombExplosion.bombImages:
      img = Image.open( "images/explosions/Bomb.png" ) # TBD not quite perfect cropping
      for y in range( 0, 2 ):
        for x in range( 0, 7 ):
          SW = 82
          SH = 96
          crop = img.crop( ( x * SW, y * SH, x * SW + SW, y * SH + SH ) )
          # crop = crop.resize( ( 150, 150 ) )
          crop = ImageTk.PhotoImage( crop )
          BombExplosion.bombImages.append( crop )
          if y == 1 and x == 3:
            break

  def update( self, e ):
    self.time += 1
    self.imgIx = self.time / 2
    if self.imgIx >= len( BombExplosion.bombImages ):
      e.addObject( SmokeV( Point( self.p.x,self.p.y - 10, self.p.z ) ) )
      return False

    return True

  def draw( self, e ):
    img = BombExplosion.bombImages[ self.imgIx ]

    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 100 or proj.x < -100:
      return

    e.canvas.create_image( proj.x, proj.y + 100, image=img )

class SmokeA(): # Small puff of smoke
  smokeAImages = [ ]

  def __init__( self, p ):
    self.p = Point( p.x, p.y, p.z )
    self.imgIx = 0

    if not SmokeA.smokeAImages:
      img = Image.open( "images/explosions/SmokeA.gif" )
      for y in range( 0, 4 ):
        for x in range( 0, 8 ):
          SW = 64
          SH = 64
          crop = img.crop( ( x * SW, y * SH, x * SW + SW, y * SH + SH ) )
          #crop = crop.resize( ( 150, 150 ) )
          crop = ImageTk.PhotoImage( crop )
          SmokeA.smokeAImages.append( crop )

  def update( self, e ):
    self.imgIx += 1
    if self.imgIx >= len( SmokeA.smokeAImages ):
      return False

    return True

  def draw( self, e ):
    img = SmokeA.smokeAImages[ self.imgIx ]

    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 100 or proj.x < -100:
      return

    e.canvas.create_image( proj.x, proj.y - 20, image=img )

class SmokeB(): # Larger smoke puff
  smokeBImages = []

  def __init__( self, p ):
    self.p = Point( p.x, p.y, p.z )
    self.imgIx = 0

    if not SmokeB.smokeBImages:
      img = Image.open( "images/explosions/SmokeB.gif" )
      for y in range( 0, 5 ):
        for x in range( 0, 8 ):
          SW = 64
          SH = 64
          crop = img.crop( ( x * SW + 1, y * SH, x * SW + SW - 1, y * SH + SH ) )
          #crop = crop.resize( ( 150, 150 ) )
          crop = ImageTk.PhotoImage( crop )
          SmokeB.smokeBImages.append( crop )

  def update( self, e ):
    self.imgIx += 1
    if self.imgIx >= len( SmokeB.smokeBImages ):
      return False

    return True

  def draw( self, e ):
    img = SmokeB.smokeBImages[ self.imgIx ]

    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 100 or proj.x < -100:
      return

    e.canvas.create_image( proj.x, proj.y, image=img )

class SmokeV(): # Vertical smoke
  smokeVImages = [ ]

  def __init__( self, p ):
    self.p = Point( p.x, p.y, p.z )
    self.imgIx = 0
    self.time = 0

    if not SmokeV.smokeVImages:
      SW = 37
      img = Image.open( "images/explosions/SmokeV.gif" )
      for x in range( 0, 10 ):
        crop = img.crop( ( x * SW, 20, 37 + x * SW, 220 ) )
        crop = crop.resize( ( 15 + x * 15, 15 + x * 15 ) )
        crop = ImageTk.PhotoImage( crop )
        SmokeV.smokeVImages.append( crop )

      for x in range( 0, 10 ):
        crop = img.crop( ( x * SW, 20, 37 + x * SW, 220 ) )
        # crop = crop.resize( ( 150, 15 + x * 15 ) )
        crop = ImageTk.PhotoImage( crop )
        SmokeV.smokeVImages.append( crop )

  def update( self, e ):
    self.time += 1

    self.imgIx = self.time / 2
    if self.imgIx >= len( SmokeV.smokeVImages ):
      return False

    return True

  def draw( self, e ):
    img = SmokeV.smokeVImages[ self.imgIx ]

    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 100 or proj.x < -100:
      return

    e.canvas.create_image( proj.x, proj.y - 90, image=img )