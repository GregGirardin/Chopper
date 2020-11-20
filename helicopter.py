import constants
import math, random
from utils import *
from PIL import ImageTk, Image
from missiles import *

heloImages = {} # Dictionary of [ name : PhotoImage ] of chopper images. Global in case we make more than one.

class Helicopter():
  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.rotorSpeed = ROTOR_SLOW
    self.fuel = 100.0
    self.rotorTheta = 0.0
    self.loadImages()
    self.imagesDict = heloImages
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
    self.bullets = 1000

    # Target vx enum -> vx map
    self.tgtXVelDict = \
    {
      TGT_VEL_STOP        :  0.0,
      TGT_VEL_LEFT_STOP   :  0.0,
      TGT_VEL_LEFT_SLOW   : -1.0,
      TGT_VEL_LEFT_FAST   : -2.0,
      TGT_VEL_RIGHT_STOP  :  0.0,
      TGT_VEL_RIGHT_SLOW  :  1.0,
      TGT_VEL_RIGHT_FAST  :  2.0
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

    self.angleDict = \
    {
      ANGLE_0   : 0.0,
      ANGLE_U5  : -.087,
      ANGLE_D5  : .087,
      ANGLE_D10 : .174
    }
    # weapon images for inventory
    self.missileSImg = ImageTk.PhotoImage( Image.open( "images/chopper/missileB_L.gif" ) )
    self.missileLImg = ImageTk.PhotoImage( Image.open( "images/chopper/missileA_L.gif" ) )
    bombImage = Image.open( "images/chopper/bomb.gif" )
    bombImage = bombImage.resize( ( 10, 30 ) )
    self.bombImg = ImageTk.PhotoImage( bombImage )

  def processMessage( self, message ):
    if message == MSG_ACCEL_L:
      if self.tgtXVelocity > TGT_VEL_LEFT_FAST:
        self.tgtXVelocity -= 1
    elif message == MSG_ACCEL_R:
      if self.tgtXVelocity < TGT_VEL_RIGHT_FAST:
        self.tgtXVelocity += 1
    elif message == MSG_ACCEL_U:
      if self.tgtYVelocity < TGT_VEL_UP_FAST:
        self.tgtYVelocity += 1
    elif message == MSG_ACCEL_D:
      if self.tgtYVelocity > TGT_VEL_DN_FAST:
        self.tgtYVelocity -= 1
    # Don't spawn the weapon here.
    # Let's keep that loosely coupled. Spawn in update().
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

  def loadImages( self ):
    global heloImages
    imageNames = ( "bodyForward",
                   "bodyLeft",  "bodyLeftD5",  "bodyLeftD10",  "bodyLeftU5",
                   "bodyRight", "bodyRightD5", "bodyRightD10", "bodyRightU5" )

    if len( heloImages ) == 0:
      for name in imageNames:
        heloImages[ name ] = ImageTk.PhotoImage( Image.open( "images/chopper/" + name + ".gif" ) )

    self.imagesDict = heloImages

  def update( self, e ):
    # Check fuel consumption
    if self.p.y > 0.0:
      self.fuel -= .11
      if self.vx != 0:
        self.fuel -= math.fabs( self.vx ) * .01
    if self.fuel <= 0.0 and self.p.y > 0.0:
      self.vy -= .1
      self.vx *= .9

    self.rotorTheta -= self.rotorSpeed / 2.0 # Spin the rotors
    if self.rotorTheta < 0:
      self.rotorTheta += 2 * PI

    if self.fuel > 0.0: # Accelerate to target velocities if we have fuel
      tv = self.tgtXVelDict[ self.tgtXVelocity ]
      if self.vx < tv:
        self.vx += .05
      elif self.vx > tv:
        self.vx -= .05
      if math.fabs( self.vx - tv ) < .01: # In case of rounding
        self.vx = tv

      tv = self.tgtYVelDict[ self.tgtYVelocity ]
      if self.vy < tv:
        self.vy += .05
      elif self.vy > tv:
        self.vy -= .05
      if math.fabs( self.vy - tv ) < .01: # In case of rounding
        self.vy = tv

    self.p.y += self.vy
    self.p.x += self.vx

    if self.p.y > MAX_ALTITUDE:
      self.vy -= .1
      self.tgtYVelocity = TGT_VEL_STOP
    elif self.p.y <= 0: # On the ground.
      self.p.y = 0
      self.vy = 0
      self.vx = 0
      self.tgtXVelocity = TGT_VEL_STOP
      self.tgtYVelocity = TGT_VEL_STOP

    if self.vy > 0:
      self.rotorSpeed = ROTOR_FAST
    elif self.p.y > 0:
      self.rotorSpeed = ROTOR_SLOW

    # Weapon spawning
    if self.weapon != WEAPON_NONE:
      if self.weapon == WEAPON_SMALL_MISSILE:
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

    img = self.imagesDict[ imageKey ]

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
    e.canvas.create_rectangle( SCREEN_WIDTH / 2 - 2, 20, SCREEN_WIDTH / 2 + 2, 25, fill="black" ) # a red block in the center
    xLen = tgtVelDispDict[ self.tgtXVelocity ]
    if xLen:
      if xLen > 0:
        for xPos in range( 0, xLen ):
          e.canvas.create_rectangle( SCREEN_WIDTH / 2 + 3 + 5 * xPos, 20,
                                     SCREEN_WIDTH / 2 + 8 + 5 * xPos, 25,
                                     fill="red" )
      else:
        for xPos in range( xLen, 0 ):
          e.canvas.create_rectangle( SCREEN_WIDTH / 2 + 3 * xPos, 20,
                                     SCREEN_WIDTH / 2 - 3 + 5 * xPos, 25,
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
          e.canvas.create_rectangle( SCREEN_WIDTH / 2 - 2,
                                     15 - 5 * yPos,
                                     SCREEN_WIDTH / 2 + 2,
                                     20 - 5 * yPos,
                                     fill="red" )
      else:
        for yPos in range( yLen, 0 ):
          e.canvas.create_rectangle( SCREEN_WIDTH / 2 - 2,
                                     20 - 5 * yPos,
                                     SCREEN_WIDTH / 2 + 2,
                                     25 - 5 * yPos,
                                     fill="red" )
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
