import constants
import math, random
from utils import *
from PIL import ImageTk, Image

heloImages = {} # Dictionary of [ name : PhotoImage ] of chopper images. Global in case we make more than one.

class Helicopter():
  def __init__( self, x, y, z ):
    self.p = Point( x, y, z )
    self.rotorSpeed = ROTOR_SLOW
    self.fuel = 100.0
    self.rotorTheta = 0.0
    self.loadImages()
    self.imagesDict = heloImages
    self.vertVelocity = 0.0
    self.velocity = 0.0
    self.tgtVelocity = TGT_VEL_STOP
    self.chopperDir = DIRECTION_FORWARD
    # Target velocity enum -> velocity map
    self.tgtVelDict = \
    {
      TGT_VEL_STOP        :  0.0,
      TGT_VEL_LEFT_STOP   :  0.0,
      TGT_VEL_LEFT_SLOW   : -1.0,
      TGT_VEL_LEFT_FAST   : -2.0,
      TGT_VEL_RIGHT_STOP  :  0.0,
      TGT_VEL_RIGHT_SLOW  :  1.0,
      TGT_VEL_RIGHT_FAST  :  2.0
    }

    self.angleDict = \
    {
      ANGLE_0   : 0.0,
      ANGLE_U5  : -.087,
      ANGLE_D5  : .087,
      ANGLE_D10 : .174
    }

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
    self.rotorTheta -= self.rotorSpeed / 2.0 # Spin the rotors
    if self.rotorTheta < 0:
      self.rotorTheta += 2 * PI

    self.p.y += self.vertVelocity
    if self.p.y > MAX_ALTITUDE:
      self.p.y = MAX_ALTITUDE
      self.vertVelocity = 0
    elif self.p.y <= 0: # TBD, check for crash
      self.p.y = 0
      self.vertVelocity = 0
      self.velocity = 0
      self.tgtVelocity = TGT_VEL_STOP

    if self.vertVelocity > 0:
      self.rotorSpeed = ROTOR_FAST
    elif self.p.y > 0:
      self.rotorSpeed = ROTOR_SLOW

    targetVelocity = self.tgtVelDict[ self.tgtVelocity ]

    if self.velocity < targetVelocity:
      self.velocity += .05
    elif self.velocity > targetVelocity:
      self.velocity -= .05
    if math.fabs( self.velocity - targetVelocity ) < .05: # in case of rounding errors
      self.velocity = targetVelocity

    self.p.x += self.velocity

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    # Determine sprite and the corresponding rotor positions
    bodyAngle = ANGLE_0
    self.chopperDir = DIRECTION_FORWARD
    targetVelocity = self.tgtVelDict[ self.tgtVelocity ]

    if self.p.y != 0: # We're on the ground
      if targetVelocity > 0.0: # Want to go right (+x dir)
        self.chopperDir = DIRECTION_RIGHT
        if self.velocity < 0.0: # but still going left, angle left but 'up' to slow down before turning.
          self.chopperDir = DIRECTION_LEFT
          bodyAngle = ANGLE_U5
        elif self.velocity < targetVelocity:
          bodyAngle = ANGLE_D10
        elif self.velocity > 0:
          bodyAngle = ANGLE_D5
      elif targetVelocity < 0.0:
        self.chopperDir = DIRECTION_LEFT
        if self.velocity > 0: # but still going right, go 'up' to slow down before turning.
          bodyAngle = ANGLE_U5
          self.chopperDir = DIRECTION_RIGHT
        elif self.velocity > targetVelocity:
          bodyAngle = ANGLE_D10
        elif self.velocity < 0:
          bodyAngle = ANGLE_D5
      else: # targetVelocity == 0
        if self.velocity != 0:
          self.chopperDir = DIRECTION_LEFT if self.velocity < 0 else DIRECTION_RIGHT
          bodyAngle = ANGLE_0
        else:
          if self.tgtVelocity == TGT_VEL_LEFT_STOP:
            self.chopperDir = DIRECTION_LEFT
          elif self.tgtVelocity == TGT_VEL_RIGHT_STOP:
            self.chopperDir = DIRECTION_RIGHT
          else:
            self.chopperDir = DIRECTION_FORWARD
    # body
    chopperAngle = self.angleDict[ bodyAngle ]

    # translate x,y to be below the rotor
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

    imageKey = "body"
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
                          ( proj.y - 12 ) + rotorLen * math.sin( chopperAngle ),
                          ( proj.x + rotorOffx ) + rotorLen * math.cos( chopperAngle + PI ),
                          ( proj.y - 12 ) + rotorLen * math.sin( chopperAngle + PI ) )
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
