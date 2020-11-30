import constants
import math, random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image
from explosions import *

class Tank():
  tankImages = []
  cannonImages = []

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_TANK
    self.time = 0
    self.v = v if v else Vector( PI, TANK_DELTA )
    self.p = Point( p.x, p.y, p.z )
    self.cannonAngle = 3 # 0 - 3
    self.colRect = ( -4, 4, 4, 0 )
    self.si = SI_TANK
    self.points = POINTS_TANK

    if len( Tank.tankImages ) == 0:
      img = Image.open( "images/vehicles/Tank.gif" ) # 256x128 rectangular sprites
      SW = 256
      SH = 128
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, SH ) )
        Tank.tankImages.append( ImageTk.PhotoImage( crop ) )

      coords = ( ( ( 1, 0 ), ( 0, 0 ), ( 1, 1 ), ( 1, 1 ) ),
                 ( ( 0, 0 ), ( 0, 1 ), ( 1, 0 ), ( 1, 1 ) ) )  # x,y of increasing cannon angle due to the gif

      for cd in ( DIRECTION_LEFT, DIRECTION_RIGHT ): # canon direction
        img2 = img.crop( ( ( cd + 2 ) * SW, 0, ( cd + 3 ) * SW, SH ) )
        images = []
        for c in coords[ cd ]: # c is an (x,y) tuple
          crop = img2.crop( ( c[ 0 ] * SW / 2 + 5, # the 5 is a hack because of cruft at the edges
                              c[ 1 ] * SH / 2 + 5,
                              c[ 0 ] * SW / 2 + SW / 2 - 5,
                              c[ 1 ] * SH / 2 + SH / 2 - 5 ) )
          crop = ImageTk.PhotoImage( crop )
          images.append( crop )
        Tank.cannonImages.append( images )

    # 'Tractor points' of the caterpillar.
    # x,y coords of the points of the tractor. \___/
    self.tp = ( ( ( -75, -15 ), ( -60, 0 ), (  60, 0 ), (  90, -23 ) ),
                ( (  75, -15 ), (  60, 0 ), ( -60, 0 ), ( -90, -23 ) ) )
    self.tpDis = [] # lenghts of the 3 segments for use while drawing the tractor.
    for pts in self.tp:
      lenList = []
      totLen = 0
      for l in range( 0, 3 ):
        segLen = distance( pts[ l ][ 0 ], pts[ l ][ 1 ], pts[ l + 1 ][ 0 ], pts[ l + 1 ][ 1 ] )
        totLen += segLen
        lenList.append( segLen )
      self.tpDis.append( lenList )

  def processMessage( self, e, message, param=None ):
    if message == MSG_COLLISION_DET:
      if param.oType == OBJECT_TYPE_WEAPON:
        self.si -= param.wDamage
        if self.si < 0:
          e.addObject( BombExplosion( Point( self.p.x, self.p.y, self.p.z ) ) )

  def update( self, e ):
    if self.si < 0:
      e.qMessage( MSG_ENEMY_DESTROYED, self )
      return False

    self.p.move( self.v )

    if self.p.x < MIN_WORLD_X or self.p.x > MAX_WORLD_X:
      self.v.flipx()

    return True

  def draw( self, e, p ):
    of = [ [ 0, -60, -110, -70 ], # Display offsets so 0,0 is bottom center
           [ 0, -60,  110, -70 ] ]

    d = DIRECTION_LEFT if self.v.dx() < 0.0 else DIRECTION_RIGHT

    e.canvas.create_image( p.x + of[ d ][ 0 ], p.y + of[ d ][ 1 ], image=Tank.tankImages[ d ] )
    e.canvas.create_image( p.x + of[ d ][ 2 ], p.y + of[ d ][ 3 ], image=Tank.cannonImages[ d ][ self.cannonAngle ] )
    # Draw tractor. 3 segments.
    for l in range( 0, 3 ):
      e.canvas.create_line( p.x + self.tp[ d ][     l ][ 0 ],
                            p.y + self.tp[ d ][     l ][ 1 ],
                            p.x + self.tp[ d ][ l + 1 ][ 0 ],
                            p.y + self.tp[ d ][ l + 1 ][ 1 ],
                            fill="black", width=3 )
    # Draw the treads. They go from one line segment to the next as though they are contiguous.
    TREAD_DISTANCE = 20.0

    if d == DIRECTION_LEFT:
      treadDistance = float( ( 1000 - self.p.x * 20 ) % TREAD_DISTANCE ) # The distance along the segment. Move the start to animate
    else:
      treadDistance = float( ( self.p.x * 20 % TREAD_DISTANCE ) )

    segment = 0 # Track has 3 segments: \_/
    while segment < 3:
      x, y = pointAlong( self.tp[ d ][ segment     ][ 0 ],
                         self.tp[ d ][ segment     ][ 1 ],
                         self.tp[ d ][ segment + 1 ][ 0 ],
                         self.tp[ d ][ segment + 1 ][ 1 ],
                         treadDistance )
      e.canvas.create_rectangle( p.x + x, p.y + y, p.x + x + 3, p.y + y + 3, fill="#111" )
      treadDistance += TREAD_DISTANCE
      if treadDistance > self.tpDis[ d ][ segment ]:
        treadDistance -= self.tpDis[ d ][ segment ]  # now treadDistance is the first point along the next segment
        segment += 1