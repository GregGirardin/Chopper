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
It spawns enemies based on time and progress
'''
class GameManager():
  def __init__( self ):
    # AI may be treated as just another world object, so it needs a few things it doesn't use.
    self.oType = OBJECT_TYPE_MGR
    self.p = Point( 0, 0, 0 )
    self.colRect = ( 0, 0, 0, 0 )
    self.e = None
    self.timeToNextEnemy = 100

  def processMessage( self, e, message, param=None ):
    pass

  def update( self, e ):

    self.timeToNextEnemy -= 1

    if self.timeToNextEnemy == 0:
      self.timeToNextEnemy = random.randint( 200, 1000 )

      choice = random.randint( 0, 50 )

      # Always spawn enemies to the right of the chopper.
      if choice < 20:
        e.addObject( Jeep( Point( e.chopper.p.x + 100, 0, 0 ), DIRECTION_LEFT ) )
      elif choice < 25:
        e.addObject( Tank( Point( e.chopper.p.x + 100, 0, 0 ), DIRECTION_LEFT ) )
      elif choice < 35:
        e.addObject( Bomber( Point( e.chopper.p.x + 100, random.randint( 10, 25 ), 0 ), DIRECTION_LEFT ) )
      elif choice < 45:
        e.addObject( Bomber2( Point( e.chopper.p.x + 100, random.randint( 10, 25 ), 0 ), DIRECTION_LEFT ) )
      elif choice < 50:
        e.addObject( Fighter( Point( e.chopper.p.x + 500, random.randint( 10, 25 ), 0 ), DIRECTION_LEFT ) )

    return True

  def draw( self, e ): # Nothing to draw, create method if we put it in objects[]
    pass