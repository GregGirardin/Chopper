import constants
import random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image

class SkyGround():
  def  __init__( self ):
    self.p = Point( 0, 0, HORIZON_DISTANCE )
    self.oType = OBJECT_TYPE_NONE

  def draw( self, e ):
    hProj = projection( e.camera, self.p )
    # sky
    p = [ 0, 0, SCREEN_WIDTH, 0, SCREEN_WIDTH, hProj.y, 0, hProj.y ]
    e.canvas.create_polygon( p, fill="lightblue", outline="black" )
    # ground
    p = [ 0, hProj.y, SCREEN_WIDTH, hProj.y, SCREEN_WIDTH, SCREEN_HEIGHT, 0, SCREEN_HEIGHT ]
    e.canvas.create_polygon( p, fill="darkgreen", outline="black" )

class Mountain():
  '''/
    Mountain is defined by X coordinate, width, Height, and Z position (distance from camera)
        TT
       TTTT
      BBBBBB
     BBBBBBBB
    BBBBBBBBBB
    X
    |--- W --|
  '''
  def __init__( self, x, w, h, z ):
    self.x = x
    self.w = w
    self.h = h
    self.z = z
    self.color = "gray"
    self.p = Point( x, 0, z )
    self.oType = OBJECT_TYPE_NONE

  def draw( self, e ):
    # world coordinates
    pL = Point( self.x, 0, self.z ) # base left
    pR = Point( self.x + self.w, 0, self.z ) # base right
    pT = Point( self.x + self.w / 2, self.h, self.z ) # top

    # translated to raster coordinates
    pL_p = projection( e.camera, pL )
    pR_p = projection( e.camera, pR )
    pT_p = projection( e.camera, pT )

    if pL_p.x > SCREEN_WIDTH or pR_p.x < 0: # off screen?
      return

    p = [ pL_p.x, pL_p.y, pT_p.x, pT_p.y, pR_p.x, pR_p.y ]

    e.canvas.create_polygon( p, fill="grey", outline="black" )

class City():
  image = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.oType = OBJECT_TYPE_NONE

    if not City.image:
      img = Image.open( "images/backgrounds/city.png" )
      img = img.resize( ( 1600, 800 ) )
      City.image = ImageTk.PhotoImage( img )

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    proj.x -= 400 # make right edge the center
    proj.y -= 250 # shift up.
    if proj.x < SCREEN_WIDTH + 800 and proj.x > -800:
      e.canvas.create_image( proj.x, proj.y, image=City.image )

class Cloud():
  image = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.oType = OBJECT_TYPE_NONE

    if not Cloud.image:
      img = Image.open( "images/backgrounds/cloud.gif" )
      Cloud.image = ImageTk.PhotoImage( img )

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 500: # Wrap
      self.p.x -= 3000
    elif proj.x < -500:
      self.p.x += 3000
    else:
      e.canvas.create_image( proj.x, proj.y, image=Cloud.image )

class Rock():
  image = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.oType = OBJECT_TYPE_NONE

    if not Rock.image:
      img = Image.open( "images/backgrounds/rock1.gif" )
      Rock.image = ImageTk.PhotoImage( img )

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 500:
      self.p.x -= 1000
    elif proj.x < -500:
      self.p.x += 1000
    else:
      e.canvas.create_image( proj.x, proj.y, image=Rock.image )

class Grass():
  image = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.oType = OBJECT_TYPE_NONE

    if not Grass.image:
      img = Image.open( "images/backgrounds/grass1.gif" )
      img = img.resize( ( 200, 30 ) )

      Grass.image = ImageTk.PhotoImage( img )

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 500:
      self.p.x -= 1000
    elif proj.x < -500:
      self.p.x += 1000
    else:
      e.canvas.create_image( proj.x, proj.y, image=Grass.image )

class Tree():
  images = []

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.oType = OBJECT_TYPE_NONE

    if len( Tree.images ) == 0:
      img = Image.open( "images/backgrounds/tree3.gif" )
      rs_img = img.resize( ( 100, 100 ) )
      Tree.images.append( ImageTk.PhotoImage( rs_img ) )

      img = Image.open( "images/backgrounds/tree.gif" )
      rs_img = img.resize( ( 380 / 2, 468 / 2 ) )
      Tree.images.append( ImageTk.PhotoImage( rs_img ) )
      rs_img = img.resize( ( 380 / 6, 468 / 6 ) )
      Tree.images.append( ImageTk.PhotoImage( rs_img ) )
      rs_img = img.resize( ( 380 / 12, 468 / 12 ) )
      Tree.images.append( ImageTk.PhotoImage( rs_img ) )

    if self.p.z > 250:
      self.imgIndex = 3
    elif self.p.z > 125:
      self.imgIndex = 2
    else:
      self.imgIndex = random.randint( 0, 2 ) # two bigger gifs..

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    proj.y -= 20 # make x,y the bottom of the gif
    if proj.x > SCREEN_WIDTH + 100: # wrap / repeat the trees
      self.p.x -= 1000
    elif proj.x < -100:
      self.p.x += 1000

    e.canvas.create_image( proj.x, proj.y, image=Tree.images[ self.imgIndex ] )

class Base():
  image = None

  def __init__( self, x, y, z, label=None ):
    self.p = Point( x, y, z )
    self.label = label
    self.oType = OBJECT_TYPE_BASE

    if not Base.image:
      img = Image.open( "images/backgrounds/base.gif" )
      img = img.resize( ( 600, 300 ) )
      Base.image = ImageTk.PhotoImage( img )

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    proj.x -= 30
    proj.y -= 50
    if proj.x < SCREEN_WIDTH + 500 and proj.x > -500:
      e.canvas.create_image( proj.x, proj.y, image=Base.image )
      e.canvas.create_text( proj.x, proj.y + 100, text=self.label, fill='black' )