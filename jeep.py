import constants
import math, random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image

# Jeeps and trucks
class Jeep():
  images = []

  def __init__( self, p, d=DIRECTION_LEFT ):
    self.oType = OBJECT_TYPE_JEEP
    self.colRect = ( -3, 1, 3, -1 )
    self.time = 0
    self.imgIx = 0
    self.bounceCount = 0
    self.d = d
    self.p = Point( p.x, p.y, p.z )

    if len( Jeep.images ) == 0:
      images = []
      img = Image.open( "images/vehicles/Jeep.png" )
      SW = 256
      for x in range( 0, 3 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, SW ) )
        crop = crop.resize( ( 120, 120 ) )
        crop = ImageTk.PhotoImage( crop )
        images.append( crop )
      Jeep.images.append( images )

      images = []
      for x in range( 0, 3 ):
        crop = img.crop( ( x * SW, SW, x * SW + SW, 2 * SW ) )
        crop = crop.resize( ( 120, 120 ) )
        crop = ImageTk.PhotoImage( crop )
        images.append( crop )
      Jeep.images.append( images )

  def processMessage( self, message, param=None ):
    pass

  # Draw wheels with circles instead of using sprites.
  def drawWheel( self, c, x, y, radius, angle ):
    # outer black / rubber
    c.create_oval( x - radius, y - radius, x + radius, y + radius, fill="#111" )
    # inner silver
    c.create_oval( x - radius * .65, y - radius * .65, x + radius * .65, y + radius * .65, fill="gray" )
    # inner white
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
    self.time += 1
    if self.time > 500:
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

    self.p.x += JEEP_DELTA if self.d == DIRECTION_RIGHT else -JEEP_DELTA

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )

    e.canvas.create_image( proj.x, proj.y, image=Jeep.images[ self.d ][ self.imgIx ] )
    wheelOffs = [ [ -43, 40 ], [ -38, 43 ] ]
    for xOff in wheelOffs[ self.d ]:
      self.drawWheel( e.canvas, proj.x + xOff, proj.y + 14, 12, self.p.x )

##############################################################################
class Transport1():
  images = []

  def __init__( self, p, d=DIRECTION_LEFT ):
    self.oType = OBJECT_TYPE_TRANSPORT1
    self.colRect = ( -5, 1, 5, -1 )
    self.time = 0
    self.bounceCount = 0
    self.d = d
    self.p = Point( p.x, p.y, p.z )

    if len( Transport1.images ) == 0:
      img = Image.open( "images/vehicles/transport1.gif" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 128 ) )
        crop = crop.resize( ( 512 / 2, 128 / 2 ) )
        crop = ImageTk.PhotoImage( crop )
        Transport1.images.append( crop )

  def processMessage( self, message, param=None ):
    pass

  # Draw wheels with circles instead of using sprites.
  def drawWheel( self, c, x, y, radius, angle ):
    c.create_oval( x - radius, y - radius, x + radius, y + radius, fill="#111" )  # outer black / rubber
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
    if e.debugCoords:
      return True
    self.time += 1
    if self.time > 500:
      return False

    self.p.x += TRANSPORT1_DELTA if self.d == DIRECTION_RIGHT else -TRANSPORT1_DELTA

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )

    e.canvas.create_image( proj.x, proj.y, image=Transport1.images[ self.d ] )

    wheelOffs = [ [ -65, -25, 25, 60 ], [ -65, -25, 25, 65 ] ]
    for xOff in wheelOffs[ self.d ]:
      self.drawWheel( e.canvas, proj.x + xOff, proj.y + 18, 15, self.p.x )

##############################################################################
class Transport2():
  images = []

  def __init__( self, p, d=DIRECTION_LEFT ):
    self.oType = OBJECT_TYPE_TRANSPORT2
    self.colRect = ( -2, 1, 2, 0 )
    self.time = 0
    self.bounceCount = 0
    self.d = d
    self.p = Point( p.x, p.y, p.z )

    if len( Transport2.images ) == 0:
      img = Image.open( "images/vehicles/transport2.gif" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 256 ) )
        crop = crop.resize( ( 512 / 2, 256 / 2) )
        crop = ImageTk.PhotoImage( crop )
        Transport2.images.append( crop )

  def processMessage( self, message, param=None ):
    pass

  # Draw wheels with circles instead of using sprites.
  def drawWheel( self, c, x, y, radius, angle ):
    # outer black / rubber
    c.create_oval( x - radius, y - radius, x + radius, y + radius, fill="#111" )
    # inner silver
    c.create_oval( x - radius * .65, y - radius * .65, x + radius * .65, y + radius * .65, fill="gray" )
    # inner white
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
    self.time += 1
    if self.time > 500:
      return False

    self.p.x += TRANSPORT2_DELTA if self.d == DIRECTION_RIGHT else -TRANSPORT2_DELTA
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    e.canvas.create_image( proj.x, proj.y, image=Transport2.images[ self.d ] )
    wheelOffs = [ [ -64, -25, 25, 64 ], [ -65, -27, 23, 62 ] ]
    for xOff in wheelOffs[ self.d ]:
      self.drawWheel( e.canvas, proj.x + xOff, proj.y + 25, 15, self.p.x )

##############################################################################
class Truck():
  images = []

  def __init__( self, p, d=DIRECTION_LEFT ):
    self.oType = OBJECT_TYPE_TRUCK
    self.colRect = ( -2, 1, 2, 0 )

    self.time = 0
    self.bounceCount = 0
    self.d = d
    self.p = Point( p.x, p.y, p.z )

    if len( Truck.images ) == 0:
      img = Image.open( "images/vehicles/Truck1.gif" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 256 ) )
        crop = crop.resize( ( 512 / 3, 256 / 3 ) )
        crop = ImageTk.PhotoImage( crop )
        Truck.images.append( crop )

  def processMessage( self, message, param=None ):
    pass

  # Draw wheels with circles instead of using sprites.
  def drawWheel( self, c, x, y, radius, angle ):
    # outer black / rubber
    c.create_oval( x - radius, y - radius, x + radius, y + radius, fill="#111" )
    # inner rim
    c.create_oval( x - radius * .65, y - radius * .65, x + radius * .65, y + radius * .65, fill="gray" )
    # inner white
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
    self.time += 1
    if self.time > 500:
      return False

    self.p.x += TRUCK_DELTA if self.d == DIRECTION_RIGHT else -TRUCK_DELTA
    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )

    e.canvas.create_image( proj.x, proj.y, image=Truck.images[ self.d ] )

    wheelOffs = [ [ -58, 20, 50 ], [ -52, -20, 57 ] ]
    for xOff in wheelOffs[ self.d ]:
      self.drawWheel( e.canvas, proj.x + xOff, proj.y + 17, 12, self.p.x )