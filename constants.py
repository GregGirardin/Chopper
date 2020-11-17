SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

PI = 3.14159

# Think of these in terms of meters.
MIN_WORLD_X = -10000
MAX_WORLD_X = 10000

HORIZON_DISTANCE = 10000

MAX_MTN_WIDTH = 1000
MAX_MTN_HEIGHT = 200
MAX_MTN_DISTANCE = HORIZON_DISTANCE / 4
MTN_PER_LAYER = 20

CAM_FOV_X = 45.0/360.0 * 6.28
CAM_FOV_Y = 30.0/360.0 * 6.28
CAM_Z = 100 # Distance behind proj plane, NOTE: should be negative in theory.

ROTOR_STOP = 0
ROTOR_SLOW = 1
ROTOR_FAST = 2

MAX_ALTITUDE = 45

# What's the desired velocity? We have to accelerate to it.
TGT_VEL_STOP       =  0
TGT_VEL_LEFT_STOP  = -1 # stopped facing left
TGT_VEL_LEFT_SLOW  = -2
TGT_VEL_LEFT_FAST  = -3
TGT_VEL_RIGHT_STOP =  1
TGT_VEL_RIGHT_SLOW =  2
TGT_VEL_RIGHT_FAST =  3

DIRECTION_LEFT    = 0 # Chopper direction
DIRECTION_RIGHT   = 1
DIRECTION_FORWARD = 2

ANGLE_0   = 0 # Chopper angle
ANGLE_U5  = 1
ANGLE_D5  = 2
ANGLE_D10 = 3