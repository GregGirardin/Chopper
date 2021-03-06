#!/usr/bin/python
import tkinter.font as tkFont
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

class displayEngine():
  def __init__( self ):
    self.root = Tk()
    self.root.title( "Chopper" )
    self.canvas = Canvas( self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT )
    self.canvas.pack()

    #self.debugCoords = True # Show x,y and collision box
    self.debugCoords = False
    self.chopper = None
    self.highScore = 0
    self.statusMessages = []
    self.statusMsgTime = 0
    self.statusMsgCurrent = None
    self.msgQ = [] # Q of messages to loosely couple messaging
    self.newGameTimer = 0
    self.currentCamOff = -20 # Start from the left initially to show the City
    self.showDirections = True

    self.newGame()

  def newGame( self ):
    self.camera = Point( 0, 15, CAM_Z )
    self.level = 1
    self.score = 0
    self.numChoppers = NUM_CHOPPERS
    self.newLevel()
    self.fadeInCount = 0

  # This is called from objects probably in the context of update()
  # Take actions later in processMessage() after all update()s have been called.
  def qMessage( self, m, param=None ):
    self.msgQ.append( ( m, param ) )

  def __processMessage__( self, m, param ):

    if m == MSG_UI: # currently all UI messages are for the chopper.
      self.chopper.processMessage( self, param )

    elif m == MSG_BUILDING_DESTROYED:
      anyBuildings = False
      for o in self.objects:
        if o.oType == OBJECT_TYPE_BUILDING:
          anyBuildings = True
          break
      if not anyBuildings:
        self.addStatusMessage( "City Destroyed" )
        self.gameOver()
      else:
        self.addStatusMessage( "City Bombed" )

    elif m == MSG_E_BUILDING_DESTROYED:
      self.modScore( param.points )
      anyBuildings = False
      for o in self.objects:
        if o.oType == OBJECT_TYPE_E_BUILDING:
          anyBuildings = True
          break
      if not anyBuildings:
        self.enemyBaseDestroyed = True
        self.addStatusMessage( "Enemy Base Destroyed" )
        self.modScore( POINTS_E_BASE )

    elif m == MSG_ENEMY_LEFT_BATTLEFIELD:
      self.modScore( param.points )
      anyEnemies = False
      for o in self.objects:
        if o.oType >= OBJECT_TYPE_FIRST_ENEMY and o.oType <= OBJECT_TYPE_LAST_ENEMY:
          anyEnemies = True
          break
      if not anyEnemies and self.spawningComplete:
        self.allEnemiesDestroyed = True
        self.addStatusMessage( "No More Enemies : Return to Base" )

    elif m == MSG_CHOPPER_DESTROYED:
      self.numChoppers -= 1
      if self.numChoppers == 0:
        self.gameOver()
      else:
        self.addStatusMessage( "Chopper Destroyed %s remaining" % self.numChoppers )
        self.currentCamOff = self.chopper.p.x # So the camera pans from where we are back to base.
        self.chopper = Helicopter( 0, 0, 1 )
        self.objects.append( self.chopper )
        self.fadeInCount = 0

    elif m == MSG_SPAWNING_COMPLETE:
      self.spawningComplete = True

    elif m == MSG_SOLDIERS_TO_CITY:
      self.addStatusMessage( "Casualties!" )
      self.modScore( -param * 5 )

    elif m == MSG_MISSION_COMPLETE:
      self.addStatusMessage( "Level Complete." )
      cityBonus = 0
      for o in self.objects:
        if o.oType == OBJECT_TYPE_BUILDING:
          cityBonus += POINTS_BUILDING
      if cityBonus:
        self.addStatusMessage( "City bonus %s" % cityBonus )
        self.modScore( cityBonus )

      self.level += 1
      if self.level > NUM_LEVELS:
        self.addStatusMessage( "All levels complete" )
        self.gameOver()
      else:
        self.newLevel()

    elif m == MSG_CHOPPER_AT_BASE:
      if self.allEnemiesDestroyed:
        self.qMessage( MSG_MISSION_COMPLETE )

  def modScore( self, points ): # add / subtract points to score
    self.score += points
    if self.score < 0:
      self.score = 0
    if self.score > self.highScore:
      self.highScore = self.score

  def newLevel( self ):
    self.cameraOnHelo = False
    self.enemyBaseDestroyed = False
    self.spawningComplete = False
    self.allEnemiesDestroyed = False
    self.fadeInCount = 0

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
    self.bg_objects.append( HillImg( 200, 0, HORIZON_DISTANCE / 4 ) )

    # Clouds.. clouds move so they're active.
    for z in range( 1, 10 ):
      self.objects.append( Cloud( random.randint( MIN_WORLD_X - 1000, MAX_WORLD_X * 2 ),
                                  random.randint( 150, 225 ),
                                  random.randint( HORIZON_DISTANCE / 20,
                                                  HORIZON_DISTANCE / 2 ) ) ) # in front of the mountains
    # Rocks
    for z in range( -3, 12, 2 ): # Z is behind projection plane but the math works.
      self.bg_objects.append( Rock( random.randint( 30, MAX_WORLD_X ), 0, z ) )

    # Grass
    for z in range( 25, 40, 1 ):
      self.bg_objects.append( Grass( random.randint( 20, MAX_WORLD_X ), 0, z ) )

    # Trees
    for z in range( 40, 500, 20 ):
      self.bg_objects.append( Tree( random.randint( 20, MAX_WORLD_X ), 0, z ) )

    # Base - active, update replenishes resources
    self.objects.append( Base( 0, 0, 2, label="Base" ) )

    # Create the Chopper
    self.chopper = Helicopter( 0, 0, 1 )
    self.objects.append( self.chopper )

    buildCity( self, MIN_WORLD_X, NUM_CITY_BUILDINGS )
    buildEBase( self, MAX_WORLD_X / 2, NUM_E_BASE_BUILDINGS + self.level * 2 )

    self.objects.append( GameManager( self ) )

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

  # Q's a status message to be displayed at the center of the screen.
  def addStatusMessage( self, m, time=50 ):
    self.statusMessages.insert( 0, ( m, time ) ) # list contains (string,time) tuples. Newest to head, pull from end

  def gameOver( self ):
    self.addStatusMessage( "Game Over Man", time=200 )
    self.newGameTimer = 300

  def update( self ):
    self.time += 1

    if self.newGameTimer > 0:
      self.newGameTimer -= 1
      if self.newGameTimer == 0:
        self.newGame()
        return

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
    tgtCamXOff = [ -30, 30, 0 ][ self.chopper.chopperDir ]

    if( self.currentCamOff - tgtCamXOff ) < 1 and ( self.currentCamOff - tgtCamXOff ) > -1:
      self.currentCamOff = tgtCamXOff
      self.cameraOnHelo = True
    elif self.currentCamOff < tgtCamXOff:
      self.currentCamOff += 1
    elif self.currentCamOff > tgtCamXOff:
      self.currentCamOff -= 1

    self.camera.x = self.chopper.p.x + self.currentCamOff
    if self.camera.x < MIN_WORLD_X:
      self.camera.x = MIN_WORLD_X
    elif self.camera.x > MAX_WORLD_X:
      self.camera.x = MAX_WORLD_X

    self.camera.y = ( self.chopper.p.y - 20 ) if self.chopper.p.y > 40 else 20

    while self.msgQ:
      m = self.msgQ.pop()
      self.__processMessage__( m[ 0 ], m[ 1 ] )

  def draw( self ):
    SCREEN_PAD = 500

    self.canvas.delete( ALL )
    for o in self.bg_objects:
      p = projection( self.camera, o.p )
      if p.x < SCREEN_WIDTH + SCREEN_PAD and p.x > -SCREEN_PAD:
        o.draw( self, p )
        if self.debugCoords:
          e.canvas.create_rectangle( p.x - 1, p.y - 1, p.x + 1, p.y + 1, outline="red" )
    for o in self.objects:
      p = projection( self.camera, o.p )
      if p.x < SCREEN_WIDTH + SCREEN_PAD and p.x > -SCREEN_PAD:
        o.draw( self, p )
        if self.debugCoords:
          e.canvas.create_rectangle( p.x - 1, p.y - 1, p.x + 1, p.y + 1, outline="red" )
          displayColRect( e, o )

    if not self.showDirections:
      if self.statusMsgTime > 0:
        self.statusMsgTime -= 1
        e.canvas.create_text( SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3,
                              text=self.statusMsgCurrent, fill='red',
                              font=tkFont.Font( family='Helvetica', size=28, weight='bold' ) )
      elif self.statusMessages:
        m = self.statusMessages.pop()
        self.statusMsgCurrent = m[ 0 ]
        self.statusMsgTime = m[ 1 ]

    t = "%s" % self.score
    e.canvas.create_text( SCREEN_WIDTH / 2, 10, text=t )
    t = "High Score %s" % self.highScore
    e.canvas.create_text( SCREEN_WIDTH / 2, 25, text=t )

    if self.fadeInCount < SCREEN_HEIGHT / 2:
      self.fadeInCount += 20
      e.canvas.create_rectangle( 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT / 2 - self.fadeInCount, fill="black" )
      e.canvas.create_rectangle( 0, SCREEN_HEIGHT / 2 + self.fadeInCount, SCREEN_WIDTH, SCREEN_HEIGHT, fill="black" )

    if self.showDirections:
      self.displayDirections()
    self.root.update()

  def displayDirections( self ):

    directions = ( "Chopper",
                   "",
                   "up/down/left/right - move chopper",
                   "a : Small Missile",
                   "s : Large Missile",
                   "z : Bomb",
                   "sp : Bullet",
                   "e/d : Gun up/down",
                   "? : This screen",
                   "",
                   "Finish level by destroying all enemies and returning to base.",
                   "Refuel by landing at base",
                   "Game ends if you lose all choppers, finish all %s levels, or the city is destroyed" % NUM_LEVELS,
                   "",
                   "Press <Space>" )

    for l in range( 0, len( directions ) ):
      e.canvas.create_text( SCREEN_WIDTH / 2, 50 + 20 * l, text=directions[ l ],
                            font=tkFont.Font( family='Helvetica', size=20, weight='bold' ) )

def leftHandler( event ):
  e.qMessage( MSG_UI, MSG_ACCEL_L )
def rightHandler( event ):
  e.qMessage( MSG_UI, MSG_ACCEL_R )
def upHandler( event ):
  e.qMessage( MSG_UI, MSG_ACCEL_U )
def downHandler( event ):
  e.qMessage( MSG_UI, MSG_ACCEL_D )

def keyHandler( event ):
  e.showDirections = False

  if event.char == "a":
    e.qMessage( MSG_UI, MSG_WEAPON_MISSILE_S )
  elif event.char == "s":
    e.qMessage( MSG_UI, MSG_WEAPON_MISSILE_L )
  elif event.char == "z":
    e.qMessage( MSG_UI, MSG_WEAPON_BOMB )
  elif event.char == "e":
    e.qMessage( MSG_UI, MSG_GUN_UP )
  elif event.char == "d":
    e.qMessage( MSG_UI, MSG_GUN_DOWN )
  elif event.char == " ":
    e.qMessage( MSG_UI, MSG_WEAPON_BULLET )
  elif event.char == "?":
    e.showDirections = True

# Main
e = displayEngine()

e.root.bind( "<Left>",  leftHandler )
e.root.bind( "<Right>", rightHandler )
e.root.bind( "<Up>",    upHandler )
e.root.bind( "<Down>",  downHandler )
e.root.bind( "<Key>",   keyHandler )

e.update() # do once initially, then wait until user presses space to clear the instructions screen
while True:
  e.draw()
  if not e.showDirections:
    e.update()
  time.sleep( .01 )

