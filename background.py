import constants
import random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image
from explosions import *

class SkyGround():
  def  __init__( self ):
    self.p = Point( 0, 0, HORIZON_DISTANCE )
    self.oType = OBJECT_TYPE_NONE

  def draw( self, e, p ):
    hProj = projection( e.camera, self.p )
    # sky
    p = [ 0, 0, SCREEN_WIDTH, 0, SCREEN_WIDTH, hProj.y, 0, hProj.y ]
    e.canvas.create_polygon( p, fill="lightblue", outline="black" )
    # ground
    p = [ 0, hProj.y, SCREEN_WIDTH, hProj.y, SCREEN_WIDTH, SCREEN_HEIGHT, 0, SCREEN_HEIGHT ]
    e.canvas.create_polygon( p, fill="darkgreen", outline="black" )

class Mountain():
  '''
    Triangle mountains.
    Mountain is defined by X coordinate, width, Height, and Z position (distance from camera)
        TT
       TTTT
      BBBBBB
     BBBBBBBB
    BBBBBBBBBB
    X
    |--- W --|

    To generate a range of mountains..

    for z in( MAX_MTN_DISTANCE, MAX_MTN_DISTANCE * .75, MAX_MTN_DISTANCE * .5 ):
      for _ in range( 1, MTN_PER_LAYER ):
        self.bg_objects.append( Mountain( random.randint( MIN_WORLD_X - 1000,
                                                          MAX_WORLD_X + 1000 ),
                                          random.randint( MAX_MTN_WIDTH / 4, MAX_MTN_WIDTH ),
                                          random.randint( MAX_MTN_HEIGHT / 4, MAX_MTN_HEIGHT ),


  '''
  def __init__( self, x, w, h, z ):
    self.x = x
    self.w = w
    self.h = h
    self.z = z
    self.color = "gray"
    self.p = Point( x, 0, z )
    self.oType = OBJECT_TYPE_NONE

  def draw( self, e, p ):
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

class MountainImg():
  image = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.oType = OBJECT_TYPE_NONE

    if not MountainImg.image:
      img = Image.open( "images/backgrounds/Mountains1.gif" )
      MountainImg.image = ImageTk.PhotoImage( img )

  def draw( self, e, p ):
    e.canvas.create_image( p.x, p.y - 204, image=MountainImg.image )

class Cloud():
  image = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.oType = OBJECT_TYPE_NONE

    if not Cloud.image:
      img = Image.open( "images/backgrounds/cloud.gif" )
      Cloud.image = ImageTk.PhotoImage( img )

  def draw( self, e, p ):
    self.p.x -= 1 # background object so we don't call update..
    if self.p.x < MIN_WORLD_X - 1000:
      self.p.x = MAX_WORLD_X

    e.canvas.create_image( p.x, p.y, image=Cloud.image )

class Rock():
  image = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.oType = OBJECT_TYPE_NONE

    if not Rock.image:
      img = Image.open( "images/backgrounds/rock1.gif" )
      Rock.image = ImageTk.PhotoImage( img )

  def draw( self, e, p ):
    e.canvas.create_image( p.x, p.y, image=Rock.image )

class Grass():
  image = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.oType = OBJECT_TYPE_NONE

    if not Grass.image:
      img = Image.open( "images/backgrounds/grass1.gif" )
      img = img.resize( ( 200, 30 ) )
      Grass.image = ImageTk.PhotoImage( img )

  def draw( self, e, p ):
    e.canvas.create_image( p.x, p.y, image=Grass.image )

class Tree():
  images = []
  offsets = [ 50, 117, 39, 20 ]
  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.oType = OBJECT_TYPE_NONE

    if len( Tree.images ) == 0:
      img = Image.open( "images/backgrounds/tree3.gif" )
      rs_img = img.resize( ( 100, 100 ) )
      Tree.images.append( ImageTk.PhotoImage( rs_img ) )

      img = Image.open( "images/backgrounds/tree.gif" )
      rs_img = img.resize( ( 190, 234 ) )
      Tree.images.append( ImageTk.PhotoImage( rs_img ) )
      rs_img = img.resize( ( 63, 78 ) )
      Tree.images.append( ImageTk.PhotoImage( rs_img ) )
      rs_img = img.resize( ( 32, 39 ) )
      Tree.images.append( ImageTk.PhotoImage( rs_img ) )

    if self.p.z > 250:
      self.imgIndex = 3
    elif self.p.z > 125:
      self.imgIndex = 2
    else:
      self.imgIndex = random.randint( 0, 2 ) # two bigger gifs..

  def draw( self, e, p ):
    e.canvas.create_image( p.x, p.y - Tree.offsets[ self.imgIndex ],
                           image=Tree.images[ self.imgIndex ] )

class Base():
  image = None

  def __init__( self, x, y, z, label=None ):
    self.p = Point( x, y, z )
    self.label = label
    self.oType = OBJECT_TYPE_BASE
    self.visited = False # Have we landed here? May use to indicate game progress.

    if not Base.image:
      img = Image.open( "images/backgrounds/base.gif" )
      img = img.resize( ( 600, 300 ) )
      Base.image = ImageTk.PhotoImage( img )

  def draw( self, e, p ):
    proj = projection( e.camera, self.p )
    e.canvas.create_image( proj.x - 30, proj.y - 50, image=Base.image )
    e.canvas.create_text( proj.x - 50, proj.y + 50, text=self.label, fill='black' )

class CityBuildings():
  imgInfo =\
  [
    # Row 1
    [ None,  32,  13,  55, 265 ],  # PhotoImage, x,y,w,h
    [ None, 116,   7, 135, 296 ],
    [ None, 259,  10,  77, 126 ],
    [ None, 343,   2,  45, 196 ],
    [ None, 399,  15,  52, 504 ],
    [ None, 462,   6, 107, 279 ],
    [ None, 585,  11,  54, 249 ],
    [ None, 640,  11, 120, 193 ],
    [ None, 882,   6,  51, 328 ],
    # Row 2
    [ None,  20, 291,  77, 396 ],
    [ None, 137, 334,  96, 393 ],
    [ None, 284, 268, 100, 427 ],
    [ None, 556, 289, 86,  397 ],
  ]

  numBuildings = len( imgInfo )

  def __init__( self, x, b, label=None ):
    self.p = Point( x, 0, 3 )
    self.label = label
    self.b = b
    self.oType = OBJECT_TYPE_BUILDING
    self.health = SI_BUILDING
    self.colRect = ( -CityBuildings.imgInfo[ b ][ 3 ] / 40,
                      CityBuildings.imgInfo[ b ][ 4 ] / 20,
                      CityBuildings.imgInfo[ b ][ 3 ] / 40,
                      0 )

    if not CityBuildings.imgInfo[ 0 ][ 0 ]: # If PhotoImage is None we haven't loaded yet
      img = Image.open( "images/backgrounds/miscCity.gif" )

      for imgParams in CityBuildings.imgInfo:
        crop = img.crop( ( imgParams[ 1 ],
                           imgParams[ 2 ],
                           imgParams[ 1 ] + imgParams[ 3 ],
                           imgParams[ 2 ] + imgParams[ 4 ] ) )
        crop = crop.resize( ( imgParams[ 3 ], imgParams[ 4 ] ) )

        imgParams[ 0 ] = ImageTk.PhotoImage( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.health -= param.wDamage
        if self.health < 0:
          e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.health < 0.0:
      e.qMessage( MSG_BUILDING_DESTROYED, self )
      return False
    return True

  def draw( self, e, p ):
    sb = CityBuildings.imgInfo[ self.b ] # Sprite info shortcut.
    e.canvas.create_image( p.x, p.y - sb[ 4 ] / 2, image=sb[ 0 ] )
    if self.label:
      e.canvas.create_text( p.x, p.y, text=self.label, fill='black' )

def buildCity( e, x, bCount, label=None ):
  assert( bCount >= 2 and bCount < CityBuildings.numBuildings )

  for b in range( 0, bCount ):
    ix = random.randint( 0, CityBuildings.numBuildings - 1 )
    e.objects.append( CityBuildings( x, ix, label=label ) )
    x += CityBuildings.imgInfo[ ix ][ 3 ] / 20

class Building(): # from miscBuildings.gif
  imgInfo = \
  [
    # First row
    [ None,   4,   3, 153, 94 ],  # PhotoImage, x,y,w,h
    [ None, 164,   3, 151, 93 ],
    [ None, 322,   9,  84, 88 ],
    [ None, 413,   9,  85, 88 ],
    [ None, 506,  10, 128, 38 ],
    [ None, 637,  10, 127, 38 ],
    [ None, 507,  51, 173, 63 ],
    [ None, 687,  50,  86, 64 ],
    # Row 2
    [ None,   3, 104, 126, 85 ],
    [ None,   3, 104, 126, 85 ],
    [ None, 363, 103,  96, 85 ],
    [ None, 463, 118,  54, 77 ],
    [ None, 523, 121,  54, 74 ],
    [ None, 580, 118,  98, 77 ],
    [ None, 681, 118,  96, 77 ],
    # Row 3
    [ None,   3, 193,  90, 67 ],
    [ None,   3, 193,  90, 67 ],
    [ None, 189, 189,  67, 71 ],
    [ None, 328, 198,  46, 62 ],
    [ None, 424, 197,  93, 62 ],
    [ None, 518, 197,  93, 62 ],
    [ None, 619, 208,  95, 51 ],
    [ None, 715, 208,  68, 51 ],
    # Row 4
    # Row 6
    [ None,   4, 427, 120, 47 ],
    [ None, 128, 429, 122, 45 ],
  ]

  numBuildings = len( imgInfo )

  def __init__( self, x, b, label=None ):
    self.oType = OBJECT_TYPE_E_BUILDING
    self.p = Point( x, 0, 3 )
    self.colRect = ( -Building.imgInfo[ b ][ 3 ] / 20,
                      Building.imgInfo[ b ][ 4 ] / 10,
                      Building.imgInfo[ b ][ 3 ] / 20,
                      0 )
    self.label = label
    self.b = b
    self.si = SI_BUILDING

    if not Building.imgInfo[ 0 ][ 0 ]: # If PhotoImage is None we haven't loaded yet
      img = Image.open( "images/backgrounds/miscBuildings.gif" )

      for imgParams in Building.imgInfo:
        crop = img.crop( ( imgParams[ 1 ],
                           imgParams[ 2 ],
                           imgParams[ 1 ] + imgParams[ 3 ],
                           imgParams[ 2 ] + imgParams[ 4 ] ) )
        crop = crop.resize( ( imgParams[ 3 ] * 2, imgParams[ 4 ] * 2 ) )

        imgParams[ 0 ] = ImageTk.PhotoImage( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.si -= param.wDamage
        if self.si < 0:
          e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.si < 0.0:
      e.qMessage( MSG_E_BUILDING_DESTROYED, self )
      return False
    return True

  def draw( self, e, p ):
    sb = Building.imgInfo[ self.b ] # Sprite info shortcut.
    e.canvas.create_image( p.x, p.y - sb[ 4 ], image=sb[ 0 ] )
    if self.label:
      e.canvas.create_text( p.x, p.y + 30, text=self.label, fill='black' )

def buildBase( e, x, bCount, label=None ):
  assert( bCount >= 2 and bCount < Building.numBuildings )

  for b in range( 0, bCount ):
    ix = random.randint( 0, Building.numBuildings - 1 )
    e.objects.append( Building( x, ix, label=label ) )
    x += Building.imgInfo[ ix ][ 3 ] / 10 # adjust pixels to world coors.