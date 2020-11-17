#!/usr/bin/python
from Tkinter import *
from constants import *
import time, math
from utils import *
from background import *
from helicopter import *

chopper = None

class displayEngine():
  def __init__( self ):
    self.root = Tk()
    self.root.title( "Chopper" )
    self.canvas = Canvas( self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT )
    self.canvas.pack()

    self.camera = Point( -20, 20, CAM_Z )
    self.tgtCamOff = 0

  def newGame( self ):
    global chopper

    self.time = 0
    self.objects = []

    # create the helo
    chopper = Helicopter( 0, 0, 10)
    self.objects.append( chopper )

    # Sky and Ground
    self.objects.append( SkyGround() )

    # Mountains
    for z in( MAX_MTN_DISTANCE, MAX_MTN_DISTANCE * .75, MAX_MTN_DISTANCE * .5 ):
      for _ in range( 1, MTN_PER_LAYER ):
        self.objects.append( Mountain( random.randint( MIN_WORLD_X, MAX_WORLD_X - MAX_MTN_WIDTH ),
                                       random.randint( MAX_MTN_WIDTH / 4, MAX_MTN_WIDTH ),
                                       random.randint( MAX_MTN_HEIGHT / 4, MAX_MTN_HEIGHT ),
                                       z ) )
    # Clouds
    for z in range( 1, 10 ):
      self.objects.append( Cloud( random.randint( MIN_WORLD_X, MAX_WORLD_X ),
                                  random.randint( 150, 250 ),
                                  random.randint( 500, 1000 ) ) ) # in front of the mountains
    # Rocks
    for z in range( -5, 9, 1 ): # hmm, Z is behind projection plane but the math works.
      self.objects.append( Rock( random.randint( -500, 500 ), 0, z ) )

    # Grass
    for z in range( -5, 9, 1 ): # hmm, Z is behind projection plane but the math works.
      self.objects.append( Grass( random.randint( -500, 500 ), 0, z ) )

    # Trees
    for z in range( 500, 50, -10 ):
      self.objects.append( Tree( random.randint( -500, 500 ), 0, z ) )

    # Base
    self.objects.append( Base( 20, 0, 20 ) )

    # Debug point
    # self.objects.append( dbgPoint( 0, 0, 10 ) )

    # Sort objects by decreasing Z to closer are drawn on top
    def increaseZ( o ):
      return -o.p.z
    self.objects.sort( key=increaseZ )

  def gameOver( self ):
    pass

  def update( self ):
    global chopper

    self.time += 1

    # Update objects
    for o in self.objects:
      if o.update( self ) == False:
        self.objects.remove( o )

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
      self.tgtCamOff += 1
    elif self.tgtCamOff > tgtCamOff:
      self.tgtCamOff -= 1

    self.camera.x = chopper.p.x + self.tgtCamOff

  def draw( self ):
    self.canvas.delete( ALL )
    for o in self.objects:
      o.draw( self )

    self.root.update()

def leftHandler( event ):
  global chopper
  if chopper.tgtVelocity > TGT_VEL_LEFT_FAST:
    chopper.tgtVelocity -= 1

def rightHandler( event ):
  global chopper
  if chopper.tgtVelocity < TGT_VEL_RIGHT_FAST:
    chopper.tgtVelocity += 1

def upHandler( event ):
  global chopper
  if chopper.vertVelocity < .6:
    chopper.vertVelocity += .3

def downHandler( event ):
  global chopper
  if chopper.vertVelocity > -.6:
    chopper.vertVelocity -= .3

def keyHandler( event ):
  # if event.char == " ":
  pass

# Main
e = displayEngine()

e.root.bind( "<Left>",  leftHandler )
e.root.bind( "<Right>", rightHandler )
e.root.bind( "<Up>",    upHandler )
e.root.bind( "<Down>",  downHandler )
e.root.bind( "<Key>",   keyHandler )

e.newGame()

while True:
  time.sleep( .02 )

  e.update()
  e.draw()