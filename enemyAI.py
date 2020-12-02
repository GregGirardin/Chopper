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
import random

'''
This gets called every loop and keeps track of game progress.
It spawns enemies based on time and progress.
Could do an AI if we ever want a sort of "general" to manage aggregate enemy behavior.
'''
class GameManager():
  def __init__( self, e ):
    # AI may be treated as just another world object, so it needs a few things it doesn't use.
    self.oType = OBJECT_TYPE_MGR
    self.p = Point( 0, 0, 0 )
    self.colRect = ( 0, 0, 0, 0 )
    self.e = e
    self.timeToNextEnemy = 100
    self.totalEnemies = 5 * e.level # tbd

  def processMessage( self, e, message, param=None ):
    pass

  def update( self, e ):
    if e.time == 10:
      if e.level == 1:
        e.addStatusMessage( "Defend the city" )
        e.addStatusMessage( "Destroy enemy buildings ->" )
      e.addStatusMessage( "Level " + str( e.level ) )

    '''
    # Debug stuff
    self.bg_objects.append( City( MIN_WORLD_X - 20, 0, 0 ) )
    self.objects.append( Bomber( Point ( -20, 20, 0 ), DIRECTION_LEFT ) )
    self.objects.append( Transporter( Point ( 0, 20, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Tank( Point(  10, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Transport1( Point(  -10, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Transport2( Point(  10, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( Truck( Point(  30, 0, 0 ), DIRECTION_RIGHT ) )
    self.objects.append( dbgPoint( Point(  0, 0, 0 ) ) )
    '''
    self.timeToNextEnemy -= 1

    if self.timeToNextEnemy == 0:
      self.timeToNextEnemy = random.randint( 100, 200 )
      self.totalEnemies -= 1

      # Spawn enemies to the right of the chopper.
      choice = random.randint( 0, 9 )
      if choice == 0:
        e.addObject( Bomber( Point( e.chopper.p.x + 100, random.randint( 10, 25 ), 0 ), DIRECTION_LEFT ) )
      elif choice == 1:
        e.addObject( Bomber2( Point( e.chopper.p.x + 500, random.randint( 10, 25 ), 0 ), DIRECTION_LEFT ) )
      elif choice == 2:
        e.addObject( Fighter( Point( e.chopper.p.x + 500, random.randint( 10, 25 ), 0 ), DIRECTION_LEFT ) )
      elif choice == 3:
        e.addObject( Tank( Point( e.chopper.p.x + 100, 0, 0 ), DIRECTION_LEFT ) )
      elif choice == 4:
        e.addObject( Transport1( Point( e.chopper.p.x + 100, 0, 0 ), DIRECTION_LEFT ) )
      elif choice == 5:
        e.addObject( Transport2( Point( e.chopper.p.x + 100, 0, 0 ), DIRECTION_LEFT ) )
      elif choice == 6:
        e.addObject( Truck( Point( e.chopper.p.x + 100, 0, 0 ), DIRECTION_LEFT ) )
      else: # default to Jeep
        e.addObject( Jeep( Point( e.chopper.p.x + 100, 0, 0 ), DIRECTION_LEFT ) )

    if self.totalEnemies == 0:
      e.qMessage( MSG_SPAWNING_COMPLETE, self )
      return False

    return True

  def draw( self, e, p ): # Nothing to draw, create method if we put it in objects[]
    pass