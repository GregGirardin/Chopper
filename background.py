import constants
import math, random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image

class SkyGround():
  def  __init__( self ):
    self.p = Point( 0, 0, HORIZON_DISTANCE )

  def update( self, e ):
    return True

  def draw( self, e ):
    hProj = projection( e.camera, self.p )
    # sky
    p = [ 0, 0,
          SCREEN_WIDTH, 0,
          SCREEN_WIDTH, hProj.y,
          0, hProj.y ]

    e.canvas.create_polygon( p, fill="lightblue", outline="black" )
    # ground
    p = [ 0, hProj.y,
          SCREEN_WIDTH, hProj.y,
          SCREEN_WIDTH, SCREEN_HEIGHT,
          0, SCREEN_HEIGHT ]

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

  def update( self, e ):
    return True # mountains don't move or disappear

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

cloudImage = None
class Cloud():
  def __init__( self, x, y, z ):
    global cloudImage

    self.p = Point( x, y, z )

    if not cloudImage:
      img = Image.open( "images/cloud.gif" )
      cloudImage = ImageTk.PhotoImage( img )

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 500: # Wrap
      self.p.x -= 3000
    elif proj.x < -500:
      self.p.x += 3000
    else:
      e.canvas.create_image( proj.x, proj.y, image=cloudImage )

rockImage = None
class Rock():
  def __init__( self, x, y, z ):
    global rockImage

    self.p = Point( x, y, z )

    if not rockImage:
      img = Image.open( "images/rock1.gif" )
      rockImage = ImageTk.PhotoImage( img )

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 500:
      self.p.x -= 1000
    elif proj.x < -500:
      self.p.x += 1000
    else:
      e.canvas.create_image( proj.x, proj.y, image=rockImage )

grassImage = None
class Grass():
  def __init__( self, x, y, z ):
    global grassImage

    self.p = Point( x, y, z )

    if not grassImage:
      img = Image.open( "images/grass1.gif" )
      grassImage = ImageTk.PhotoImage( img )

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 500:
      self.p.x -= 1000
    elif proj.x < -500:
      self.p.x += 1000
    else:
      e.canvas.create_image( proj.x, proj.y, image=grassImage )

treeImages = []
class Tree():
  def __init__( self, x, y, z ):
    global treeImages

    self.p = Point( x, y, z )

    if len( treeImages ) == 0:
      img = Image.open( "images/tree3.gif" )
      rs_img = img.resize( ( 380 / 2, 468 / 2 ) )
      treeImages.append( ImageTk.PhotoImage( rs_img ) )

      img = Image.open( "images/tree.gif" )
      rs_img = img.resize( ( 380 / 2, 468 / 2 ) )
      treeImages.append( ImageTk.PhotoImage( rs_img ) )
      rs_img = img.resize( ( 380 / 4, 468 / 4 ) )
      treeImages.append( ImageTk.PhotoImage( rs_img ) )
      rs_img = img.resize( ( 380 / 8, 468 / 8 ) )
      treeImages.append( ImageTk.PhotoImage( rs_img ) )

    if self.p.z > 250:
      self.imgIndex = 3
    elif self.p.z > 125:
      self.imgIndex = 2
    else:
      self.imgIndex = random.randint( 0, 2 ) # two bigger gifs..

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    proj.y -= 50 # make x,y the bottom of the gif
    if proj.x > SCREEN_WIDTH + 100: # wrap / repeat the trees
      self.p.x -= 1000
    elif proj.x < -100:
      self.p.x += 1000

    e.canvas.create_image( proj.x, proj.y, image=treeImages[ self.imgIndex ] )

baseImage = None
class Base():
  def __init__( self, x, y, z ):
    global baseImage

    self.p = Point( x, y, z )

    if not baseImage:
      img = Image.open( "images/base.gif" )
      baseImage = img.resize( ( 200, 200) )
      baseImage = ImageTk.PhotoImage( baseImage )

  def update( self, e ):
    return True

  def draw( self, e ):
    global baseImage

    proj = projection( e.camera, self.p )
    proj.x -= 70
    proj.y -= 100
    if proj.x > SCREEN_WIDTH + 100: # wrap / repeat the trees
      return
    elif proj.x < -100:
      return
    e.canvas.create_image( proj.x, proj.y, image=baseImage )

# Debug
class dbgPoint():
  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    e.canvas.create_rectangle( proj.x - 5, proj.y, proj.x + 5, proj.y, outline="red" )
    e.canvas.create_rectangle( proj.x, proj.y - 5, proj.x, proj.y + 5, outline="red" )