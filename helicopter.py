import constants
import math, random
from utils import *
from PIL import ImageTk, Image

heloImages = {} # Dictionary of [ name : PhotoImage ] of chopper images. Global in case we make more than one.

class Helicopter():
  def __init__( self, x, y, z ):
    self.fuel = 100.0
    self.rotorSpeed = ROTOR_SLOW
    self.p = Point( x, y, z )
    self.rotorTheta = 0.0
    self.loadImages()
    self.imagesDict = heloImages
    self.vertVelocity = 0.0
    self.velocity = 0.0
    self.tgtVelocity = 0.0
    # Target velocity enum -> velocity map
    self.tgtVelDict = \
    {
      TGT_VEL_STOP        :  0.0,
      TGT_VEL_LEFT_SLOW   : -1.0,
      TGT_VEL_LEFT_MED    : -2.0,
      TGT_VEL_LEFT_FAST   : -4.0,
      TGT_VEL_RIGHT_SLOW  :  1.0,
      TGT_VEL_RIGHT_MED   :  2.0,
      TGT_VEL_RIGHT_FAST  :  4.0
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
    self.rotorTheta -= self.rotorSpeed / 2.0 # spin the rotors
    if self.rotorTheta < 0:
      self.rotorTheta += 2 * PI

    self.p.y += self.vertVelocity
    if self.p.y > MAX_ALTITUDE:
      self.p.y = MAX_ALTITUDE
      self.vertVelocity = 0
    elif self.p.y <= 0:
      self.p.y = 0
      self.vertVelocity = 0
      self.velocity = 0

    if self.vertVelocity > 0:
      self.thrust = ROTOR_FAST
    elif self.p.y > 0:
      self.thrust = ROTOR_SLOW

    # self.thrust = ROTOR_STOP
    # self.rotorTheta = 0.0

    if self.velocity < self.tgtVelocity:
      self.velocity += .1
    elif self.velocity > self.tgtVelocity:
      self.velocity -= .1
    if math.fabs( self.velocity - self.tgtVelocity ) < .1: # in case of rounding errors
      self.velocity = self.tgtVelocity

    self.p.x += self.velocity

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )
    projShadow = projection( e.camera, Point( self.p.x, 0, self.p.z ) )

    # Determine sprite and the corresponding rotor parameters
    # offset from projection if left is (30,-20) if right is
    bodyAngle = ANGLE_0
    chopperDir = DIRECTION_FORWARD

    if self.tgtVelocity > 0: # Want to go right (+x dir)
      chopperDir = DIRECTION_RIGHT
      if self.velocity < 0: # but still going left, angle left but 'up' to slow down before turning.
        chopperDir = DIRECTION_LEFT
        bodyAngle = ANGLE_U5
      elif self.velocity < self.tgtVelocity:
        bodyAngle = ANGLE_D10
      elif self.velocity > 0:
        bodyAngle = ANGLE_D5
    elif self.tgtVelocity < 0:
      chopperDir = DIRECTION_LEFT
      if self.velocity > 0: # but still going right, go 'up' to slow down before turning.
        bodyAngle = ANGLE_U5
        chopperDir = DIRECTION_RIGHT
      elif self.velocity > self.tgtVelocity:
        bodyAngle = ANGLE_D10
      elif self.velocity < 0:
        bodyAngle = ANGLE_D5
    else: #self.tgtVelocity == 0
      if self.velocity != 0:
        chopperDir = DIRECTION_LEFT if self.velocity < 0 else DIRECTION_RIGHT
        bodyAngle = ANGLE_0
      else:
        chopperDir = DIRECTION_FORWARD

    # body
    chopperAngle = 0.0
    if bodyAngle == ANGLE_U5:
      chopperAngle = -.087 # if left
    elif bodyAngle == ANGLE_D5:
      chopperAngle = .087
    elif bodyAngle == ANGLE_D10:
      chopperAngle = .174

    # make x,y = point below the rotor
    proj.y -= 30

    if chopperDir == DIRECTION_LEFT:
      proj.x += 30
      chopperAngle = -chopperAngle
      tRotorX = proj.x + 60
      rotorOffx = -35
    elif chopperDir == DIRECTION_RIGHT:
      proj.x -= 24
      tRotorX = proj.x - 60
      rotorOffx = 20
    else:
      rotorOffx = 0

    tRotorY = (proj.y - 10) if bodyAngle == ANGLE_U5 else proj.y - 25

    imageKey = "body"
    if chopperDir == DIRECTION_FORWARD:
      imageKey += "Forward"
    elif chopperDir == DIRECTION_LEFT:
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
    if chopperDir != DIRECTION_FORWARD:
      TAIL_ROTOR_LEN = 20
      tmpTheta = self.rotorTheta
      if chopperDir == DIRECTION_RIGHT:
        tmpTheta = -tmpTheta
      e.canvas.create_line( tRotorX + TAIL_ROTOR_LEN * math.cos( tmpTheta ),
                            tRotorY + TAIL_ROTOR_LEN * math.sin( tmpTheta ),
                            tRotorX + TAIL_ROTOR_LEN * math.cos( tmpTheta + PI ),
                            tRotorY + TAIL_ROTOR_LEN * math.sin( tmpTheta + PI ) )

    # Shadow
    e.canvas.create_rectangle( proj.x - 60, projShadow.y, proj.x + 60, projShadow.y, outline="black" )
