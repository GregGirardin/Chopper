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
    self.totalEnemies = 5 * e.level

  def processMessage( self, e, message, param=None ):
    pass

  def update( self, e ):
    if e.time == 10:
      if e.level == 1:
        e.addStatusMessage( "Defend the city" )
        e.addStatusMessage( "Destroy enemy buildings ->" )
      e.addStatusMessage( "Level " + str( e.level ) )

      for tank in range( 0, e.level ):
        e.addObject( Tank( Point( MAX_WORLD_X / 2 + tank * 10, 0, 0 ), DIRECTION_LEFT ) )

    self.timeToNextEnemy -= 1

    if self.timeToNextEnemy == 0:
      self.timeToNextEnemy = random.randint( 50, 200 )
      self.totalEnemies -= 1

      # Spawn enemies to the right of the chopper
      spX = e.chopper.p.x + 100
      spY = random.randint( 10, 25 )

      if e.cityDestroyed:
        choice = 2 + random.randint( 0, 2 ) # Fighter or Tank can attack the chopper
      else:
        choice = random.randint( 0, 9 )
      if choice == 0:
        e.addObject( Bomber1( Point( spX, spY, 0 ), DIRECTION_LEFT ) )
      elif choice == 1:
        e.addObject( Bomber2( Point( spX, spY, 0 ), DIRECTION_LEFT ) )
      elif choice == 2:
        e.addObject( Fighter( Point( spX, spY, 0 ), DIRECTION_LEFT ) )
      elif choice == 3:
        e.addObject( Tank( Point( spX, 0, 0 ), DIRECTION_LEFT ) )
      elif choice == 4:
        e.addObject( Transport1( Point( spX, 0, 0 ), DIRECTION_LEFT ) )
      elif choice == 5:
        e.addObject( Transport2( Point( spX, 0, 0 ), DIRECTION_LEFT ) )
      elif choice == 6:
        e.addObject( Truck( Point( spX, 0, 0 ), DIRECTION_LEFT ) )
      else: # default to Jeep
        e.addObject( Jeep( Point( spX, 0, 0 ), DIRECTION_LEFT ) )
      if self.totalEnemies == 0:
        e.qMessage( MSG_SPAWNING_COMPLETE, self )
        return False
    return True

  def draw( self, e, p ): # Nothing to draw, create method if we put it in objects[]
    pass