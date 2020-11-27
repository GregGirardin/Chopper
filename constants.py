SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800

PI = 3.14159

# Think of these in terms of meters maybe
MIN_WORLD_X = -50
MAX_WORLD_X = 3000

BASE_DISTANCE = 500

HORIZON_DISTANCE = 10000

MAX_MTN_WIDTH = 1000
MAX_MTN_HEIGHT = 200
MAX_MTN_DISTANCE = HORIZON_DISTANCE / 4
MTN_PER_LAYER = 20

CAM_FOV_X = 45.0/360.0 * 6.28
CAM_FOV_Y = 30.0/360.0 * 6.28
CAM_Z = 100 # Distance behind projection plane, NOTE: should be negative in theory.

# Helo stuff
ROTOR_STOP = 0
ROTOR_SLOW = 1
ROTOR_FAST = 2

MAX_ALTITUDE = 100
DISPLAY_CONTROL_TIME = 30 # How may frames to display the control "stick" position after movement

# What's the desired X velocity? We have to accelerate to it.
TGT_VEL_STOP       =  0 # facing fwd
TGT_VEL_LEFT_STOP  = -1 # stopped facing left
TGT_VEL_LEFT_SLOW  = -2
TGT_VEL_LEFT_FAST  = -3
TGT_VEL_RIGHT_STOP =  1
TGT_VEL_RIGHT_SLOW =  2
TGT_VEL_RIGHT_FAST =  3

# What's the desired Y velocity
TGT_VEL_UP_SLOW = 1
TGT_VEL_UP_FAST = 2
TGT_VEL_DN_SLOW = -1
TGT_VEL_DN_FAST = -2

# Chopper body angle
ANGLE_0   = 0 # level
ANGLE_U5  = 1 # Up 5 degrees for slowing down
ANGLE_D5  = 2 # Down 5
ANGLE_D10 = 3 # Down 10

WEAPON_NONE = 0
WEAPON_SMALL_MISSILE = 1
WEAPON_LARGE_MISSILE = 2
WEAPON_BOMB = 3
WEAPON_BULLET = 4

# Messages to objects

# From user
MSG_ACCEL_L = 0
MSG_ACCEL_R = 1
MSG_ACCEL_U = 2
MSG_ACCEL_D = 3
MSG_WEAPON_MISSILE_S = 4
MSG_WEAPON_MISSILE_L = 5
MSG_WEAPON_BOMB = 6
MSG_WEAPON_BULLET = 7
MSG_GUN_UP = 10
MSG_GUN_DOWN = 11

MSG_COLLISION_DET = 20 # Collision detected

DIRECTION_LEFT    = 0
DIRECTION_RIGHT   = 1
DIRECTION_FORWARD = 2

# Movement per update
TANK_DELTA = .2
CHOPPER_V_DELTA = .02
JEEP_DELTA = .4
TRUCK_DELTA = .4
TRANSPORT1_DELTA = .2
TRANSPORT2_DELTA = .2

BOMBER_DELTA = .8
FIGHTER_DELTA = 1.2

# Active object types
OBJECT_TYPE_NONE        =  0
OBJECT_TYPE_BASE        =  1
OBJECT_TYPE_CHOPPER     =  2
OBJECT_TYPE_JEEP        =  3
OBJECT_TYPE_TRANSPORT1  =  4
OBJECT_TYPE_TRANSPORT2  =  5
OBJECT_TYPE_TRUCK       =  6
OBJECT_TYPE_JET         =  7
OBJECT_TYPE_TANK        =  8
OBJECT_TYPE_WEAPON      =  9 # Weapon I fired
OBJECT_TYPE_E_WEAPON    = 10 # Weapon enemy fired
OBJECT_TYPE_EBASE       = 11 # Enemy base

OBJECT_TYPE_MGR         = 99

# Game objectives
MISSION_BASEII = 0
MISSION_BASEIII = 1

# weapon damage
WEAPON_DAMAGE_BULLET    = 1
WEAPON_DAMAGE_MISSLE_S  = 10
WEAPON_DAMAGE_MISSLE_L  = 30
WEAPON_DAMAGE_BOMB      = 100

# Initial structural integrity
SI_CHOPPER    = 100
SI_JEEP       = 10
SI_TRANSPORT1 = 15
SI_TRANSPORT2 = 15
SI_TRUCK      = 15
SI_TANK       = 50
SI_BOMBER     = 40
SI_BOMBER2    = 80
SI_FIGHTER    = 10