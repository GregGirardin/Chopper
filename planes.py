import constants
import math, random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image
from explosions import *
from missiles import *

##############################################################################
class Bomber1():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_JET
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -6, 2, 6, 0 )
    self.v = copy( v ) if v else Vector( PI, BOMBER1_DELTA )
    self.si = self.siMax = SI_BOMBER1
    self.points = POINTS_BOMBER
    self.bombs = 2
    self.target_y = p.y
    self.showSICount = 0
    self.wDamage = 0

    if len( Bomber1.images ) == 0:
      img = Image.open( "images/vehicles/Bomber1.png" )
      SW = 512
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, 133 ) )
        crop = crop.resize( ( int( SW / 1.5 ), int( 133 / 1.5 ) ) )
        crop = ImageTk.PhotoImage( crop )
        Bomber1.images.append( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.showSICount = SHOW_SI_COUNT
        self.si -= param.wDamage
        if self.si < 0:
          e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.si < 0.0:
      e.qMessage( MSG_ENEMY_LEFT_BATTLEFIELD, self )
      return False

    if math.fabs( self.p.y - self.target_y ) > .2:
      if self.p.y < self.target_y:
        self.p.y += .1
      elif self.p.y > self.target_y:
        self.p.y -= .1

    if self.p.x < MIN_WORLD_X - 50:
      self.target_y = random.randint( 50, 100 )
      self.v = Vector( 0, BOMBER1_DELTA )
    elif self.p.x > MAX_WORLD_X + 50:
      if e.cityDestroyed:
        e.addStatusMessage( "Bomber Left Theater" )
        e.qMessage( MSG_ENEMY_LEFT_BATTLEFIELD, self )
        return False
      self.target_y = random.randint( 15, 25 )
      self.v = Vector( PI, BOMBER1_DELTA )
      self.bombs = 1

    if not e.time % 10: # don't need to do this every cycle.
      if self.bombs:  # See if there's a target
        for o in e.objects:
          if o.oType == OBJECT_TYPE_BUILDING:
            if( math.fabs( o.p.x - self.p.x ) < 10 ):
              e.addObject( Bomb( self.p, self.v, oType=OBJECT_TYPE_E_WEAPON ) )
              self.bombs -= 1
              break

    self.p.move( self.v )

    return True

  def draw( self, e, p ):
    ps = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT
    e.canvas.create_image( p.x, p.y - 20, image=Bomber1.images[ d ] )
    e.canvas.create_rectangle( p.x - 60, ps.y, p.x + 60, ps.y, outline="black" )
    showSI( e.canvas, p, self )

##############################################################################
class Bomber2():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_JET
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -4, 2, 4, 0 )
    self.v = v if v else Vector( PI, BOMBER2_DELTA )
    self.si = SI_BOMBER2
    self.siMax = SI_BOMBER2
    self.points = POINTS_BOMBER
    self.showSICount = 0
    self.target_y = p.y
    self.bombs = 1
    self.wDamage = 0

    if len( Bomber2.images ) == 0:
      img = Image.open( "images/vehicles/Bomber2.gif" )
      SW = 256
      for y in range( 0, 2 ):
        crop = img.crop( ( 0, y * SW, 640, y * SW + SW ) )
        crop = crop.resize( ( 640 / 3, 256 / 3 ) )
        crop = ImageTk.PhotoImage( crop )
        Bomber2.images.append( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.showSICount = SHOW_SI_COUNT
        self.si -= param.wDamage
        if self.si < 0:
          e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.si < 0.0:
      e.qMessage( MSG_ENEMY_LEFT_BATTLEFIELD, self )
      return False

    if math.fabs( self.p.y - self.target_y ) > .2:
      if self.p.y < self.target_y:
        self.p.y += .1
      elif self.p.y > self.target_y:
        self.p.y -= .1

    if self.p.x < MIN_WORLD_X - 50:
      self.target_y = random.randint( 50, 75 )
      self.v = Vector( 0, BOMBER2_DELTA )
    elif self.p.x > MAX_WORLD_X + 50:
      if e.cityDestroyed:
        e.addStatusMessage( "Bomber Left Theater" )
        e.qMessage( MSG_ENEMY_LEFT_BATTLEFIELD, self )
        return False
      self.target_y = random.randint( 10, 25 )
      self.v = Vector( PI, BOMBER2_DELTA )
      self.bombs = 1

    if not e.time % 10: # don't need to do this every cycle.
      if self.bombs:  # See if there's a target
        for o in e.objects:
          if o.oType == OBJECT_TYPE_BUILDING:
            if( math.fabs( o.p.x - self.p.x ) < 10 ):
              e.addObject( Bomb( self.p, self.v, oType=OBJECT_TYPE_E_WEAPON ) )
              self.bombs -= 1
              break

    self.p.move( self.v )

    return True

  def draw( self, e, p ):
    ps = projection( e.camera, Point( self.p.x, 0, self.p.z ) ) # Shadow
    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT

    e.canvas.create_image( p.x, p.y - 40, image=Bomber2.images[ d ] )
    e.canvas.create_rectangle( p.x - 60, ps.y, p.x + 60, ps.y, outline="black" )

    showSI( e.canvas, p, self )

##############################################################################
class Fighter():
  images = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_JET
    self.p = Point( p.x, p.y, p.z )
    self.colRect = ( -2, 2, 2, .5 )
    self.v = v if v else vecFromComps( -FIGHTER_DELTA, 0 )
    self.nextMissile = 200
    self.si = self.siMax = SI_FIGHTER
    self.points = POINTS_FIGHTER
    self.target_y = p.y
    self.showSICount = 0
    self.angleUp = False # we have a sprite angled for this object.
    self.wDamage = 0


    if len( Fighter.images ) == 0:
      img = Image.open( "images/vehicles/Fighter.gif" )
      SW = 512
      for y in range( 0, 2 ):
        for x in range( 0, 2 ):
          crop = img.crop( ( x * SW, y * 128, x * SW + SW, y * 128 + 128 ) )
          crop = crop.resize( ( SW / 3, 128 / 3 ) )
          crop = ImageTk.PhotoImage( crop )
          Fighter.images.append( crop )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.showSICount = SHOW_SI_COUNT
        self.si -= param.wDamage
        if self.si < 0:
          e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.si < 0.0:
      e.qMessage( MSG_ENEMY_LEFT_BATTLEFIELD, self )
      return False

    if( ( ( self.p.x - e.chopper.p.x ) >  100 and self.v.dx() > 0 ) or
        ( ( self.p.x - e.chopper.p.x ) < -100 and self.v.dx() < 0 ) ):
      self.v.flipx() # change direction when we get too far
      self.p.y = e.chopper.p.y + random.randint( 0, 5 ) + 1 # and get closer to the helo's y
      if self.p.y < 1:
        self.p.y = 1
    if self.nextMissile > 0:
      self.nextMissile -= 1
    elif self.p.y >= self.target_y: # time to shoot a missile. Don't shoot while ascending.
      if( ( self.v.dx() > 0 and e.chopper.p.x > self.p.x ) or
          ( self.v.dx() < 0 and e.chopper.p.x < self.p.x ) ): # nly shoot if we're going towards the chopper
        d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT
        e.addObject( MissileSmall( self.p, self.v, d, oType=OBJECT_TYPE_E_WEAPON ) )
        self.nextMissile = 50 + random.randint( 0, 100 )

    if( ( ( self.v.dx() > 0 and e.chopper.p.x > self.p.x ) or
          ( self.v.dx() < 0 and e.chopper.p.x < self.p.x ) )
        and random.randint( 0, 10 ) == 0 ): # If jet is behind sometimes try to level with chopper
      self.target_y = e.chopper.p.y + 2

    self.angleUp = False

    if math.fabs( self.p.y - self.target_y ) > .2:
      if self.p.y < self.target_y:
        self.p.y += .15
        self.angleUp = True
      elif self.p.y > self.target_y:
        self.p.y -= .15

    self.p.move( self.v )

    return True

  def draw( self, e, p ):
    ps = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT
    if self.angleUp:
      d += 2 # Sprites are L,R, up L, up R
    e.canvas.create_image( p.x, p.y - 25, image=Fighter.images[ d ] )
    e.canvas.create_rectangle( p.x - 60, ps.y, p.x + 60, ps.y, outline="black" )

    showSI( e.canvas, p, self )