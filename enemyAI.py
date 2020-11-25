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

'''
This gets called every loop and keeps track of game progress.
It spawns enemies based on time and progress
'''

class GameManager():
  def __init__( self ):
    # AI may be treated as just another world object, so it needs a few things it doesn't use.
    self.oType = OBJECT_TYPE_MGR
    self.time = 0
    self.p = Point( 0, 0, 0 )
    self.colRect = ( 0, 0, 0, 0 )
    self.e = None

    self.missions = [ False, False, False, ]

  def processMessage( self, e,  message, param=None ):
    pass

  def update( self, e ):
    self.e = e # keep a reference to the engine.

    self.time += 1

    if self.time == 1: # spawn
      self.e.addObject( Jeep( Point( 200, 0, 0 ), DIRECTION_LEFT ) )
      print "spawing Jeep"

    return True

  def draw( self, e ): # Nothing to draw, create method if we put it in objects[]
    pass