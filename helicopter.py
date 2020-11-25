import constants
import math
from utils import *
from PIL import ImageTk, Image
from missiles import *

class Helicopter():
  heloImages = {}

  def __init__( self, x, y, z ):
    self.oType = OBJECT_TYPE_CHOPPER
    self.colRect = (-2, 3, 2, 0)
    self.p = Point( x, y, z )
    self.atBase = False
    self.rotorSpeed = ROTOR_SLOW
    self.fuel = 100.0
    self.rotorTheta = 0.0
    self.loadImages()
    self.vx = 0.0
    self.vy = 0.0
    self.tgtXVelocity = TGT_VEL_STOP
    self.tgtYVelocity = TGT_VEL_STOP
    self.chopperDir = DIRECTION_FORWARD
    self.weapon = WEAPON_NONE # This gets set and then fired in the next update()
                              # Trying to keep msg processing loosely coupled.
    self.health = 100.0
    self.countLargeMissiles = 4
    self.countSmallMissiles = 20
    self.countBomb = 4
    self.countBullet = 250

    self.displayStickCount = 0
    self.gunAngle = 0
    self.gunPosition = 0 # currently just a number from 0-4

    self.structuralIntegrity = 1000

    # Target vx enum -> vx map
    self.tgtXVelDict = \
    {
      TGT_VEL_STOP        :  0.0,
      TGT_VEL_LEFT_STOP   :  0.0,
      TGT_VEL_LEFT_SLOW   :  -.5,
      TGT_VEL_LEFT_FAST   : -1.0,
      TGT_VEL_RIGHT_STOP  :  0.0,
      TGT_VEL_RIGHT_SLOW  :   .5,
      TGT_VEL_RIGHT_FAST  :  1.0
    }

    # Target vy enum -> vy map
    self.tgtYVelDict = \
    {
      TGT_VEL_STOP      : 0.0,
      TGT_VEL_UP_SLOW   :  .3,
      TGT_VEL_UP_FAST   :  .6,
      TGT_VEL_DN_SLOW   : -.3,
      TGT_VEL_DN_FAST   : -.6
    }

    self.gunAngleFromPosition = \
    {
      0 :  10.0 / 360 * 2 * PI,
      1 :   0.0 / 360 * 2 * PI,
      2 : -10.0 / 360 * 2 * PI,
      3 : -20.0 / 360 * 2 * PI,
      4 : -45.0 / 360 * 2 * PI,
    }

    self.angleDict = \
    {
      ANGLE_0   : 0.0,
      ANGLE_U5  : -.087,
      ANGLE_D5  :  .087,
      ANGLE_D10 :  .174
    }
    # weapon images for inventory
    self.missileSImg = ImageTk.PhotoImage( Image.open( "images/chopper/missileB_L.gif" ) )
    self.missileLImg = ImageTk.PhotoImage( Image.open( "images/chopper/missileA_L.gif" ) )
    bombImage = Image.open( "images/chopper/bomb.gif" )
    bombImage = bombImage.resize( ( 10, 30 ) )
    self.bombImg = ImageTk.PhotoImage( bombImage )

  def processMessage( self, e, message, param=None ):
    if message == MSG_ACCEL_L:
      if self.tgtXVelocity > TGT_VEL_LEFT_FAST:
        self.tgtXVelocity -= 1
        self.displayStickCount = DISPLAY_CONTROL_TIME
    elif message == MSG_ACCEL_R:
      if self.tgtXVelocity < TGT_VEL_RIGHT_FAST:
        self.tgtXVelocity += 1
        self.displayStickCount = DISPLAY_CONTROL_TIME
    elif message == MSG_ACCEL_U:
      if self.tgtYVelocity < TGT_VEL_UP_FAST:
        self.tgtYVelocity += 1
        self.displayStickCount = DISPLAY_CONTROL_TIME
    elif message == MSG_ACCEL_D:
      if self.tgtYVelocity > TGT_VEL_DN_FAST:
        self.tgtYVelocity -= 1
        self.displayStickCount = DISPLAY_CONTROL_TIME

    # Don't spawn the weapon here. Let's keep that loosely coupled. Spawn in update().
    elif message == MSG_WEAPON_MISSILE_S:
      if self.chopperDir != DIRECTION_FORWARD:
        if self.countSmallMissiles > 0:
          self.weapon = WEAPON_SMALL_MISSILE
          self.countSmallMissiles -= 1
    elif message == MSG_WEAPON_MISSILE_L:
      if self.chopperDir != DIRECTION_FORWARD:
        if self.countLargeMissiles > 0:
          self.countLargeMissiles -= 1
          self.weapon = WEAPON_LARGE_MISSILE
    elif message == MSG_WEAPON_BOMB:
      if self.countBomb > 0:
        self.countBomb -= 1
        self.weapon = WEAPON_BOMB
    elif message == MSG_WEAPON_BULLET:
      if self.countBullet > 0:
        self.countBullet -= 1
        self.weapon = WEAPON_BULLET
    elif message == MSG_GUN_UP:
      if self.gunPosition > 0:
        self.gunPosition -= 1
        self.gunAngle = self.gunAngleFromPosition[ self.gunPosition ]
    elif message == MSG_GUN_DOWN:
      if self.gunPosition < 4:
        self.gunPosition += 1
        self.gunAngle = self.gunAngleFromPosition[ self.gunPosition ]
    elif message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.structuralIntegrity -= param.wDamage

  def loadImages( self ):
    imageNames = ( "bodyForward",
                   "bodyLeft",  "bodyLeftD5",  "bodyLeftD10",  "bodyLeftU5",
                   "bodyRight", "bodyRightD5", "bodyRightD10", "bodyRightU5" )

    if len( Helicopter.heloImages ) == 0:
      for name in imageNames:
        Helicopter.heloImages[ name ] = ImageTk.PhotoImage( Image.open( "images/chopper/" + name + ".gif" ) )

  def update( self, e ):

    if self.structuralIntegrity < 0:
      e.addStatusMessage( "Destroyed!" )
      return False

    # Handle fuel consumption
    if self.p.y > 0.0:
      self.fuel -= .01
      if self.vx != 0:
        self.fuel -= math.fabs( self.vx ) * .01
    if self.fuel <= 0.0:
      if self.p.y > 0.0:
        self.vy -= .05
        self.vx *= .95
      else:
        self.fuel = 0
        self.rotorTheta = 0

    if self.fuel > 0.0:
      # Spin the rotors
      self.rotorTheta -= self.rotorSpeed / 4.0
      if self.rotorTheta < 0:
        self.rotorTheta += 2 * PI

      # Accelerate to target velocities if we have fuel
      tv = self.tgtXVelDict[ self.tgtXVelocity ]
      if self.vx < tv:
        self.vx += CHOPPER_V_DELTA
      elif self.vx > tv:
        self.vx -= CHOPPER_V_DELTA
      if math.fabs( self.vx - tv ) < .01: # In case of rounding
        self.vx = tv

      tv = self.tgtYVelDict[ self.tgtYVelocity ]
      if self.vy < tv:
        self.vy += CHOPPER_V_DELTA
      elif self.vy > tv:
        self.vy -= CHOPPER_V_DELTA
      if math.fabs( self.vy - tv ) < .01: # In case of rounding
        self.vy = tv

    self.p.y += self.vy
    self.p.x += self.vx

    # Stay in the playing field.
    if self.p.x < MIN_WORLD_X:
      if self.tgtXVelocity < TGT_VEL_RIGHT_SLOW:
        e.addStatusMessage( "Stay On Mission", 50 )
        e.addStatusMessage( "Head East ->", 50 )
      self.tgtXVelocity = TGT_VEL_RIGHT_SLOW
    elif self.p.x > MAX_WORLD_X:
      self.tgtXVelocity = TGT_VEL_LEFT_SLOW

    if self.p.y > MAX_ALTITUDE:
      self.vy -= .1
      self.tgtYVelocity = TGT_VEL_STOP
    elif self.p.y <= 0: # On the ground.
      self.p.y = 0
      self.vy = 0
      self.vx = 0
      self.tgtXVelocity = TGT_VEL_STOP
      self.tgtYVelocity = TGT_VEL_STOP

      if not self.atBase:
        for obj in e.bg_objects:
          # See if we're near a base
          if obj.oType == OBJECT_TYPE_BASE:
            if math.fabs( self.p.x - obj.p.x ) < 10.0: # At a base, refill
              self.fuel = 100.0
              self.countLargeMissiles = 4
              self.countSmallMissiles = 20
              self.countBomb = 4
              self.countBullet = 250
              self.atBase = True
              e.addStatusMessage( "Refueled", time=50 )
              break
    else: # Off the ground
      self.atBase = False

    if self.vy > 0:
      self.rotorSpeed = ROTOR_FAST
    elif self.p.y > 0:
      self.rotorSpeed = ROTOR_SLOW

    # Weapon spawning
    if self.weapon != WEAPON_NONE:
      if self.weapon == WEAPON_BULLET:
        if self.chopperDir == DIRECTION_RIGHT:
          e.addObject( Bullet( Point( self.p.x + 1, self.p.y + 1, self.p.z ),
                               math.fabs( self.vx ) + 2.5, self.gunAngle ) )
        elif self.chopperDir == DIRECTION_LEFT:
          e.addObject( Bullet( Point( self.p.x - 1, self.p.y + 1, self.p.z ),
                               math.fabs( self.vx ) + 2.5, PI - self.gunAngle ) )
      elif self.weapon == WEAPON_SMALL_MISSILE:
        e.addObject( MissileSmall( self.p, self.vx, self.vy, self.chopperDir ) )
      elif self.weapon == WEAPON_LARGE_MISSILE:
        e.addObject( MissileLarge( self.p, self.vx, self.vy, self.chopperDir ) )
      elif self.weapon == WEAPON_BOMB:
        e.addObject( Bomb( self.p, self.vx, self.vy ) )
      self.weapon = WEAPON_NONE

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    # Determine sprite and the corresponding rotor positions
    bodyAngle = ANGLE_0
    self.chopperDir = DIRECTION_FORWARD
    targetVelocity = self.tgtXVelDict[ self.tgtXVelocity ]

    if self.p.y != 0: # We're not on the ground
      if targetVelocity > 0.0: # Want to go right (+x dir)
        self.chopperDir = DIRECTION_RIGHT
        if self.vx < 0.0: # but still going left, angle left but 'up' to slow down before turning.
          self.chopperDir = DIRECTION_LEFT
          bodyAngle = ANGLE_U5
        elif self.vx < targetVelocity:
          bodyAngle = ANGLE_D10
        elif self.vx > 0:
          bodyAngle = ANGLE_D5
      elif targetVelocity < 0.0:
        self.chopperDir = DIRECTION_LEFT
        if self.vx > 0: # but still going right, go 'up' to slow down before turning.
          bodyAngle = ANGLE_U5
          self.chopperDir = DIRECTION_RIGHT
        elif self.vx > targetVelocity:
          bodyAngle = ANGLE_D10
        elif self.vx < 0:
          bodyAngle = ANGLE_D5
      else: # targetVelocity == 0
        if self.vx != 0:
          self.chopperDir = DIRECTION_LEFT if self.vx < 0 else DIRECTION_RIGHT
          bodyAngle = ANGLE_0
        else:
          if self.tgtXVelocity == TGT_VEL_LEFT_STOP:
            self.chopperDir = DIRECTION_LEFT
          elif self.tgtXVelocity == TGT_VEL_RIGHT_STOP:
            self.chopperDir = DIRECTION_RIGHT
          else:
            self.chopperDir = DIRECTION_FORWARD
    # body
    chopperAngle = self.angleDict[ bodyAngle ]

    # Translate x,y to be below the rotor
    proj.y -= 30
    if self.chopperDir == DIRECTION_LEFT:
      proj.x += 30
      chopperAngle = -chopperAngle
      tRotorX = proj.x + 65
      rotorOffx = -35
    elif self.chopperDir == DIRECTION_RIGHT:
      proj.x -= 24
      tRotorX = proj.x - 65
      rotorOffx = 20
    else:
      rotorOffx = 0

    if bodyAngle == ANGLE_0:
      tRotorY = proj.y - 17
    elif bodyAngle == ANGLE_U5:
      tRotorY = proj.y - 10
    elif bodyAngle == ANGLE_D5:
      tRotorY = proj.y - 23
    elif bodyAngle == ANGLE_D10:
      tRotorY = proj.y - 28

    imageKey = "body" # determine key for image.
    if self.chopperDir == DIRECTION_FORWARD:
      imageKey += "Forward"
    elif self.chopperDir == DIRECTION_LEFT:
      imageKey += "Left"
    else:
      imageKey += "Right"

    if bodyAngle == ANGLE_U5:
      imageKey += "U5"
    elif bodyAngle == ANGLE_D5:
      imageKey += "D5"
    elif bodyAngle == ANGLE_D10:
      imageKey += "D10"

    img = Helicopter.heloImages[ imageKey ]

    e.canvas.create_image( proj.x, proj.y, image=img ) # puts 0,0 where the body hits the rotor
    # Rotor
    ROTOR_LEN = 70
    rotorLen = ROTOR_LEN * math.cos( self.rotorTheta )
    e.canvas.create_line( ( proj.x + rotorOffx ) + rotorLen * math.cos( chopperAngle ),
                          ( proj.y - 12 )        + rotorLen * math.sin( chopperAngle ),
                          ( proj.x + rotorOffx ) + rotorLen * math.cos( chopperAngle + PI ),
                          ( proj.y - 12 )        + rotorLen * math.sin( chopperAngle + PI ) )
    # Tail rotor
    if self.chopperDir != DIRECTION_FORWARD:
      TAIL_ROTOR_LEN = 20
      tmpTheta = self.rotorTheta
      if self.chopperDir == DIRECTION_RIGHT:
        tmpTheta = -tmpTheta
      e.canvas.create_line( tRotorX + TAIL_ROTOR_LEN * math.cos( tmpTheta ),
                            tRotorY + TAIL_ROTOR_LEN * math.sin( tmpTheta ),
                            tRotorX + TAIL_ROTOR_LEN * math.cos( tmpTheta + PI ),
                            tRotorY + TAIL_ROTOR_LEN * math.sin( tmpTheta + PI ) )

    # Shadow
    e.canvas.create_rectangle( proj.x - 60, projShadow.y, proj.x + 60, projShadow.y, outline="black" )

    # Statuses
    if self.displayStickCount:
      self.displayStickCount -= 1
      # Throttle direction indicators
      tgtVelDispDict = \
      { # Dictionary of throttle indicator lengths
        TGT_VEL_STOP        :  0,
        TGT_VEL_LEFT_STOP   : -1,
        TGT_VEL_LEFT_SLOW   : -2,
        TGT_VEL_LEFT_FAST   : -3,
        TGT_VEL_RIGHT_STOP  :  1,
        TGT_VEL_RIGHT_SLOW  :  2,
        TGT_VEL_RIGHT_FAST  :  3
      }
      dispX = proj.x
      dispY = proj.y - 50 # display floating above the chopper
      e.canvas.create_rectangle( dispX - 2, dispY + 20, dispX + 2, dispY + 25, fill="black" ) # a red block in the center
      xLen = tgtVelDispDict[ self.tgtXVelocity ]
      if xLen:
        if xLen > 0:
          for xPos in range( 0, xLen ):
            e.canvas.create_rectangle( dispX + 3 + 5 * xPos, dispY + 20,
                                       dispX + 8 + 5 * xPos, dispY + 25,
                                       fill="red" )
        else:
          for xPos in range( xLen, 0 ):
            e.canvas.create_rectangle( dispX + 3 * xPos,     dispY + 20,
                                       dispX - 3 + 5 * xPos, dispY + 25,
                                       fill="red" )

      tgtVelyDispDict = \
      { # Dictionary of throttle indicator lengths
        TGT_VEL_STOP    :  0,
        TGT_VEL_UP_SLOW :  1,
        TGT_VEL_UP_FAST :  2,
        TGT_VEL_DN_SLOW : -1,
        TGT_VEL_DN_FAST : -2
      }

      yLen = tgtVelyDispDict[ self.tgtYVelocity ]
      if yLen:
        if yLen > 0:
          for yPos in range( 0, yLen ):
            e.canvas.create_rectangle( dispX - 2, dispY +  15 - 5 * yPos,
                                       dispX + 2, dispY +  20 - 5 * yPos,
                                       fill="red" )
        else:
          for yPos in range( yLen, 0 ):
            e.canvas.create_rectangle( dispX - 2, dispY +  20 - 5 * yPos,
                                       dispX + 2, dispY +  25 - 5 * yPos,
                                       fill="red" )

    # Draw gun
    if self.chopperDir == DIRECTION_RIGHT:
      gx = proj.x + 50
      gy = proj.y + 15
      e.canvas.create_line( gx, gy,
                            gx + 10.0 * math.cos( self.gunAngle ),
                            gy - 10.0 * math.sin( self.gunAngle ),
                            fill="gray",
                            width=3 )
    elif self.chopperDir == DIRECTION_LEFT:
      gx = proj.x - 60
      gy = proj.y + 15
      e.canvas.create_line( gx, gy,
                            gx - 10.0 * math.cos( -self.gunAngle ),
                            gy + 10.0 * math.sin( -self.gunAngle ),
                            fill="gray",
                            width=3 )

    # Fuel level
    e.canvas.create_rectangle( 10, 10, 10 + 100.0 * 2, 15, fill="red" )
    e.canvas.create_rectangle( 10, 10, 10 + self.fuel * 2, 15, fill="green" )

    # Number of weapons
    for i in range( 0, self.countSmallMissiles ):
      e.canvas.create_image( 10, 50 + 6 * i, image=self.missileSImg )
    for i in range( 0, self.countLargeMissiles ):
      e.canvas.create_image( 70, 50 + 6 * i, image=self.missileLImg )
    for i in range( 0, self.countBomb ):
      e.canvas.create_image( 10 + 10 * i, 35, image=self.bombImg )
    t = "Rounds %s" % self.countBullet
    e.canvas.create_text( 100, 30, text=t )

