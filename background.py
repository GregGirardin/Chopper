import constants
import random
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
    return True # Mountains don't move or disappear

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

    p = [ pL_p.x, pL_p.y,
          pT_p.x, pT_p.y,
          pR_p.x, pR_p.y ]

    e.canvas.create_polygon( p, fill="grey", outline="black" )

class MountainGif():
  image = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )

    if not Rock.rockImage:
      img = Image.open( "images/backgrounds/mountain.gif" )
      MountainGif.image = ImageTk.PhotoImage( img )

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 500:
      self.p.x -= 1000
    elif proj.x < -500:
      self.p.x += 1000
    else:
      e.canvas.create_image( proj.x, proj.y, image=MountainGif.image )


class Cloud():
  cloudImage = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )

    if not Cloud.cloudImage:
      img = Image.open( "images/backgrounds/cloud.gif" )
      Cloud.cloudImage = ImageTk.PhotoImage( img )

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 500: # Wrap
      self.p.x -= 3000
    elif proj.x < -500:
      self.p.x += 3000
    else:
      e.canvas.create_image( proj.x, proj.y, image=Cloud.cloudImage )

class Rock():
  rockImage = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )

    if not Rock.rockImage:
      img = Image.open( "images/backgrounds/rock1.gif" )
      Rock.rockImage = ImageTk.PhotoImage( img )

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 500:
      self.p.x -= 1000
    elif proj.x < -500:
      self.p.x += 1000
    else:
      e.canvas.create_image( proj.x, proj.y, image=Rock.rockImage )

class Grass():
  grassImage = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )

    if not Grass.grassImage:
      img = Image.open( "images/backgrounds/grass1.gif" )
      img = img.resize( ( 200, 30 ) )

      Grass.grassImage = ImageTk.PhotoImage( img )

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 500:
      self.p.x -= 1000
    elif proj.x < -500:
      self.p.x += 1000
    else:
      e.canvas.create_image( proj.x, proj.y, image=Grass.grassImage )

class Tree():
  treeImages = []

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )

    if len( Tree.treeImages ) == 0:
      img = Image.open( "images/backgrounds/tree3.gif" )
      rs_img = img.resize( ( 100, 100 ) )
      Tree.treeImages.append( ImageTk.PhotoImage( rs_img ) )

      img = Image.open( "images/backgrounds/tree.gif" )
      rs_img = img.resize( ( 380 / 2, 468 / 2 ) )
      Tree.treeImages.append( ImageTk.PhotoImage( rs_img ) )
      rs_img = img.resize( ( 380 / 6, 468 / 6 ) )
      Tree.treeImages.append( ImageTk.PhotoImage( rs_img ) )
      rs_img = img.resize( ( 380 / 12, 468 / 12 ) )
      Tree.treeImages.append( ImageTk.PhotoImage( rs_img ) )

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
    proj.y -= 20 # make x,y the bottom of the gif
    if proj.x > SCREEN_WIDTH + 100: # wrap / repeat the trees
      self.p.x -= 1000
    elif proj.x < -100:
      self.p.x += 1000

    e.canvas.create_image( proj.x, proj.y,
                           image=Tree.treeImages[ self.imgIndex ] )
class Base():
  baseImage = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )

    if not Base.baseImage:
      img = Image.open( "images/base.gif" )
      img = img.resize( ( 600, 300 ) )
      Base.baseImage = ImageTk.PhotoImage( img )

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    proj.x -= 70
    proj.y -= 100
    if proj.x < SCREEN_WIDTH + 500 and proj.x > -500:
      e.canvas.create_image( proj.x - 200, proj.y + 50, image=Base.baseImage )

# Debug point
class dbgPoint():
  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    e.canvas.create_rectangle( proj.x, proj.y - 5, proj.x, proj.y, outline="red" )