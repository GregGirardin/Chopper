import constants
import math, random
from utils import *
from explosions import *
from tkinter import *
from PIL import ImageTk, Image
from copy import copy

# If vehicles make it to a city building they do damage to the building at turn around

# Jeeps and trucks
class Jeep():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_JEEP
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -3, 3, 3, 0 )
    self.imgIx = 0
    self.bounceCount = 0
    self.v = v if v else Vector( PI, JEEP_DELTA )
    self.si = self.siMax = SI_JEEP
    self.points = POINTS_JEEP
    self.showSICount = 0
    # For vehicles wDamage is the damage we do to a building when we contact it
    # it then turns around.
    self.wDamage = WEAPON_DAMAGE_JEEP

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
        self.showSICount = SHOW_SI_COUNT
        self.si -= param.wDamage
        if self.si < 0:
          e.addObject( BombExplosion( self.p ) )
      if param.oType == OBJECT_TYPE_BUILDING:
        # building records the damage we do to it.. turn around.
        self.v = Vector( 0, JEEP_DELTA )

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
    if self.si < 0:
      e.qMessage( MSG_ENEMY_LEFT_BATTLEFIELD, self )
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

    if self.p.x < MIN_WORLD_X:  # Should not happen with current rules. Game ends when city destroyed.
      self.v = Vector( 0, JEEP_DELTA )
    elif self.p.x > MAX_WORLD_X / 2:
      self.v = Vector( PI, JEEP_DELTA )

    self.p.move( self.v )

    return True

  def draw( self, e, p_ ):
    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT
    p = copy( p_ )
    p.y -= 20
    e.canvas.create_image( p.x, p.y, image=Jeep.images[ d ][ self.imgIx ] )
    wheelOffs = [ [ -43, 40 ], [ -38, 43 ] ]
    for xOff in wheelOffs[ d ]:
      # using our self.p.x as angle in drawWheel() keeps wheel spinning as though it's on the ground.
      self.drawWheel( e.canvas, p.x + xOff, p.y + 14, 12, self.p.x )

    showSI( e.canvas, p, self )

##############################################################################
class Transport1():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_TRANSPORT1
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -5, 3, 5, 0 )
    self.bounceCount = 0
    self.v = v if v else Vector( PI, TRANSPORT1_DELTA )
    self.si = self.siMax = SI_TRANSPORT1

    self.points = POINTS_TRANSPORT
    self.showSICount = 0
    self.wDamage = WEAPON_DAMAGE_T1

    if len( Transport1.images ) == 0:
      img = Image.open( "images/vehicles/transport1.gif" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 128 ) )
        crop = crop.resize( ( 256, 64 ) )
        crop = ImageTk.PhotoImage( crop )
        Transport1.images.append( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.showSICount = SHOW_SI_COUNT
        self.si -= param.wDamage
        if self.si < 0:
          e.addObject( BombExplosion( self.p ) )
      if param.oType == OBJECT_TYPE_BUILDING:
        # building records the damage we do to it.. turn around.
        self.v = Vector( 0, JEEP_DELTA )

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
    if self.si < 0:
      e.qMessage( MSG_ENEMY_LEFT_BATTLEFIELD, self )
      return False

    if self.p.x < MIN_WORLD_X:  # Should not happen with current rules. Game ends when city destroyed.
      self.v = Vector( 0, TRANSPORT1_DELTA )
    elif self.p.x > MAX_WORLD_X / 2:
      self.v = Vector( PI, TRANSPORT1_DELTA )

    self.p.move( self.v )
    return True

  def draw( self, e, p_ ):
    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT
    p = copy( p_ )
    p.y -= 30
    e.canvas.create_image( p.x, p.y, image=Transport1.images[ d ] )

    wheelOffs = [ [ -65, -25, 25, 60 ], [ -65, -25, 25, 65 ] ]
    for xOff in wheelOffs[ d ]:
      self.drawWheel( e.canvas, p.x + xOff, p.y + 18, 15, self.p.x )

    showSI( e.canvas, p, self )

##############################################################################
class Transport2():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_TRANSPORT2
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -5, 3, 5, 0 )
    self.bounceCount = 0
    self.v = v if v else Vector( PI, TRANSPORT2_DELTA )
    self.si = self.siMax = SI_TRANSPORT2
    self.points = POINTS_TRANSPORT
    self.showSICount = 0
    self.wDamage = WEAPON_DAMAGE_T2

    if len( Transport2.images ) == 0:
      img = Image.open( "images/vehicles/transport2.gif" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 256 ) )
        crop = crop.resize( ( 256, 128 ) )
        crop = ImageTk.PhotoImage( crop )
        Transport2.images.append( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.showSICount = SHOW_SI_COUNT
        self.si -= param.wDamage
        if self.si < 0:
          e.addObject( BombExplosion( self.p ) )
      if param.oType == OBJECT_TYPE_BUILDING:
        # building records the damage we do to it.. turn around.
        self.v = Vector( 0, JEEP_DELTA )

  def drawWheel( self, c, x, y, radius, angle ):
    c.create_oval( x - radius, y - radius, x + radius, y + radius, fill="#111" )
    c.create_oval( x - radius * .65, y - radius * .65,
                   x + radius * .65, y + radius * .65, fill="gray" )
    c.create_oval( x - radius * .33, y - radius * .33,
                   x + radius * .33, y + radius * .33, fill="white" )

    # Draw lug nuts to indicate rotation
    theta = 0
    radius *= .5
    while theta < 2 * PI:
      lnx = x + radius * math.cos( theta - angle )
      lny = y - radius * math.sin( theta - angle )
      c.create_oval( lnx - 2, lny - 2, lnx + 2, lny + 2, fill="#fff" )
      theta += ( 2 * PI ) / 5

  def update( self, e ):
    if self.si < 0:
      e.qMessage( MSG_ENEMY_LEFT_BATTLEFIELD, self )
      return False

    if self.p.x < MIN_WORLD_X: # Should not happen with current rules. Game ends when city destroyed.
      self.v = Vector( 0, TRANSPORT2_DELTA )
    elif self.p.x > MAX_WORLD_X / 2:
      self.v = Vector( PI, TRANSPORT2_DELTA )
    self.p.move( self.v )

    return True

  def draw( self, e, p_ ):
    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT
    p = copy( p_ )
    p.y -= 35
    e.canvas.create_image( p.x, p.y, image=Transport2.images[ d ] )
    wheelOffs = [ [ -64, -25, 25, 64 ], [ -65, -27, 23, 62 ] ]
    for xOff in wheelOffs[ d ]:
      self.drawWheel( e.canvas, p.x + xOff, p.y + 25, 15, self.p.x)

    showSI( e.canvas, p, self )

##############################################################################
class Truck():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_TRUCK
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -3, 2.5, 3, 0 )
    self.bounceCount = 0
    self.v = v if v else Vector( PI, TRUCK_DELTA )
    self.si = self.siMax = SI_TRUCK
    self.points = POINTS_TRUCK
    self.showSICount = 0
    self.wDamage = WEAPON_DAMAGE_TRUCK

    if len( Truck.images ) == 0:
      img = Image.open( "images/vehicles/Truck1.gif" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 256 ) )
        crop = crop.resize( ( 171, 85 ) )
        crop = ImageTk.PhotoImage( crop )
        Truck.images.append( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.showSICount = SHOW_SI_COUNT
        self.si -= param.wDamage
        if self.si < 0:
          e.addObject( BombExplosion( self.p ) )
      if param.oType == OBJECT_TYPE_BUILDING:
        # building records the damage we do to it.. turn around.
        self.v = Vector( 0, JEEP_DELTA )

  # Draw wheels with circles instead of using sprites.
  def drawWheel( self, c, x, y, radius, angle ):
    c.create_oval( x - radius, y - radius, x + radius, y + radius, fill="#111" )
    c.create_oval( x - radius * .65, y - radius * .65,
                   x + radius * .65, y + radius * .65, fill="gray" )
    c.create_oval( x - radius * .33, y - radius * .33,
                   x + radius * .33, y + radius * .33, fill="white" )

    # Draw lug nuts to indicate rotation
    theta = 0
    radius *= .5
    while theta < 2 * PI:
      lnx = x + radius * math.cos( theta - angle )
      lny = y - radius * math.sin( theta - angle )
      c.create_oval( lnx - 2, lny - 2, lnx + 2, lny + 2, fill="#fff" )
      theta += ( 2 * PI ) / 2

  def update( self, e ):
    if self.si < 0:
      e.qMessage( MSG_ENEMY_LEFT_BATTLEFIELD, self )
      return False

    if self.p.x < MIN_WORLD_X:  # Should not happen with current rules. Game ends when city destroyed.
      self.v = Vector( 0, TRUCK_DELTA )
    elif self.p.x > MAX_WORLD_X / 2:
      self.v = Vector( PI, TRUCK_DELTA )

    self.p.move( self.v )

    return True

  def draw( self, e, p_ ):
    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT
    p = copy( p_ )
    p.y -= 20
    e.canvas.create_image( p.x, p.y, image=Truck.images[ d ] )
    wheelOffs = [ [ -58, 20, 50 ], [ -52, -20, 57 ] ]
    for xOff in wheelOffs[ d ]:
      self.drawWheel( e.canvas, p.x + xOff, p.y + 17, 12, self.p.x )

    showSI( e.canvas, p, self )