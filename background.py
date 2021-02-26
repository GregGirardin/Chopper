import constants
import random
from utils import *
from tkinter import *
from PIL import ImageTk, Image
from explosions import *

class SkyGround():
  image = None

  def  __init__( self ):
    self.p = Point( 0, 0, HORIZON_DISTANCE )
    self.oType = OBJECT_TYPE_NONE

    if not SkyGround.image:
      img = Image.open( "images/backgrounds/cloud2.png" )
      img = img.resize( ( 2000, 500 ) )

      SkyGround.image = ImageTk.PhotoImage( img )

  def draw( self, e, p ):
    hProj = projection( e.camera, self.p )
    # sky
    e.canvas.create_image( p.x + 200, p.y - 280, image=SkyGround.image )

    # p = [ 0, 0, SCREEN_WIDTH, 0, SCREEN_WIDTH, hProj.y, 0, hProj.y ]
    # e.canvas.create_polygon( p, fill="lightblue", outline="black" )

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
      img = img.resize( ( 3000, 250 ) )

      MountainImg.image = ImageTk.PhotoImage( img )

  def draw( self, e, p ):
    e.canvas.create_image( p.x, p.y - 100, image=MountainImg.image )

class HillImg():
  image = None

  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.oType = OBJECT_TYPE_NONE

    if not HillImg.image:
      img = Image.open( "images/backgrounds/Mountains2.gif" )
      img = img.resize( ( 4000, 150 ) )
      HillImg.image = ImageTk.PhotoImage( img )

  def draw( self, e, p ):
    pass
    e.canvas.create_image( p.x, p.y - 40, image=HillImg.image )

class Cloud():
  images = []
  ud_index = 0
  offset = [ 50, 25, 12 ]

  def __init__( self, x, y, z ):
    self.oType = OBJECT_TYPE_NONE
    self.p = Point( x, y, z )
    self.colRect = ( -3, 3, 3, 0 )

    if z < HORIZON_DISTANCE / 5:
      self.imgIx = 0
    elif z < HORIZON_DISTANCE / 3:
      self.imgIx = 1
    else:
      self.imgIx = 2

    Cloud.ud_index += 1
    self.checkTimer = Cloud.ud_index # Just to stagger the checks.

    if not Cloud.images:
      img = Image.open( "images/backgrounds/cloud.gif" )
      Cloud.images.append( ImageTk.PhotoImage( img ) )
      img2 = img.resize( ( 200, 100 ) )
      Cloud.images.append( ImageTk.PhotoImage( img2 ) )
      img2 = img.resize( ( 100, 50 ) )
      Cloud.images.append( ImageTk.PhotoImage( img2 ) )

  def update( self, e ):
    self.p.x -= 1

    self.checkTimer -= 1
    if self.checkTimer == 0:
      self.checkTimer = 20
      p = projection( e.camera, self.p )
      if p.x < -500: # Way off screen, move to the right of the screen
        foundX = False
        self.p.x = MAX_WORLD_X
        while not foundX:
          self.p.x += 100  # Move right until it doesn't show up on screen
          pTry = projection( e.camera, self.p )
          if pTry.x > SCREEN_WIDTH + 250:
            foundX = True
      return True

  def draw( self, e, p ):
    e.canvas.create_image( p.x, p.y - Cloud.offset[ self.imgIx ], image=Cloud.images[ self.imgIx ] )

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

    if z > 250: # far away? Use small sprite
      self.imgIndex = 3
    elif z > 50: # medium distance?
      self.imgIndex = 2
    else: # close
      self.imgIndex = random.randint( 0, 2 ) # two bigger gifs..

  def draw( self, e, p ):
    e.canvas.create_image( p.x, p.y - Tree.offsets[ self.imgIndex ], image=Tree.images[ self.imgIndex ] )

class Base():
  image = None

  def __init__( self, x, y, z, label=None ):
    self.p = Point( x, y, z )
    self.label = label
    self.oType = OBJECT_TYPE_BASE
    self.colRect = ( 0, 0, 0, 0 )
    self.maxAmount = ( 100.0, 200.0, 10.0, 4.0, 4.0, 10.0 )  # resources
    self.curAmount = [ 100.0, 200.0, 10.0, 4.0, 4.0, 10.0 ]
    if not Base.image:
      img = Image.open( "images/backgrounds/base.gif" )
      img = img.resize( ( 600, 300 ) )
      Base.image = ImageTk.PhotoImage( img )

  def processMessage( self, e, message, param=None ):
    if message == MSG_CHOPPER_AT_BASE:
      # Tighly coupled processMessage calling here, so be aware. obj can/will mutate curAmount[]
      # param is the object that wants resources
      param.processMessage( e, MSG_RESOURCES_AVAIL, param=self.curAmount )

  def update( self, e ):
    if not( e.time % 100 ):
      for r in range( RESOURCE_FIRST, RESOURCE_COUNT ):
        if self.curAmount[ r ] < self.maxAmount[ r ]:
          self.curAmount[ r ] += self.maxAmount[ r ] / 10 # replenish

  def draw( self, e, p ):
    e.canvas.create_image( p.x - 30, p.y - 50, image=Base.image )
    e.canvas.create_text( p.x - 50, p.y + 50, text=self.label, fill='black' )

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
    self.p = Point( x, 0, 2 )
    self.label = label
    self.b = b
    self.oType = OBJECT_TYPE_BUILDING
    self.si = SI_BUILDING
    self.colRect = ( -CityBuildings.imgInfo[ b ][ 3 ] / 40, CityBuildings.imgInfo[ b ][ 4 ] / 15,
                      CityBuildings.imgInfo[ b ][ 3 ] / 40, 0 )

    if not CityBuildings.imgInfo[ 0 ][ 0 ]:
      img = Image.open( "images/backgrounds/miscCity.gif" )

      for imgParams in CityBuildings.imgInfo:
        crop = img.crop( ( imgParams[ 1 ], imgParams[ 2 ],
                           imgParams[ 1 ] + imgParams[ 3 ], imgParams[ 2 ] + imgParams[ 4 ] ) )
        crop = crop.resize( ( int( imgParams[ 3 ] * 1.2 ), int( imgParams[ 4 ] * 1.2 ) ) )

        imgParams[ 0 ] = ImageTk.PhotoImage( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      #if param.oType == OBJECT_TYPE_E_WEAPON:
      self.si -= param.wDamage
      if self.si < 0:
        e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.si < 0.0:
      e.qMessage( MSG_BUILDING_DESTROYED )
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

class EBuilding(): # from miscBuildings.gif
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
    # Row 6
    [ None,   4, 427, 120, 47 ],
    [ None, 128, 429, 122, 45 ],
  ]

  numBuildings = len( imgInfo )

  def __init__( self, x, b, label=None ):
    self.oType = OBJECT_TYPE_E_BUILDING
    self.p = Point( x, 0, 3 )
    self.colRect = ( -EBuilding.imgInfo[ b ][ 3 ] / 30,
                      EBuilding.imgInfo[ b ][ 4 ] / 10,
                      EBuilding.imgInfo[ b ][ 3 ] / 30,
                      0 )
    self.label = label
    self.b = b
    self.si =  self.siMax = SI_E_BUILDING
    self.points = POINTS_E_BUILDING
    self.showSICount = 0

    if not EBuilding.imgInfo[ 0 ][ 0 ]:
      img = Image.open( "images/backgrounds/miscBuildings.gif" )

      for imgParams in EBuilding.imgInfo:
        crop = img.crop( ( imgParams[ 1 ],
                           imgParams[ 2 ],
                           imgParams[ 1 ] + imgParams[ 3 ],
                           imgParams[ 2 ] + imgParams[ 4 ] ) )
        crop = crop.resize( ( imgParams[ 3 ] * 2, imgParams[ 4 ] * 2 ) )
        imgParams[ 0 ] = ImageTk.PhotoImage( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      self.showSICount = SHOW_SI_COUNT
      if param.oType == OBJECT_TYPE_WEAPON:
        self.si -= param.wDamage
        #if self.si < 0:
        #  e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.si < 0.0:
      e.qMessage( MSG_E_BUILDING_DESTROYED, self )
      return False
    return True

  def draw( self, e, p ):
    sb = EBuilding.imgInfo[ self.b ] # Sprite info shortcut.

    if self.label:
      e.canvas.create_text( p.x, p.y + 10, text=self.label, fill='black' )
    p.y -= sb[ 4 ]
    e.canvas.create_image( p.x, p.y, image=sb[ 0 ] )
    showSI( e.canvas, p, self )

def buildEBase( e, x, bCount, label=None ):
  assert( bCount >= 2 and bCount < EBuilding.numBuildings )

  for b in range( 0, bCount ):
    ix = random.randint( 0, EBuilding.numBuildings - 1 )
    e.objects.append( EBuilding( x, ix, label="Enemy" ) )
    x += EBuilding.imgInfo[ ix ][ 3 ] / 10 # adjust pixels to world coors.