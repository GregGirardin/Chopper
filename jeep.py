import constants
import math, random
from utils import *
from explosions import *
from Tkinter import *
from PIL import ImageTk, Image

# Jeeps and trucks
class Jeep():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_JEEP
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -3, 3, 3, 1 )
    self.time = 0
    self.imgIx = 0
    self.bounceCount = 0
    self.v = v if v else Vector( PI, JEEP_DELTA )
    self.health = SI_JEEP

    if len( Jeep.images ) == 0:
      img = Image.open( "images/vehicles/Jeep.png" )
      SW = 256
      for y in ( 0, SW ):
        images = []
        for x in range( 0, 3 ):
          crop = img.crop( ( x * SW, y , x * SW + SW, y + SW ) )
          crop = crop.resize( ( 120, 120 ) )
          crop = ImageTk.PhotoImage( crop )
          images.append( crop)
        Jeep.images.append( images )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.health -= param.wDamage
        if self.health < 0:
          e.addObject( BombExplosion( self.p ) )

  # Draw wheels with circles instead of using sprites.
  def drawWheel( self, c, x, y, radius, angle ):
    # outer black / rubber, inner silver, inner white
    c.create_oval( x - radius, y - radius, x + radius, y + radius, fill="#111" )
    c.create_oval( x - radius * .65, y - radius * .65, x + radius * .65, y + radius * .65, fill="gray" )
    c.create_oval( x - radius * .33, y - radius * .33, x + radius * .33, y + radius * .33, fill="white" )

    # Draw lug nuts to indicate rotation
    theta = 0
    radius *= .5
    while theta < 2 * PI:
      lnx = x + radius * math.cos( theta - angle )
      lny = y - radius * math.sin( theta - angle )
      c.create_oval( lnx - 2, lny - 2, lnx + 2, lny + 2, fill="#fff" )
      theta += ( 2 * PI ) / 4

  def update( self, e ):
    if self.health < 0:
      e.addStatusMessage( "Jeep destroyed." )
      return False

    if not self.bounceCount:
      if random.randint( 0, 20 ) == 0: # Bounce occasionally, angle up / level / angle down / level
        self.bounceCount = 4

    self.imgIx = 0 # level
    if self.bounceCount:
      if self.bounceCount > 2:
        self.imgIx = 2 # angle up sprite
      elif self.bounceCount == 2:
        self.imgIx = 0 # level again
      elif self.bounceCount == 1:
        self.imgIx = 1 # angle down
      self.bounceCount -= 1

    if self.p.x < MIN_WORLD_X or self.p.x > MAX_WORLD_X:
      self.v.flipx()

    self.p.move( self.v )

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )

    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT

    e.canvas.create_image( proj.x, proj.y - 30, image=Jeep.images[ d ][ self.imgIx ] )
    wheelOffs = [ [ -43, 40 ], [ -38, 43 ] ]
    for xOff in wheelOffs[ d ]:
      self.drawWheel( e.canvas, proj.x + xOff, proj.y + 14 - 30, 12, self.p.x )

##############################################################################
class Transport1():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_TRANSPORT1
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -5, 1, 5, -1 )
    self.time = 0
    self.bounceCount = 0
    self.v = v if v else Vector( PI, TRANSPORT1_DELTA )
    self.health = SI_TRANSPORT1

    if len( Transport1.images ) == 0:
      img = Image.open( "images/vehicles/transport1.gif" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 128 ) )
        crop = crop.resize( ( 512 / 2, 128 / 2 ) )
        crop = ImageTk.PhotoImage( crop )
        Transport1.images.append( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.health -= param.wDamage
        if self.health < 0:
          e.addObject( BombExplosion( self.p ) )

  # Draw wheels with circles instead of using sprites.
  def drawWheel( self, c, x, y, radius, angle ):
    c.create_oval( x - radius, y - radius,
                   x + radius, y + radius, fill="#111" )  # outer black / rubber
    c.create_oval( x - radius * .65, y - radius * .65,
                   x + radius * .65, y + radius * .65, fill="gray" )  # inner silver
    c.create_oval( x - radius * .33, y - radius * .33,
                   x + radius * .33, y + radius * .33, fill="white" ) # inner white

    # Draw lug nuts to indicate rotation
    theta = 0
    radius *= .5
    while theta < 2 * PI:
      lnx = x + radius * math.cos( theta - angle )
      lny = y - radius * math.sin( theta - angle )
      c.create_oval( lnx - 2, lny - 2, lnx + 2, lny + 2, fill="#fff" )
      theta += ( 2 * PI ) / 5

  def update( self, e ):
    if self.health < 0:
      e.addStatusMessage( "Transport destroyed!" )
      return False

    if self.p.x < MIN_WORLD_X or self.p.x > MAX_WORLD_X:
      self.v.flipx()

    self.p.move( self.v )

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )

    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT

    e.canvas.create_image( proj.x, proj.y, image=Transport1.images[ d ] )

    wheelOffs = [ [ -65, -25, 25, 60 ], [ -65, -25, 25, 65 ] ]
    for xOff in wheelOffs[ d ]:
      self.drawWheel( e.canvas, proj.x + xOff, proj.y + 18, 15, self.p.x )

##############################################################################
class Transport2():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_TRANSPORT2
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -2, 1, 2, 0 )
    self.time = 0
    self.bounceCount = 0
    self.v = v if v else Vector( PI, TRANSPORT2_DELTA )
    self.health = SI_TRANSPORT2

    if len( Transport2.images ) == 0:
      img = Image.open( "images/vehicles/transport2.gif" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 256 ) )
        crop = crop.resize( ( 512 / 2, 256 / 2) )
        crop = ImageTk.PhotoImage( crop )
        Transport2.images.append( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.health -= param.wDamage
        if self.health < 0:
          e.addObject( BombExplosion( self.p ) )

  def drawWheel( self, c, x, y, radius, angle ):
    c.create_oval( x - radius, y - radius, x + radius, y + radius, fill="#111" )
    c.create_oval( x - radius * .65, y - radius * .65, x + radius * .65, y + radius * .65, fill="gray" )
    c.create_oval( x - radius * .33, y - radius * .33, x + radius * .33, y + radius * .33, fill="white" )

    # Draw lug nuts to indicate rotation
    theta = 0
    radius *= .5
    while theta < 2 * PI:
      lnx = x + radius * math.cos( theta - angle )
      lny = y - radius * math.sin( theta - angle )
      c.create_oval( lnx - 2, lny - 2, lnx + 2, lny + 2, fill="#fff" )
      theta += ( 2 * PI ) / 5

  def update( self, e ):
    if self.health < 0:
      e.addStatusMessage( "Transport destroyed!" )
      return False

    if self.p.x < MIN_WORLD_X or self.p.x > MAX_WORLD_X:
      self.v.flipx()

    self.p.move( self.v )

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT

    e.canvas.create_image( proj.x, proj.y, image=Transport2.images[ d ] )
    wheelOffs = [ [ -64, -25, 25, 64 ], [ -65, -27, 23, 62 ] ]
    for xOff in wheelOffs[ d ]:
      self.drawWheel( e.canvas, proj.x + xOff, proj.y + 25, 15, self.p.x )

##############################################################################
class Truck():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_TRUCK
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -2, 1, 2, 0 )
    self.time = 0
    self.bounceCount = 0
    self.v = v if v else Vector( PI, TRUCK_DELTA )
    self.health = SI_TRUCK

    if len( Truck.images ) == 0:
      img = Image.open( "images/vehicles/Truck1.gif" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 256 ) )
        crop = crop.resize( ( 512 / 3, 256 / 3 ) )
        crop = ImageTk.PhotoImage( crop )
        Truck.images.append( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.health -= param.wDamage
        if self.health < 0:
          e.addObject( BombExplosion( self.p ) )

  # Draw wheels with circles instead of using sprites.
  def drawWheel( self, c, x, y, radius, angle ):
    c.create_oval( x - radius, y - radius, x + radius, y + radius, fill="#111" )
    c.create_oval( x - radius * .65, y - radius * .65, x + radius * .65, y + radius * .65, fill="gray" )
    c.create_oval( x - radius * .33, y - radius * .33, x + radius * .33, y + radius * .33, fill="white" )

    # Draw lug nuts to indicate rotation
    theta = 0
    radius *= .5
    while theta < 2 * PI:
      lnx = x + radius * math.cos( theta - angle )
      lny = y - radius * math.sin( theta - angle )
      c.create_oval( lnx - 2, lny - 2, lnx + 2, lny + 2, fill="#fff" )
      theta += ( 2 * PI ) / 2

  def update( self, e ):
    if self.health < 0:
      e.addStatusMessage( "Truck destroyed!" )
      return False

    if self.p.x < MIN_WORLD_X or self.p.x > MAX_WORLD_X:
      self.v.flipx()
    self.p.move( self.v )

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )

    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT
    e.canvas.create_image( proj.x, proj.y, image=Truck.images[ d ] )

    wheelOffs = [ [ -58, 20, 50 ], [ -52, -20, 57 ] ]
    for xOff in wheelOffs[ d ]:
      self.drawWheel( e.canvas, proj.x + xOff, proj.y + 17, 12, self.p.x )