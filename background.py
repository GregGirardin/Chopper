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
    if proj.x > SCREEN_WIDTH + 500:  # wrap / repeat the trees
      self.p.x -= 3000
    elif proj.x < -500:
      self.p.x += 3000
    else:
      e.canvas.create_image( proj.x, proj.y, image=cloudImage )

treeImages = []
class Tree():
  def __init__( self, x, y, z ):
    global treeImages

    self.p = Point( x, y, z )

    if len( treeImages ) == 0:
      img = Image.open( "images/tree.gif" )
      rs_img = img.resize( ( 380 / 2, 468 / 2 ) ) # half size, medium
      treeImages.append( ImageTk.PhotoImage( rs_img ) ) # full size, close
      rs_img = img.resize( ( 380 / 4, 468 / 4 ) ) # half size, medium
      treeImages.append( ImageTk.PhotoImage( rs_img ) )
      rs_img = img.resize( ( 380 / 8, 468 / 8) ) # 1/4 size, far
      treeImages.append( ImageTk.PhotoImage( rs_img ) )

  def update( self, e ):
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    if proj.x > SCREEN_WIDTH + 100: # wrap / repeat the trees
      self.p.x -= 1000
    elif proj.x < -100:
      self.p.x += 1000
    if self.p.z > 250:
      e.canvas.create_image( proj.x, proj.y, image=treeImages[ 2 ] )
    elif self.p.z > 100:
      e.canvas.create_image( proj.x, proj.y, image=treeImages[ 1 ] )
    else:
      e.canvas.create_image( proj.x, proj.y, image=treeImages[ 0 ] )
