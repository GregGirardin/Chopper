#!/usr/bin/python
from Tkinter import *
from constants import *
import time, math
from utils import *
from background import *
from helicopter import *
from missiles import *
from explosions import *
from jeep import *
from tank import *
from planes import *

chopper = None

class displayEngine():
  def __init__( self ):
    self.root = Tk()
    self.root.title( "Chopper" )
    self.canvas = Canvas( self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT )
    self.canvas.pack()

    self.camera = Point( 0, 20, CAM_Z )
    self.tgtCamOff = 0.0

  def newGame( self ):
    global chopper

    self.time = 0
    self.bg_objects = [] # Background objects that don't interact with anything
    self.active_objects = [] # buildings / vehicles / smoke / bullets
    # Two lists to speed up collision detection and other interactions of
    # objects that can interact.

    # Sky and ground
    self.bg_objects.append( SkyGround() )

    # Mountains
    for z in( MAX_MTN_DISTANCE, MAX_MTN_DISTANCE * .75, MAX_MTN_DISTANCE * .5 ):
      for _ in range( 1, MTN_PER_LAYER ):
        self.bg_objects.append( Mountain( random.randint( MIN_WORLD_X, MAX_WORLD_X - MAX_MTN_WIDTH ),
                                          random.randint( MAX_MTN_WIDTH / 4, MAX_MTN_WIDTH ),
                                          random.randint( MAX_MTN_HEIGHT / 4, MAX_MTN_HEIGHT ),
                                          z ) )
    # Mountains to indicate Borders
    self.bg_objects.append( Mountain( MIN_WORLD_X - 100, 100, 100, -20 ) )
    self.bg_objects.append( Mountain( MAX_WORLD_X, 100, 100, -20 ) )

    # Clouds
    for z in range( 1, 10 ):
      self.bg_objects.append( Cloud( random.randint( MIN_WORLD_X, MAX_WORLD_X ),
                                     random.randint( 150, 250 ),
                                     random.randint( 500, 1000 ) ) ) # in front of the mountains
    # Rocks
    for z in range( -5, 9, 1 ): # hmm, Z is behind projection plane but the math works.
      x = random.randint( -500, 500 )
      if math.fabs( x ) > 30:
        self.bg_objects.append( Rock( x, 0, z ) )

    # Grass
    for z in range( 20, 30, 1 ):
      x = random.randint( -500, 500 )
      if math.fabs( x ) > 30:
        self.bg_objects.append( Grass( x, 0, z ) )

    # Trees
    for z in range( 500, 50, -10 ):
      x = random.randint( -500, 500 )
      if math.fabs( x ) > 30:
        self.bg_objects.append( Tree( x, 0, z ) )

    # Active objects.

    # Create the Chopper
    chopper = Helicopter( 0, 0, 1 )
    self.active_objects.append( chopper )

    # Base
    self.active_objects.append( Base( 20, 0, 2 ) )

    # Debug stuff
    self.active_objects.append( Jet( Point ( 250, 20, 0 ), DIRECTION_LEFT ) )
    self.active_objects.append( Truck( Point( 0, 0, 0 ), DIRECTION_LEFT ) )

    # Sort objects by decreasing Z so closer are drawn on top
    def increaseZ( o ):
      return -o.p.z

    self.bg_objects.sort( key=increaseZ )
    self.active_objects.sort( key=increaseZ )

  def addObject( self, object ):
    def increaseZ( o ):
      return -o.p.z
    self.active_objects.append( object )
    self.active_objects.sort( key=increaseZ )

  def gameOver( self ):
    pass

  def update( self ):
    self.time += 1

    # Update objects
    for o in self.bg_objects:
      o.update( self )

    for o in self.active_objects:
      if o.update( self ) == False:
        self.active_objects.remove( o )

    # Do collision detection

    # Spawn objects

    # update camera. Determine where we want it relative to the chopper
    # If chopper is facing left, we want the camera on the right side of the screen.
    if chopper.chopperDir == DIRECTION_LEFT:
      tgtCamOff = -30
    elif chopper.chopperDir == DIRECTION_RIGHT:
      tgtCamOff = 30
    else:
      tgtCamOff = 0

    if self.tgtCamOff < tgtCamOff:
      self.tgtCamOff += .5
    elif self.tgtCamOff > tgtCamOff:
      self.tgtCamOff -= .5

    self.camera.x = chopper.p.x + self.tgtCamOff
    if self.camera.x < MIN_WORLD_X:
      self.camera.x = MIN_WORLD_X
    elif self.camera.x > MAX_WORLD_X:
      self.camera.x = MAX_WORLD_X

    if chopper.p.y > 40:
      self.camera.y = chopper.p.y - 20
    else:
      self.camera.y = 20

  def draw( self ):
    self.canvas.delete( ALL )
    for o in self.bg_objects:
      o.draw( self )
    for o in self.active_objects:
      o.draw( self )
    self.root.update()

def leftHandler( event ):
  chopper.processMessage( MSG_ACCEL_L )
def rightHandler( event ):
  chopper.processMessage( MSG_ACCEL_R )
def upHandler( event ):
  chopper.processMessage( MSG_ACCEL_U )
def downHandler( event ):
  chopper.processMessage( MSG_ACCEL_D )

def keyHandler( event ):
  if event.char == "a":
    chopper.processMessage( MSG_WEAPON_MISSILE_S )
  elif event.char == "s":
    chopper.processMessage( MSG_WEAPON_MISSILE_L )
  elif event.char == "z":
    chopper.processMessage( MSG_WEAPON_BOMB )
  elif event.char == "e":
    chopper.processMessage( MSG_GUN_UP )
  elif event.char == "d":
    chopper.processMessage( MSG_GUN_DOWN )
  elif event.char == " ":
    chopper.processMessage( MSG_WEAPON_BULLET )

# Main
e = displayEngine()

e.root.bind( "<Left>",  leftHandler )
e.root.bind( "<Right>", rightHandler )
e.root.bind( "<Up>",    upHandler )
e.root.bind( "<Down>",  downHandler )
e.root.bind( "<Key>",   keyHandler )

e.newGame()

while True:
  time.sleep( .01 )

  e.update()
  e.draw()