#!/usr/bin/python
from Tkinter import *
from constants import *
import time
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

  def newGame( self ):
    global chopper

    self.objects = []

    # Sky and Ground
    self.objects.append( SkyGround() )

    # Create mountains
    # Furthest first. Drawn in order so want closer in front
    for z in( MAX_MTN_DISTANCE, MAX_MTN_DISTANCE * .75, MAX_MTN_DISTANCE * .5 ):
      for _ in range( 1, MTN_PER_LAYER ):
        self.objects.append( Mountain( random.randint( MIN_WORLD_X, MAX_WORLD_X - MAX_MTN_WIDTH ),
                                       random.randint( MAX_MTN_WIDTH / 4, MAX_MTN_WIDTH ),
                                       random.randint( MAX_MTN_HEIGHT / 4, MAX_MTN_HEIGHT ),
                                       z ) )
    # create clouds
    for z in range( 1, 10 ):
      self.objects.append( Cloud( random.randint( MIN_WORLD_X, MAX_WORLD_X ),
                                  random.randint( 150, 250 ),
                                  random.randint( 500, 1000 ) ) ) # in front of the mountains
    # create rock layers?

    # create trees
    for z in range( 500, 50, -10 ):
      self.objects.append( Tree( random.randint( -500, 500 ), 0, z ) )

    # create the helo
    chopper = Helicopter( 0, 0, 10)
    self.objects.append( chopper )

    # create the Base
    self.objects.append( Base( 20, 0, 20 ) )

    # debug point
    self.objects.append( dbgPoint( 0, 0, 10 ) )

    # Sort objects by decreasing Z to closer are drawn on top
    def increaseZ( o ):
      return -o.p.z
    self.objects.sort( key=increaseZ )

  def gameOver( self ):
    pass

  def update( self ):
    #if self.camera.x < 2000:
    #  self.camera.x += 5
    #elif self.camera.y < 50:
    #  self.camera.y += 2

    # self.chopper.p.y += 1

    # Update objects
    for o in self.objects:
      if o.update( self ) == False:
        self.objects.remove( o )

    # Do collision detection

    # Spawn objects

  def draw( self ):
    self.canvas.delete( ALL )
    for o in self.objects:
      o.draw( self )

    self.root.update()

def leftHandler( event ):
  pass
def rightHandler( event ):
  pass

def upHandler( event ):
  global chopper

  if chopper.thrust < 10.0:
    chopper.thrust += 1
def downHandler( event ):
  global chopper

  if chopper.thrust > 0:
    chopper.thrust -= 1

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
  time.sleep( .05 )

  e.update()
  e.draw()