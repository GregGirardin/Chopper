#!/usr/bin/python
from Tkinter import *
import tkFont
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
from enemyAI import *
import random

chopper = None

class displayEngine():
  def __init__( self ):
    self.root = Tk()
    self.root.title( "Chopper" )
    self.canvas = Canvas( self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT )
    self.canvas.pack()

    self.camera = Point( 0, 15, CAM_Z )
    self.currentCamOff = -50 # Start from the left initially to show the City
    self.debugCoords = True # True # debug. Show x,y and collision box

    self.chopper = None # keep a reference since a
    self.citySI = 100.0
    self.level = 1

  def cityBombed( self, si ):
    self.cityCasualties += si
    self.displayCityTime = 30
    self.addStatusMessage( "City has been bombed.", 25 )

  def newGame( self ):
    global chopper

    self.statusMessages = []
    self.statusMsgTime = None
    self.statusMsgCurrent = None

    self.cityCasualties = 0
    self.level = 1

    self.time = 0
    self.bg_objects = [] # Background objects that don't interact with anything.. no collisions or update
    self.objects = [] # buildings / vehicles / smoke / bullets. Things that require updates and collisions
    # Two lists to speed up collision detection and other interactions of objects that can interact.

    # Sky and ground
    self.bg_objects.append( SkyGround() )

    # Mountains
    for z in( MAX_MTN_DISTANCE, MAX_MTN_DISTANCE * .75, MAX_MTN_DISTANCE * .5 ):
      for _ in range( 1, MTN_PER_LAYER ):
        self.bg_objects.append( Mountain( random.randint( MIN_WORLD_X - 1000,
                                                          MAX_WORLD_X + 1000 ),
                                          random.randint( MAX_MTN_WIDTH / 4, MAX_MTN_WIDTH ),
                                          random.randint( MAX_MTN_HEIGHT / 4, MAX_MTN_HEIGHT ),
                                          z ) )

    # Clouds
    for z in range( 1, 10 ):
      self.bg_objects.append( Cloud( random.randint( MIN_WORLD_X, MAX_WORLD_X ),
                                     random.randint( 150, 250 ),
                                     random.randint( 500, 1000 ) ) ) # in front of the mountains
    # Rocks
    for z in range( -5, 9, 1 ): # Z is behind projection plane but the math works.
      x = random.randint( -500, 500 )
      if math.fabs( x ) > 30:
        self.bg_objects.append( Rock( x, 0, z ) )

    # Grass
    for z in range( 20, 30, 1 ):
      x = random.randint( -300, 300 )
      if math.fabs( x ) > 20:
        self.bg_objects.append( Grass( x, 0, z ) )

    # Trees
    for z in range( 500, 50, -10 ):
      x = random.randint( -500, 500 )
      if math.fabs( x ) > 20:
        self.bg_objects.append( Tree( x, 0, z ) )

    # Base
    self.bg_objects.append( Base( 0, 0, 2, label="Base" ) )

    # Active objects. (we call update() and check for collisions)

    # Create the Chopper
    chopper = Helicopter( 0, 0, 1 )
    self.objects.append( chopper )
    self.chopper = chopper

    buildCity( self, MIN_WORLD_X - 50, 8 )
    buildBase( self, MAX_WORLD_X / 3, 2 ) # construct enemy base

    self.objects.append( GameManager() )

    # Debug stuff
    '''
    self.bg_objects.append( City( MIN_WORLD_X - 20, 0, 0 ) )
    self.objects.append( Bomber( Point ( -20, 20, 0 ), DIRECTION_LEFT ) ) # DIRECTION_RIGHT DIRECTION_LEFT
    self.objects.append( Transporter( Point ( 0, 20, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Tank( Point(  10, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Jeep( Point(  -30, 0, 0 ), DIRECTION_LEFT ) )
    self.objects.append( Jeep( Point(  -20, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Transport1( Point(  -10, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Transport2( Point(  10, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Truck( Point(  30, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( dbgPoint( Point(  0, 0, 0 ) ) )

    '''
    self.objects.append( Fighter( Point ( 200, 20, 0 ), DIRECTION_LEFT ) )

    # Sort objects by decreasing Z so closer are drawn on top
    def increaseZ( o ):
      return -o.p.z

    self.bg_objects.sort( key=increaseZ )
    self.objects.sort( key=increaseZ )

  def addObject( self, object ):
    def increaseZ( o ):
      return -o.p.z
    self.objects.append( object )
    self.objects.sort( key=increaseZ )

  # Q's a status message to be displayed at the center of the screen. time is display cycles.
  def addStatusMessage( self, m, time=50 ):
    self.statusMessages.insert( 0, ( m, time ) ) # list contains (string,time) tuples. Newest to head, pull from end

  def gameOver( self ):
    self.addStatusMessage( "Game Over.", time=200 )

  def update( self ):
    self.time += 1

    if self.time == 50:
      self.addStatusMessage( "Stage 1" )
      self.addStatusMessage( "Defend the city" )
      self.addStatusMessage( "Destroy enemy base ->" )

    # Collision detection
    numObjects = len( self.objects )
    for i in range( 0, numObjects - 1 ):
      for j in range( i + 1, numObjects ):
        obj1 = self.objects[ i ]
        obj2 = self.objects[ j ]
        if collisionCheck( self, obj1, obj2 ):
          obj1.processMessage( self, MSG_COLLISION_DET, obj2 )
          obj2.processMessage( self, MSG_COLLISION_DET, obj1 )

    # Update objects
    for o in self.objects:
      if o.update( self ) == False:
        self.objects.remove( o )

    # Move the camera. Determine where we want it relative to the chopper
    # If chopper is facing left, we want the camera on the right side of the screen.
    tgtCamOff = [ -30, 30, 0 ][ chopper.chopperDir ]

    if self.currentCamOff < tgtCamOff:
      self.currentCamOff += .5
    elif self.currentCamOff > tgtCamOff:
      self.currentCamOff -= .5

    self.camera.x = chopper.p.x + self.currentCamOff
    if self.camera.x < MIN_WORLD_X:
      self.camera.x = MIN_WORLD_X
    elif self.camera.x > MAX_WORLD_X:
      self.camera.x = MAX_WORLD_X

    self.camera.y = ( chopper.p.y - 20 ) if chopper.p.y > 40 else 20

  def draw( self ):
    self.canvas.delete( ALL )
    for o in self.bg_objects:
      o.draw( self )
      if self.debugCoords:
        proj = projection( self.camera, o.p )
        e.canvas.create_rectangle( proj.x - 1, proj.y - 1, proj.x + 1, proj.y + 1, outline="red" )
    for o in self.objects:
      o.draw( self )
      if self.debugCoords:
        proj = projection( self.camera, o.p )
        e.canvas.create_rectangle( proj.x - 1, proj.y - 1, proj.x + 1, proj.y + 1, outline="red" )
        displayColRect( e, o )

    if self.statusMsgTime > 0:
      self.statusMsgTime -= 1
      e.canvas.create_text( SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3,
                            text=self.statusMsgCurrent, fill='red',
                            font=tkFont.Font( family='Helvetica', size=28, weight='bold' ) )
    elif self.statusMessages:
      m = self.statusMessages.pop()
      self.statusMsgCurrent = m [ 0 ]
      self.statusMsgTime = m[ 1 ]

    self.root.update()

def leftHandler( event ):
  chopper.processMessage( e, MSG_ACCEL_L )
def rightHandler( event ):
  chopper.processMessage( e, MSG_ACCEL_R )
def upHandler( event ):
  chopper.processMessage( e, MSG_ACCEL_U )
def downHandler( event ):
  chopper.processMessage( e, MSG_ACCEL_D )

def keyHandler( event ):
  if event.char == "a":
    chopper.processMessage( e, MSG_WEAPON_MISSILE_S )
  elif event.char == "s":
    chopper.processMessage( e, MSG_WEAPON_MISSILE_L )
  elif event.char == "z":
    chopper.processMessage( e, MSG_WEAPON_BOMB )
  elif event.char == "e":
    chopper.processMessage( e, MSG_GUN_UP )
  elif event.char == "d":
    chopper.processMessage( e, MSG_GUN_DOWN )
  elif event.char == " ":
    chopper.processMessage( e, MSG_WEAPON_BULLET )

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