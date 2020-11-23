import constants
import math, random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image

class Tank():
  tankImages = []
  cannonImages = []

  def __init__( self, p, d=DIRECTION_RIGHT ):
    self.time = 0
    self.bounceCount = 0
    self.d = d
    self.p = Point( p.x, p.y, p.z )

    if len( Tank.tankImages ) == 0:
      img = Image.open( "images/vehicles/Tank.gif" ) # 256x128 rectangular sprites
      SW = 256
      SH = 128
      for x in range( 0, 2 ): # Right and Left
        crop = img.crop( ( x * SW, 0, x * SW + SW, SH ) )
        Tank.tankImages.append( ImageTk.PhotoImage( crop ) )

      images = []
      img2 = img.crop( ( 2 * SW, 0, 3 * SW, SH ) )
      for y in range( 0, 2 ):
        for x in range( 0, 2 ):
          crop = img2.crop( ( x * SW/2, y * SH/2, x * SW/2 + SW/2, y * SH/2 + SH/2 ) )
          crop = ImageTk.PhotoImage( crop )
          images.append( crop )
      Tank.cannonImages.append( images )

      images = []
      img2 = img.crop( ( 3 * SW, 0, 4 * SW, SH ) )
      for y in range( 0, 2 ):
        for x in range( 1, -1, -1 ):
          crop = img2.crop( ( x * SW/2, y * SH/2, x * SW/2 + SW/2, y * SH/2 + SH/2 ) )
          crop = ImageTk.PhotoImage( crop )
          images.append( crop )
      Tank.cannonImages.append( images )

  def update( self, e ):
    self.time += 1
    if self.time > 1000:
      return False

    if not self.bounceCount:
      if random.randint( 0, 20 ) == 0: # Bounce occasionally, angle up / level / angle down / level
        self.bounceCount = 4

    self.imgIx = 0 # level

    if self.bounceCount:
      if self.bounceCount > 2:
        self.imgIx = 2 # angle up sprite
      elif self.bounceCount == 2:
        self.imgIx = 0 # level again
      elif self.bounceCount == 1:
        self.imgIx = 1 # angle down
      self.bounceCount -= 1

    if self.d == DIRECTION_LEFT:
      self.p.x -= TANK_DELTA
    else:
      self.p.x += TANK_DELTA

    return True

  def draw( self, e ):
    proj = projection( e.camera, self.p )

    if self.d == DIRECTION_RIGHT:
      e.canvas.create_image( proj.x + 20,  proj.y - 45, image=Tank.tankImages[ 0 ] )
      e.canvas.create_image( proj.x + 110, proj.y - 70, image=Tank.cannonImages[ 0 ][ 2 ] )
    else:
      e.canvas.create_image( proj.x + 5,   proj.y - 45, image=Tank.tankImages[ 1 ] )
      e.canvas.create_image( proj.x - 110, proj.y - 80, image=Tank.cannonImages[ 1 ][ 2 ] )

      # e.canvas.create_rectangle( proj.x, proj.y - 5, proj.x, proj.y, outline="red" )