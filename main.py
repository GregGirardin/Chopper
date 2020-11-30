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
    self.currentCamOff = 0 # Start from the left initially to show the City
    self.debugCoords = False # True # debug. Show x,y and collision box
    self.chopper = None
    self.citySI = 100.0
    self.level = 1
    self.statusMessages = []
    self.statusMsgTime = 0
    self.msgQ = []

  # this is called from objects probably in the context of update()
  # take actions later in processMessage() after all update()s have been called.
  def qMessage( self, m, param ):
    self.msgQ.append( ( m, param ) )

  def processMessage( self, m, param ):

    if m == MSG_BUILDING_DESTROYED:
      anyBuildings = False
      for o in self.objects:
        if o.oType == OBJECT_TYPE_BUILDING:
          anyBuildings = True
          break
      if not anyBuildings:
        self.addStatusMessage( "City has been destroyed." )
      else:
        self.addStatusMessage( "City has been bombed." )

    elif m == MSG_E_BUILDING_DESTROYED:
      anyBuildings = False
      for o in self.objects:
        if o.oType == OBJECT_TYPE_E_BUILDING:
          anyBuildings = True
          break
      if not anyBuildings:
        self.addStatusMessage( "Enemy base has been destroyed." )

      elif m == MSG_ENEMY_DESTROYED:
        # see if it's the last one.
        self.score += param.points
        anyEnemies = False
        for o in self.objects:
          if o.oType >= OBJECT_TYPE_FIRST_ENEMY and o.oType <= OBJECT_TYPE_LAST_ENEMY:
            anyEnemies = True
            break
        if not anyEnemies:
          self.addStatusMessage( "All enemies destroyed" )

      elif m == MSG_CHOPPER_DESTROYED:
        self.addStatusMessage( "Chopper Destroyed!" )

  def newLevel( self, level ):
    global chopper

    self.statusMessages = [ ]
    self.statusMsgTime = None
    self.statusMsgCurrent = None

    self.level = level
    self.levelComplete = False
    self.time = 0
    self.bg_objects = [] # Background objects that don't interact with anything.. no collisions or update
    self.objects = [] # buildings / vehicles / smoke / bullets. Things that require updates and collisions
    # Two lists to speed up collision detection and other interactions of objects that can interact.
    # We call update() and check for collisions for objects[]

    # Sky and ground
    self.bg_objects.append( SkyGround() )

    # Mountain range
    self.bg_objects.append( MountainImg( 200, 0, HORIZON_DISTANCE / 2 ) )

    # Clouds
    for z in range( 1, 10 ):
      self.bg_objects.append( Cloud( random.randint( MIN_WORLD_X, MAX_WORLD_X ),
                                     random.randint( 150, 250 ),
                                     random.randint( 500, 2000 ) ) ) # in front of the mountains
    # Rocks
    '''
    for z in range( -5, 9, 1 ): # Z is behind projection plane but the math works.
      x = random.randint( -500, 500 )
      if math.fabs( x ) > 30:
        self.bg_objects.append( Rock( x, 0, z ) )
    '''

    # Grass
    for z in range( 20, 40, 1 ):
      x = random.randint( -20, 1000 )
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

    buildCity( self, MIN_WORLD_X - 10, 10 )
    buildBase( self, MAX_WORLD_X / 3, 10 ) # construct enemy base

    self.objects.append( GameManager( self ) )

    # Debug stuff
    '''
    self.bg_objects.append( City( MIN_WORLD_X - 20, 0, 0 ) )
    self.objects.append( Bomber( Point ( -20, 20, 0 ), DIRECTION_LEFT ) )
    self.objects.append( Transporter( Point ( 0, 20, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Tank( Point(  10, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Jeep( Point(  -30, 0, 0 ), DIRECTION_LEFT ) )
    self.objects.append( Jeep( Point(  -20, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Transport1( Point(  -10, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Transport2( Point(  10, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Truck( Point(  30, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( dbgPoint( Point(  0, 0, 0 ) ) )
    '''
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
    self.addStatusMessage( "Game Over.", time=100 )

  def update( self ):
    self.time += 1

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
      p = projection( self.camera, o.p )
      if p.x < SCREEN_WIDTH + 100 and p.x > -500:
        o.draw( self, p )
        if self.debugCoords:
          e.canvas.create_rectangle( p.x - 1, p.y - 1, p.x + 1, p.y + 1, outline="red" )
    for o in self.objects:
      p = projection( self.camera, o.p )
      if p.x < SCREEN_WIDTH + 100 and p.x > -500:
        o.draw( self, p )
        if self.debugCoords:
          e.canvas.create_rectangle( p.x - 1, p.y - 1, p.x + 1, p.y + 1, outline="red" )
          displayColRect( e, o )

    if self.statusMsgTime > 0:
      self.statusMsgTime -= 1
      e.canvas.create_text( SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3,
                            text=self.statusMsgCurrent, fill='red',
                            font=tkFont.Font( family='Helvetica', size=28, weight='bold' ) )
    elif self.statusMessages:
      m = self.statusMessages.pop()
      self.statusMsgCurrent = m[ 0 ]
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

e.newLevel( 1 )

while True:
  e.update()
  while e.msgQ:
    m = e.msgQ.pop()
    e.processMessage( m[ 0 ], m[ 1 ] )
  e.draw()