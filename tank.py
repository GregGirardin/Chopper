import constants
import math, random
from utils import *
from Tkinter import *
from PIL import ImageTk, Image
from explosions import *
from missiles import *

# Tank operational states
TANK_STATE_MOVE_TO_ATK = 0  # go to building
TANK_STATE_ATK_CHOPPER = 1     # Helo present. Engage
TANK_STATE_SHELLING = 2     # in position
TANK_STATE_RELOAD = 3       # out of weapons, go back to reload.
TANK_STATE_IDLE = 4

class Tank():
  tankImages = []
  cannonImages = []
  cannonAngles = [ 0, .175, .40, .55 ] # Canon has 4 positions

  def __init__( self, p, v=None ):
    self.oType = OBJECT_TYPE_TANK
    self.v = v if v else Vector( PI, TANK_DELTA )
    self.p = Point( p.x, p.y, p.z )
    self.cannonAngle = 0 # 0 - 3
    self.colRect = ( -4, 4, 4, 0 )
    self.si = SI_TANK
    self.siMax = SI_TANK
    self.points = POINTS_TANK
    self.showSICount = 0
    self.state = TANK_STATE_MOVE_TO_ATK
    self.shells = TANK_SHELLS
    self.delayCount = 0 # general delay counter
    self.direction = DIRECTION_LEFT

    if len( Tank.tankImages ) == 0:
      img = Image.open( "images/vehicles/Tank.gif" )
      SW = 256
      SH = 128
      for x in range( 0, 2 ):
        crop = img.crop( ( x * SW, 0, x * SW + SW, SH ) )
        crop = crop.resize( ( 192, 96 ) ) # 3/4 scale

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
          crop = crop.resize( ( 96 , 48 ) )

          crop = ImageTk.PhotoImage( crop )
          images.append( crop )
        Tank.cannonImages.append( images )

    # 'Tractor points' of the caterpillar.
    # x,y coords of the points of the tractor. \___/
    self.tp = ( ( ( -56, -11 ), ( -45, 0 ), (  45, 0 ), (  67, -17 ) ),
                ( (  56, -11 ), (  45, 0 ), ( -45, 0 ), ( -67, -17 ) ) )
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
      self.showSICount = SHOW_SI_COUNT
      if param.oType == OBJECT_TYPE_WEAPON:
        self.si -= param.wDamage
        if self.si < 0:
          e.addObject( Explosion( self.p ) )

  def update( self, e ):
    if self.si < 0:
      e.qMessage( MSG_ENEMY_LEFT_BATTLEFIELD, self )
      return False

    # Behavior / AI
    if e.time % 10 == 0: # Don't need to do this every update..
      if self.state == TANK_STATE_MOVE_TO_ATK:
        dis = distanceToObjectType( e, self.p.x, OBJECT_TYPE_BUILDING )
        if not dis: # No more city buildings ? attack the chopper
          self.state = TANK_STATE_ATK_CHOPPER
        else:
          if dis > 25:
            self.v = Vector( 0, TANK_DELTA )
          elif dis < -25:
            self.v = Vector( PI, TANK_DELTA )
          else:
            self.state = TANK_STATE_SHELLING

      elif self.state == TANK_STATE_SHELLING:
        self.v = Vector( 0, 0 )
        if self.shells == 0:
          self.state = TANK_STATE_RELOAD
        else:
          if self.delayCount <= 0:
            self.delayCount = 3
            self.shells -= 1
            self.cannonAngle = 0
            angle = Tank.cannonAngles[ self.cannonAngle ]

            if self.direction == DIRECTION_RIGHT:
              e.addObject( Bullet( Point( self.p.x + 5, self.p.y + 2, self.p.z ),
                                   Vector( angle, BULLET_DELTA ),
                                   oType=OBJECT_TYPE_E_WEAPON, wDamage=10 ) )
            else:
              e.addObject( Bullet( Point( self.p.x - 5, self.p.y + 2, self.p.z ),
                                   Vector( ( PI - angle ), BULLET_DELTA ),
                                   oType=OBJECT_TYPE_E_WEAPON, wDamage=10 ) )
            self.state = TANK_STATE_MOVE_TO_ATK
          else:
            self.delayCount -= 1

      elif self.state == TANK_STATE_RELOAD:
        dis = distanceToObjectType( e, self.p.x, OBJECT_TYPE_E_BUILDING )
        if not dis: # No more buildings to reload at.
          self.state = TANK_STATE_ATK_CHOPPER
        else:
          if dis > 5:
            self.v = Vector( 0, TANK_DELTA )
          elif dis < -5:
            self.v = Vector( PI, TANK_DELTA )
          else:
            self.shells = TANK_SHELLS # reloaded
            self.state = TANK_STATE_MOVE_TO_ATK

      elif self.state == TANK_STATE_ATK_CHOPPER:
        if self.shells == 0:
          self.state = TANK_STATE_RELOAD

        dis = e.chopper.p.x - self.p.x
        if dis > 50:
          self.v = Vector( 0, TANK_DELTA )
        elif dis < -50:
          self.v = Vector( PI, TANK_DELTA )
        else:  # Chopper isn't too far. Determine angle and shoot.
          self.v = Vector( 0, 0 )
          theta = vec_dir( math.fabs( dis ), e.chopper.p.y )
          if theta > Tank.cannonAngles[ 3 ]:
            self.cannonAngle = 3
          elif theta > Tank.cannonAngles[ 2 ]:
            self.cannonAngle = 2
          elif theta > Tank.cannonAngles[ 1 ]:
            self.cannonAngle = 1
          else:
            self.cannonAngle = 0

          self.direction = DIRECTION_RIGHT if dis > 0 else DIRECTION_LEFT

          angle = Tank.cannonAngles[ self.cannonAngle ]
          yOff = [ 2.5, 3, 4, 4 ][ self.cannonAngle ]

          if self.delayCount <= 0:
            self.delayCount = 5
            self.shells -= 1

            if self.direction == DIRECTION_RIGHT:
              e.addObject( Bullet( Point( self.p.x + 6, self.p.y + yOff, self.p.z ),
                                   Vector( angle, BULLET_DELTA ),
                                   oType=OBJECT_TYPE_E_WEAPON,
                                   wDamage=10 ) )
            else:
              e.addObject( Bullet( Point( self.p.x - 6, self.p.y + yOff, self.p.z ),
                                   Vector( ( PI - angle ), BULLET_DELTA ),
                                   oType=OBJECT_TYPE_E_WEAPON,
                                   wDamage=10 ) )
          else:
            self.delayCount -= 1

      elif self.state == TANK_STATE_IDLE:
        self.v = Vector( 0, 0 )
        # No buildings or buildings to get more shells

    if self.v.magnitude > .01: # if not moving don't change direction
      if self.v.dx() > 0:
        self.direction = DIRECTION_RIGHT
      else:
        self.direction = DIRECTION_LEFT

    self.p.move( self.v )
    return True

  def draw( self, e, p ):
    of = [ [ 0, -45, -82, -52 ], # Display offsets so 0,0 is bottom center
           [ 0, -45,  82, -52 ] ]

    d = self.direction

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
    TREAD_DISTANCE = 15.0

    if d == DIRECTION_LEFT:
      treadDistance = float( ( 1000 - self.p.x * 15 ) % TREAD_DISTANCE ) # The distance along the segment. Move the start to animate
    else:
      treadDistance = float( ( self.p.x * 15 % TREAD_DISTANCE ) )

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

    showSI( e.canvas, p, self )