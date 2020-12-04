import constants
import math
from utils import *
from PIL import ImageTk, Image
from missiles import *

class Helicopter():
  heloImages = {}

  def __init__( self, x, y, z ):
    self.oType = OBJECT_TYPE_CHOPPER
    self.colRect = ( -2, 3, 2, 0 )
    self.p = Point( x, y, z )
    self.onGround = False
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
    self.si = SI_CHOPPER
    self.countLargeMissiles = MAX_L_MISSILES
    self.countSmallMissiles = MAX_S_MISSILES
    self.countBomb = MAX_BOMBS
    self.countBullet = MAX_BULLETS
    self.bulletRdyCounter = 0

    self.displayStickCount = 0
    self.gunAngle = 0
    self.gunPosition = 0 # currently just a number from 0-4

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
      if self.tgtXVelocity > TGT_VEL_LEFT_FAST and self.p.y > 0 and self.p.x > MIN_WORLD_X:
        self.tgtXVelocity -= 1
        self.displayStickCount = DISPLAY_CONTROL_TIME
    elif message == MSG_ACCEL_R:
      if self.tgtXVelocity < TGT_VEL_RIGHT_FAST and self.p.y > 0:
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
      if self.countBullet > 0 and self.bulletRdyCounter == 0:
        self.countBullet -= 1
        self.weapon = WEAPON_BULLET
        self.bulletRdyCounter = 5
    elif message == MSG_GUN_UP:
      if self.gunPosition > 0:
        self.gunPosition -= 1
        self.gunAngle = self.gunAngleFromPosition[ self.gunPosition ]
    elif message == MSG_GUN_DOWN:
      if self.gunPosition < 4:
        self.gunPosition += 1
        self.gunAngle = self.gunAngleFromPosition[ self.gunPosition ]
    elif message == MSG_COLLISION_DET and e.cameraOnHelo:
      # Note that we ignore collisions after we spawn a helo but before the camera
      # has moved to the helo, otherwise we could get destroyed again before we see the helo
      if param.oType == OBJECT_TYPE_E_WEAPON:
        self.si -= param.wDamage

  def loadImages( self ):
    imageNames = ( "bodyForward",
                   "bodyLeft",  "bodyLeftD5",  "bodyLeftD10",  "bodyLeftU5",
                   "bodyRight", "bodyRightD5", "bodyRightD10", "bodyRightU5" )

    if len( Helicopter.heloImages ) == 0:
      for name in imageNames:
        Helicopter.heloImages[ name ] = ImageTk.PhotoImage( Image.open( "images/chopper/" + name + ".gif" ) )

  ######################
  def update( self, e ):
    if self.si < 0:
      e.qMessage( MSG_CHOPPER_DESTROYED, self )
      return False

    if self.bulletRdyCounter > 0:
      self.bulletRdyCounter -= 1

    # Fuel consumption
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

      # Accelerate to target velocities
      tv = self.tgtXVelDict[ self.tgtXVelocity ]
      if self.vx < tv:
        self.vx += CHOPPER_X_DELTA
      elif self.vx > tv:
        self.vx -= CHOPPER_X_DELTA
      if math.fabs( self.vx - tv ) < CHOPPER_X_DELTA: # In case of rounding
        self.vx = tv

      tv = self.tgtYVelDict[ self.tgtYVelocity ]
      if tv == TGT_VEL_STOP:
        self.vy *= .5
      elif self.vy < tv:
        self.vy += CHOPPER_Y_DELTA
      elif self.vy > tv:
        self.vy -= CHOPPER_Y_DELTA
      if math.fabs( self.vy - tv ) <= CHOPPER_Y_DELTA: # In case of rounding
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
      if self.tgtYVelocity < TGT_VEL_STOP:
        self.tgtYVelocity = TGT_VEL_STOP
      if self.tgtXVelocity > TGT_VEL_STOP:
        self.tgtXVelocity = TGT_VEL_RIGHT_STOP
      elif self.tgtXVelocity < TGT_VEL_STOP:
        self.tgtXVelocity = TGT_VEL_LEFT_STOP
      self.vx = 0
      self.vy = 0

      if not self.onGround:
        for obj in e.bg_objects:
          # See if we're near a base
          if obj.oType == OBJECT_TYPE_BASE:
            if math.fabs( self.p.x - obj.p.x ) < 10.0:
              self.onGround = True
              if e.missionComplete:
                e.qMessage( MSG_MISSION_COMPLETE )
              if obj.readyToRefuel:
                obj.processMessage( e, MSG_REFUELING_AT_BASE )
                self.fuel = 100.0
                self.countLargeMissiles = MAX_L_MISSILES
                self.countSmallMissiles = MAX_S_MISSILES
                self.countBomb = MAX_BOMBS
                self.countBullet = MAX_BULLETS
                if self.si < SI_CHOPPER * .66:
                  self.si += SI_CHOPPER / 3
                  e.addStatusMessage( "Refueled", time=50 )
              else:
                e.addStatusMessage( "Base Not Ready" )

    else: # Off the ground
      self.onGround = False

    if self.vy > 0:
      self.rotorSpeed = ROTOR_FAST
    else:
      self.rotorSpeed = ROTOR_SLOW

    # Weapon spawning
    if self.weapon != WEAPON_NONE:
      v = vecFromComps( self.vx, self.vy )
      if self.weapon == WEAPON_BULLET:
        if self.chopperDir == DIRECTION_RIGHT:
          e.addObject( Bullet( Point( self.p.x + 1, self.p.y + 1, self.p.z ),
                               Vector( self.gunAngle, math.fabs( self.vx ) + BULLET_DELTA ) ) )
        elif self.chopperDir == DIRECTION_LEFT:
          e.addObject( Bullet( Point( self.p.x - 1, self.p.y + 1, self.p.z ),
                               Vector( ( PI - self.gunAngle ), math.fabs( self.vx ) + BULLET_DELTA ) ) )
      elif self.weapon == WEAPON_SMALL_MISSILE:
        e.addObject( MissileSmall( self.p, v, self.chopperDir ) )
      elif self.weapon == WEAPON_LARGE_MISSILE:
        e.addObject( MissileLarge( self.p, v, self.chopperDir ) )
      elif self.weapon == WEAPON_BOMB:
        e.addObject( Bomb( self.p, v ) )
      self.weapon = WEAPON_NONE

    return True

  def draw( self, e, p ):
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    # Determine sprite and the corresponding rotor positions
    bodyAngle = ANGLE_0
    #self.chopperDir = DIRECTION_FORWARD
    targVel = self.tgtXVelDict[ self.tgtXVelocity ]

    if self.p.y != 0: # We're not on the ground
      if targVel > 0.0: # Want to go right (+x dir)
        self.chopperDir = DIRECTION_RIGHT
        if self.vx < 0.0: # but still going left, angle left but 'up' to slow down before turning.
          self.chopperDir = DIRECTION_LEFT
          bodyAngle = ANGLE_U5
        elif self.vx < targVel:
          bodyAngle = ANGLE_D10
        elif self.vx > 0:
          bodyAngle = ANGLE_D5
      elif targVel < 0.0:
        self.chopperDir = DIRECTION_LEFT
        if self.vx > 0: # but still going right, go 'up' to slow down before turning.
          bodyAngle = ANGLE_U5
          self.chopperDir = DIRECTION_RIGHT
        elif self.vx > targVel:
          bodyAngle = ANGLE_D10
        elif self.vx < 0:
          bodyAngle = ANGLE_D5
      else: # targVel == 0
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
    p.y -= 30
    if self.chopperDir == DIRECTION_LEFT:
      p.x += 30
      chopperAngle = -chopperAngle
      tRotorX = p.x + 65
      rotorOffx = -35
    elif self.chopperDir == DIRECTION_RIGHT:
      p.x -= 24
      tRotorX = p.x - 65
      rotorOffx = 20
    else:
      rotorOffx = 0

    if bodyAngle == ANGLE_0:
      tRotorY = p.y - 17
    elif bodyAngle == ANGLE_U5:
      tRotorY = p.y - 10
    elif bodyAngle == ANGLE_D5:
      tRotorY = p.y - 23
    elif bodyAngle == ANGLE_D10:
      tRotorY = p.y - 28

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

    e.canvas.create_image( p.x, p.y, image=img ) # puts 0,0 where the body hits the rotor
    # Rotor
    ROTOR_LEN = 70
    rotorLen = ROTOR_LEN * math.cos( self.rotorTheta )
    e.canvas.create_line( ( p.x + rotorOffx ) + rotorLen * math.cos( chopperAngle ),
                          ( p.y - 12 )        + rotorLen * math.sin( chopperAngle ),
                          ( p.x + rotorOffx ) + rotorLen * math.cos( chopperAngle + PI ),
                          ( p.y - 12 )        + rotorLen * math.sin( chopperAngle + PI ) )
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
    e.canvas.create_rectangle( p.x - 60, projShadow.y, p.x + 60, projShadow.y, outline="black" )

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
      dispX = p.x
      dispY = p.y - 50 # display floating above the chopper
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
      gx = p.x + 50
      gy = p.y + 15
      e.canvas.create_line( gx, gy,
                            gx + 10.0 * math.cos( self.gunAngle ),
                            gy - 10.0 * math.sin( self.gunAngle ),
                            fill="gray",
                            width=3 )
    elif self.chopperDir == DIRECTION_LEFT:
      gx = p.x - 60
      gy = p.y + 15
      e.canvas.create_line( gx, gy,
                            gx - 10.0 * math.cos( -self.gunAngle ),
                            gy + 10.0 * math.sin( -self.gunAngle ),
                            fill="gray",
                            width=3 )

    # Fuel level
    e.canvas.create_rectangle( 10, 10, 10 + 100.0 * 2, 15, fill="red" )
    e.canvas.create_rectangle( 10, 10, 10 + self.fuel * 2, 15, fill="green" )
    # Structural integrity
    e.canvas.create_rectangle( 10, 15, 10 + 200, 20, fill="red" )
    e.canvas.create_rectangle( 10, 15, int( 10 + self.si * 200/SI_CHOPPER ), 20, fill="green" )
    # Number of weapons
    for i in range( 0, self.countSmallMissiles ):
      e.canvas.create_image( 10, 50 + 6 * i, image=self.missileSImg )
    for i in range( 0, self.countLargeMissiles ):
      e.canvas.create_image( 70, 50 + 6 * i, image=self.missileLImg )
    for i in range( 0, self.countBomb ):
      e.canvas.create_image( 10 + 10 * i, 35, image=self.bombImg )
    t = "Rounds %s" % self.countBullet
    e.canvas.create_text( 100, 30, text=t )