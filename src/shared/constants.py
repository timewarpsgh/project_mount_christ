import random

import sys

sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared\packets')
sys.path.append(r'D:\data\code\python\project_mount_christ\src\shared')

from enum import Enum, auto
import login_pb2 as pb
from helpers import Point


# seen grids
SEEN_GRIDS_COLS = 64
SEEN_GRIDS_ROWS = 32
SIZE_OF_ONE_GRID = 33.75 # WORLD_MAP_ROWS/SEEN_GRIDS_ROWS (1080/32)

BATTLE_TIMER_IN_SECONDS = 8
MOVE_TIMER_IN_PORT = 0.1
FRAME_RATE = 360
PORT_SPEED = 80
NPC_SPEED = 20
DEAD_SPEED = 80 #5

############## BATTLE CONFIGS ##############
STEPS_LEFT = 30

MAX_SHOOT_DISTANCE = 30#3    30
SHOOT_DAMAGE = 50 #50

MAX_ENGAGE_DISTANCE = 1.5#1.5  30
ENGAGE_TARGET_DAMAGE = 50 #200
ENGAGE_SELF_DAMAGE = 1

ENGAGE_DAMAGE = 0.5

#########################################################

NPC_ROLE_START_ID = 2_000_000_000
DYNAMIC_PORT_NPC_UPDATE_TIMER = 0.6
CREW_RECRUIT_COST = 50
SUPPLY_2_COST = {
    'food': 5,
    'water': 0,
    'material': 5,
    'cannon': 50,
}

INT_2_SUPPLY_NAME = {
    1: 'food',
    2: 'water',
    3: 'material',
    4: 'cannon',
}

SUPPLY_CONSUMPTION_INVERVAL = 5
SUPPLY_CONSUMPTION_PER_PERSON = 0.1
SEASON_CHANGE_INTERVAL = SUPPLY_CONSUMPTION_INVERVAL * 30 * 3
ONE_YEAR_INTERVAL = SEASON_CHANGE_INTERVAL * 4

# settings
DAEMON_MODE = False

SAVE_ON_CONNECTION_LOST = True
SET_ONLINE_TO_TRUE_ON_LOGIN = True
REMOTE_ON = True
DEVELOPER_MODE_ON = False
VERSION = 1.1

# in battle
THINK_TIME_IN_BATTLE = 30
MAX_STEPS_IN_BATTLE = 6


ESCAPE_DISTANCE = 20
BATTLE_MOVE_TIME_INVERVAL = 0.2
NEXT_SHIP_TIME_INVERVAL = 0.3

# world configurables
CAPTION = 'Uncharted Waters 2 Online'
FPS = 30.0
FONT_SIZE = 16
CREW_UNIT_COST = 100
SUPPLY_UNIT_COST = 5
ONE_DAY_AT_SEA_IN_SECONDS = 3
EXP_GOT_MODIFIER = 10
EXP_PER_DISCOVERY = 500
GOLD_REWARD_FOR_HANDING_IN_QUEST = 3000
MAX_LV = 60
PORTS_ALLIED_NATION_AND_PRICE_INDEX_CHANGE_INTERVAL_SECONDS = 60 * 120
MOVE_TIME_INVERVAL = 0.01
MAX_ITEMS_IN_BAG = 30

FLEET_COUNT_PER_NATION = 6
NATION_COUNT = 6
NPC_COUNT = 36

EIGHT_DIRECTIONS = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']
MAX_WIND_OR_WAVE = 5
WIND_WAVE_CHANGE_INTERVAL = 5
TIME_OF_DAY_OPTIONS = ['dawn', 'day', 'dusk', 'night']
PORT_COUNT = 130

DEFECT_COST = 200000
DEFECT_LV = 15
SUPPLY_LOW_ALERT_DAYS = 10
EACH_DAY_PASS = 1
SHIP_SPEED_CUT = 5
INVEST_MIN_INGOTS = 5

EASY_MODE_OVERIDE_RATIO = 2
HARD_MODE_OVERIDE_RATIO = 5

MAX_WORLD_MSG_TO_DISPLAY = 10

# tiles
WALKABLE_TILES = set(range(1, 40))
SAILABLE_TILES = set(range(1, 33))
WALKABLE_TILES_FOR_ASIA = set(range(1, 47))
PARTIAL_WORLD_MAP_TILES = 73
PARTIAL_WORLD_MAP_TILES_IN_ONE_DIRECTION = 36
PORT_TILES_COUNT = 96
GRID_TILES_COUNT = 13
CELL_TILES_COUNT = 13
TILES_AROUND_PORTS = [[2, 0], [2, 1], [2, -1], [-2, 0],
                      [-2, 1], [-2, -1],[0, 2], [1, 2],
                      [-1, 2], [0, -2], [1, -2], [-1, -2]]
THREE_NEARBY_TILES_OF_UP_LEFT_TILE = [[1, 0], [0, 1], [1, 1]]

WORLD_MAP_COLUMNS = 12 * 2 * 30 * 3 # 2160
WORLD_MAP_ROWS = 12 * 2 * 45 # 1080
WORLD_MAP_TILE_SIZE = 16
WORLD_MAP_X_LENGTH = WORLD_MAP_COLUMNS * WORLD_MAP_TILE_SIZE

WORLD_MAP_EDGE_LENGTH = 40

WORLD_MAP_MAX_Y_TO_DRAW_NEW_PARTIAL_WORLD_MAP = WORLD_MAP_TILE_SIZE * \
                                                (WORLD_MAP_ROWS - WORLD_MAP_EDGE_LENGTH)
WORLD_MAP_MIN_Y_TO_DRAW_NEW_PARTIAL_WORLD_MAP = WORLD_MAP_TILE_SIZE * WORLD_MAP_EDGE_LENGTH
WORLD_MAP_MIN_X_TO_DRAW_NEW_PARTIAL_WORLD_MAP = WORLD_MAP_TILE_SIZE * WORLD_MAP_EDGE_LENGTH
WORLD_MAP_MAX_X_TO_DRAW_NEW_PARTIAL_WORLD_MAP = WORLD_MAP_TILE_SIZE * \
                                                (WORLD_MAP_COLUMNS - WORLD_MAP_EDGE_LENGTH)

BATTLE_TILE_SIZE = 32
PORT_MAP_SIZE = 96 * 3
PORT_MAP_EDGE = 94
# pixels
WINDOW_WIDTH = 720
WINDOW_HEIGHT = 480

BUTTON_WIDTH, BUTTON_HIGHT = 60, 30
SELECTION_LIST_WIDTH, SELECTION_LIST_HIGHT = 225 , 250
SELECTION_LIST_X, SELECTION_LIST_Y = WINDOW_WIDTH - SELECTION_LIST_WIDTH, 120

HUD_WIDTH, HUD_HIGHT = 110, 400
BUILDING_PERSON_WIDTH, BUILDING_PERSON_HIGHT = 138, 114
BUILDING_CHAT_WIDTH, BUILDING_CHAT_HIGHT = 480, 129
BUILDING_BG_SIZE = 500
SHIP_SIZE_IN_PIXEL = 32
PERSON_SIZE_IN_PIXEL = 32
FIGURE_WIDTH = 65
FIGURE_HIGHT = 81
ITEMS_IMAGE_SIZE = 49
PIXELS_COVERED_EACH_MOVE = 16
SHIP_DOT_SIZE = 2

# IDs
DOG_FRAME_1_INDEX = 28
DOG_FRAME_2_INDEX = 29
DOG_BUILDING_ID = 2

OLD_MAN_FRAME_1_ID = 26
OLD_MAN_FRAME_2_ID = 27
OLD_MAN_BUILDING_ID = 5

AGENT_FRAME_1_ID = 24
AGENT_FRAME_2_ID = 25
AGENT_BUILDING_ID = 1

TAX_FREE_PERMIT_ID = 10
EXPENSIVE_EQUIPMENTS_IDS = {36, 37, 42, 43, 48}


# network
HOST = 'localhost'
PORT = 8082
REMOTE_HOST = '122.112.204.50'  #'175.27.138.5'
REMOTE_PORT = 8082
HEADER_SIZE = 4
OBJECT_SIZE = 4

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 69, 0)
CRIMSON = (139, 0, 0)
BLUE = (0,0,128)
TRANS_GRAY = (50, 50, 50, 35)
TRANS_BLANK = (0, 0, 0, 0)



ID_2_BUILDING_TYPE = {
    1: 'market',
    2: 'bar',
    3: 'dry_dock',
    4: 'harbor',
    5: 'inn',
    6: 'palace',
    7: 'job_house',
    8: 'msc',
    9: 'bank',
    10: 'item_shop',
    11: 'church',
    12: 'fortune_house',
}

class Building(Enum):
    MARKET = 1
    BAR = 2
    HARBOR = 4
    INN = 5


DIRECT_2_SEA_MOVE_COLLISION_TILES = {
    pb.DirType.N: [[-1, 0], [-1, 1]],
    pb.DirType.S: [[2, 0], [2, 1]],
    pb.DirType.E: [[0, 2], [1, 2]],
    pb.DirType.W: [[0, -1], [1, -1]],

    pb.DirType.NE: [[-1, 1], [-1, 2], [0, 2]],
    pb.DirType.NW: [[0, -1], [-1, -1], [-1, 0]],
    pb.DirType.SE: [[1, 2], [2, 2], [2, 1]],
    pb.DirType.SW: [[2, 0], [2, -1], [1, -1]],
}

NOW_DIRECT_2_ALTERNATIVE_DIRECTS = {
    pb.DirType.N: [pb.DirType.NE, pb.DirType.NW],
    pb.DirType.S: [pb.DirType.SE, pb.DirType.SW],
    pb.DirType.E: [pb.DirType.NE, pb.DirType.SE],
    pb.DirType.W: [pb.DirType.NW, pb.DirType.SW],

    pb.DirType.NE: [pb.DirType.N, pb.DirType.E],
    pb.DirType.NW: [pb.DirType.N, pb.DirType.W],
    pb.DirType.SE: [pb.DirType.S, pb.DirType.E],
    pb.DirType.SW: [pb.DirType.S, pb.DirType.W],
}

REGIONS = [
    'Europe',
    'New World',
    'West Africa',
    'East Africa',
    'Middle East',
    'India',
    'Southeast Asia',
    'Far East',
]

MARKETS =  [
    'Iberia',
    'Northern Europe',
    'The Mediterranean',
    'North Africa',
    'Ottoman Empire',
    'West Africa',
    'Central America',
    'South America',
    'East Africa',
    'Middle East',
    'India',
    'Southeast Asia',
    'Far East',
]

DIR_2_VECTOR = {
    pb.DirType.N: [Point(0, 0), Point(0, 1)],
    pb.DirType.S: [Point(0, 0), Point(0, -1)],
    pb.DirType.W: [Point(0, 0), Point(-1, 0)],
    pb.DirType.E: [Point(0, 0), Point(1, 0)],
    pb.DirType.NE: [Point(0, 0), Point(1, 1)],
    pb.DirType.SW: [Point(0, 0), Point(-1, -1)],
    pb.DirType.NW: [Point(0, 0), Point(-1, 1)],
    pb.DirType.SE: [Point(0, 0), Point(1, -1)]
}

STRATEGY_2_TEXT = {
    0: 'shoot',
    1: 'engage',
    2: 'flee',
    3: 'hold',
}

DIR_2_HEX_DIR = {
    0: 0,
    1: 1,
    3: 2,
    4: 3,
    5: 4,
    7: 5,
}

DIR_2_MOVE_MARKS_OFFSETS = {
    # left, right, current
    pb.DirType.N: [[-1, -0.5], [1, -0.5], [0, -1]],
    pb.DirType.S: [[1, 0.5], [-1, 0.5], [0, 1]],

    pb.DirType.NE: [[0, -1], [1, 0.5], [1, -0.5]],
    pb.DirType.SW: [[0, 1], [-1, -0.5], [-1, 0.5]],

    pb.DirType.SE: [[1, -0.5], [0, 1], [1, 0.5]],

    pb.DirType.NW: [[-1, 0.5], [0, -1], [-1, -0.5]]
}

INT_2_DUTY_NAME = {
    1: 'captain',
    2: 'chief navigator',
    3: 'accountant',
    4: 'first mate',
}

LV_2_MAX_XP = {
    1: 400,
    2: 900,
    3: 1400,
    4: 2100,
    5: 2800,
    6: 3600,
    7: 4500,
    8: 5400,
    9: 6500,
    10: 7600,
    11: 8700,
    12: 9800,
    13: 11000,
    14: 12300,
    15: 13600,
    16: 15000,
    17: 16400,
    18: 17800,
    19: 19300,
    20: 20800,
    21: 22400,
    22: 24000,
    23: 25500,
    24: 27200,
    25: 28900,
    26: 30500,
    27: 32200,
    28: 33900,
    29: 36300,
    30: 38800,
    31: 41600,
    32: 44600,
    33: 48000,
    34: 51400,
    35: 55000,
    36: 58700,
    37: 62400,
    38: 66200,
    39: 70200,
    40: 74300,
    41: 78500,
    42: 82800,
    43: 87100,
    44: 91500,
    45: 96000,
    46: 100600,
    47: 105200,
    48: 109800,
    49: 114500,
    50: 119200,
    51: 124000,
    52: 128800,
    53: 133700,
    54: 138700,
    55: 143700,
    56: 148800,
    57: 153900,
    58: 159100,
    59: 164400,
    60: 0  # Max level, no more XP needed
}

INT_2_SEASON = {
    1: 'spring',
    2: 'summer',
    3: 'fall',
    4: 'winter',
}

class Nation(Enum):
    ENGLAND = auto()
    NETHERLANDS = auto()
    SPAIN = auto()
    PORTUGAL = auto()
    ITALY = auto()
    OTTOMAN = auto()

class Capital(Enum):
    LONDON = 30
    AMSTERDAM = 34
    SEVILLE = 2
    LISBON = 1
    GENOA = 9
    ISTANBUL = 3

class Fleet(Enum):
    MERCHANT = auto()
    CONVOY = auto()
    BATTLE = auto()


PORT_ID_2_NATION = {
    Capital.LONDON.value: Nation.ENGLAND.value,
    Capital.AMSTERDAM.value: Nation.NETHERLANDS.value,
    Capital.SEVILLE.value: Nation.SPAIN.value,
    Capital.LISBON.value: Nation.PORTUGAL.value,
    Capital.GENOA.value: Nation.ITALY.value,
    Capital.ISTANBUL.value: Nation.OTTOMAN.value,
}

class Item(Enum):
    BALM = 1
    LIME_JUICE = 2
    RAT_POISON = 3

    TAX_FREE_PERMIT = 10
    LETTER_OF_MARQUE = 11

    QUADRANT = 4
    SEXTANT = 5
    THEODOLITE = 6

    TELESCOPE = 8

    CAT = 9

class ItemType(Enum):
    WEAPON = 'weapon'
    ARMOR = 'armor'
    CONSUMABLE = 'consumable'

class Aura(Enum):
    RATS = 1
    SCURVY = 2
    STORM = 3

    PRAYER = 4
    DONATION = 5

if __name__ == '__main__':
    print(ItemType.WEAPON.name)