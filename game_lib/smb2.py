import json, re
from enum import IntEnum

def get_solidness(tile: int):
    """ 
    Returns tile solidity (similar to original SMB2 game table)
    Returns empty (0) if not valid
    """
    solidness = sorted([ 0x01, 0x43, 0x80, 0xC0, 0x12, 0x60, 0x91, 0xCA, 0x18, 0x69, 0x98, 0xD5, 0x40, 0x80, 0xc0, 0x100])
    tile = tile % 256
    for cnt, x in enumerate(solidness):
        solidness = cnt % 4
        if tile < x:
            return solidness
    return 0
    

def read_header(header_bytes):
    """
    Read header bytes to dict
    """
    return {
        'vertical':     (header_bytes[0] & 0b10000000) == 0,
        'horizontal':     (header_bytes[0] & 0b10000000) >> 7,
        'unk1':         (header_bytes[0] & 0b01000000) >> 6,
        'pala':         (header_bytes[0] & 0b00111000) >> 3,
        'unk2':         (header_bytes[0] & 0b00000100) >> 2,
        'palb':         (header_bytes[0] & 0b00000011) >> 0,
        'unk3':         (header_bytes[1] & 0b11100000) >> 5,
        'ground_set':    (header_bytes[1] & 0b00011111) >> 0,
        'pages':        (header_bytes[2] & 0b11110000) >> 4,
        'exterior_type':   (header_bytes[2] & 0b00001111) >> 0,
        'unk4':         (header_bytes[3] & 0b11000000) >> 6,
        'ground_type': (header_bytes[3] & 0b00111000) >> 3,
        'unk5':         (header_bytes[3] & 0b00000100) >> 2,
        'music':        (header_bytes[3] & 0b00000011) >> 0
    }

    
def write_header_bytes_orig(h):
    """
    Header to bytes
    """
    byte1 = (h['horizontal'] << 7) + (h['unk1'] << 6) + (h['pala'] << 3)
    byte1 += (h['unk2'] << 2) + (h['palb'])
    byte2 = (h['unk3'] << 5) + h['ground_set']
    byte3 = (h['pages'] << 4) + h['exterior_type']
    byte4 = (h['unk4'] << 6) + (h['ground_type'] << 3) 
    byte4 += (h['unk5'] << 2) + (h['music'])
    return [byte1, byte2, byte3, byte4]

def write_header_bytes(h):
    """
    Header to bytes
    """
    byte1 = (h['horizontal'] << 7) + (h['unk1'] << 6) + (h['pala'] << 3)
    byte1 += (h['unk2'] << 2) + (h['palb'])
    byte2 = (h['pages'] << 4)
    byte2 += (h['unk5'] << 2) + (h['music'])
    return [byte1, byte2]

def parse_door_ptr(dig):
    level_num = dig[0]
    area, page = dig[1] >> 4, dig[1] % 16
    return (level_num, area, page)


def enemy_data_to_json(enemy_data, pages, vertical=False):
    enemy_json = []
    for page in range(pages):
        my_enemy_data = enemy_data[:enemy_data[0]][1:]
        for e in [my_enemy_data[i:i+2] for i in range(0, len(my_enemy_data), 2)]:
            # if vertical:
            #     enemy_json.append((EnemyName(e[0] % 128), e[1] >> 4, ((e[1] % 16)+page*16)%15, ((e[1] % 16)+page*16)//15))
            # else:
                enemy_json.append((EnemyName(e[0] % 128), e[1] >> 4, e[1]%16, page))
        enemy_data = enemy_data[enemy_data[0]:]
    return enemy_json


def enemies_to_bytes(enemies, vertical):
    byte_arr = []
    my_enemies_transcribed = []
    if not vertical:
        my_enemies_transcribed = enemies
    else:
        for e in enemies:
            i, x, y, page = e
            new_y = ( page * 15 + y ) % 16
            page = ( page * 15 + y ) // 16
            my_enemies_transcribed.append((i, x, new_y, page))

    highest_page = max([0] + [x[3]+1 for x in enemies])
    for page in range(11):
        my_enemy_of_page = [x for x in my_enemies_transcribed if x[3] == page]
        byte_arr.append(len(my_enemy_of_page)*2 + 1)
        for e in my_enemy_of_page:
            if page > 8:
                print('end of room', str(EnemyName(e[0])))
            i, x, y, page = e
            byte_arr.append(i)
            byte_arr.append((x << 4) + y)
    return bytes(byte_arr)

class LevelStorage():
    NEXT_LEVEL_PTR = 10 # rooms are 0-9, next level is 10
    class Room():
        def __init__(self, data, enemies, header, doors, transitions):
            self.data = data
            self.data_modified = None
            self.enemies = enemies
            self.header = header
            self.world = header['world']
            self.vertical = header['horizontal'] == 0
            self.doors = doors
            self.transitions = transitions
            self.is_jar = header['is_jar']
            self.flags = {} # inconsistent usage, should probably make any level modifications a new room

            self.has_boss = any([e['type'] >= 0x5c for e in self.enemies])

    # TODO: This and all the current JSON is poop, rewrite
    # A) raw level data is there, including header and enemy
    # B) metadata.json contains info for all rooms in a dir, emy and header, but not level data
    # C) 10 room restriction per level is arbitrary but we should keep it that way
    @staticmethod
    def process_level(level):
        my_level = []
        accessed_ids = set([0])
        for room in level:
            with open(room) as f:
                room_dict = json.load(f)
            my_header = { x['name']: x['value'] for x in room_dict['properties'] }
            is_vertical = my_header['horizontal'] == 0
            my_room_data = [x-1 if x!=0 else 0x40 for x in room_dict['layers'][0]['data']]
            my_enemies = [
                {
                    'x': (e['x']//16)%16,
                    'y': ((e['y']-16)//16)%15,
                    'page': ((e['y']-16)//16)//15 if is_vertical else (e['x']//16)//16,
                    'name': e['name'],
                    'type': e['gid'] - 257
                } for e in room_dict['layers'][1]['objects']
            ]
            my_doors = { # pagenumber: (room, page)
                int(re.search(r'\d+', x).group()): tuple([int(z) for z in y.split(',')])
                        for x,y in my_header.items() if 'doorptr_page' in x
            }
            transitions = {
                int(re.search(r'\d+', x).group()): y
                        for x,y in my_header.items() if 'transition_page' in x
            }
            for tile in my_room_data:
                if tile == TileName.JarTopGeneric:
                    accessed_ids.add(4)
            accessed_ids = accessed_ids.union(set([x[0]%10 for x in my_doors.values()]))
            my_level.append(LevelStorage.Room(my_room_data, my_enemies, my_header, my_doors, transitions))
        my_level = [level if n in accessed_ids else None for n, level in enumerate(my_level)]
        return my_level

    def __init__(self, level_set):
        self.levels = [LevelStorage.process_level(x) for x in level_set]
        self.worlds = [self.levels[i:i+3] for i in range(0, len(self.levels), 3)]
        self.rooms = [item for sublist in self.levels for item in sublist]
    
    def get_room_by_index(self, world, level, room):
        if world > len(self.worlds) or level > len(self.worlds[world]) or room > 10:
            raise ValueError('Bad Index')
        return self.worlds[world][level][room]

tbl = {
    "*":0XCF,
    "0":0xD0, "1":0xD1, "2":0xD2, "3":0xD3, "4":0xD4, "5":0xD5, "6":0xD6, "7":0xD7, "8":0xD8, "9":0xD9,
    "A":0xDA, "B":0xDB, "C":0xDC, "D":0xDD, "E":0xDE, "F":0xDF, "G":0xE0, "H":0xE1, "I":0xE2, "J":0xE3,
    "K":0xE4, "L":0xE5, "M":0xE6, "N":0xE7, "O":0xE8, "P":0xE9, "Q":0xEA, "R":0xEB, "S":0xEC, "T":0xED,
    "U":0xEE, "V":0xEF, "W":0xF0, "X":0xF1, "Y":0xF2, "Z":0xF3, "-":0xF4, "?":0xF5, ".":0xF6, ",":0xF7,
    "@":0xF8, " ":0xFB
}

reverseTbl = {y:x for x,y in tbl.items()}

char_to_tbl = [251, 251, 251, 251, 251, 251, 251, 251,
            251, 251, 251, 251, 251, 251, 251, 251,
            251, 251, 251, 251, 251, 251, 251, 251,
            251, 251, 251, 251, 251, 251, 251, 251,
            251, 206, 251, 251, 251, 251, 251, 251,
            251, 251, 251, 251, 251, 251, 251, 251,
            208, 209, 210, 211, 212, 213, 214, 215,
            216, 217, 251, 251, 251, 251, 251, 251,
            251, 218, 219, 220, 221, 222, 223, 224,
            225, 226, 227, 228, 229, 230, 231, 232,
            233, 234, 235, 236, 237, 238, 239, 240,
            241, 242, 243, 251, 251, 251, 251, 251,
            251, 218, 219, 220, 221, 222, 223, 224,
            225, 226, 227, 228, 229, 230, 231, 232,
            233, 234, 235, 236, 237, 238, 239, 240,
            241, 242, 243, 251, 251, 251, 251, 251]

class TileName(IntEnum):
    Black = 0x00
    BgCloudLeft = 0x01
    BgCloudRight = 0x02
    BgCloudSmall = 0x03
    WaterfallTop = 0x04
    Waterfall = 0x05
    WaterfallSplash = 0x06
    Chain = 0x07
    WaterTop = 0x08
    HouseLeft = 0x09
    Water = 0x0A
    HouseMiddle = 0x0B
    WaterWhale = 0x0C
    HouseRight = 0x0D
    Unused0E = 0x0E
    Unused0F = 0x0F
    Unused10 = 0x10
    WaterWhaleTail = 0x11
    JumpThroughBlock = 0x12
    CloudLeft = 0x13
    CloudMiddle = 0x14
    CloudRight = 0x15
    JumpThroughIce = 0x16
    ChainStandable = 0x17
    SolidBrick0 = 0x18
    GroundBrick0 = 0x19
    Spikes = 0x1A
    SolidRoundBrick0 = 0x1B
    SolidBlock = 0x1C
    CactusTop = 0x1D
    CactusMiddle = 0x1E
    FrozenRock = 0x1F
    LogPillarTop0 = 0x20
    LogPillarMiddle0 = 0x21
    ClawGripRock = 0x22
    Unused23 = 0x23
    Unused24 = 0x24
    Unused25 = 0x25
    Unused26 = 0x26
    Unused27 = 0x27
    Unused28 = 0x28
    Unused29 = 0x29
    Unused2A = 0x2A
    Unused2B = 0x2B
    Unused2C = 0x2C
    Unused2D = 0x2D
    Unused2E = 0x2E
    Unused2F = 0x2F
    Unused30 = 0x30
    Unused31 = 0x31
    Unused32 = 0x32
    Unused33 = 0x33
    Unused34 = 0x34
    Unused35 = 0x35
    Unused36 = 0x36
    Unused37 = 0x37
    Unused38 = 0x38
    Unused39 = 0x39
    Unused3A = 0x3A
    Unused3B = 0x3B
    Unused3C = 0x3C
    Unused3D = 0x3D
    Unused3E = 0x3E
    Unused3F = 0x3F
    Sky = 0x40
    SubspaceMushroom1 = 0x41
    SubspaceMushroom2 = 0x42
    GrassCoin = 0x43
    GrassLargeVeggie = 0x44
    GrassSmallVeggie = 0x45
    GrassRocket = 0x46
    GrassShell = 0x47
    GrassBomb = 0x48
    GrassPotion = 0x49
    Grass1UP = 0x4A
    GrassPow = 0x4B
    GrassBobOmb = 0x4C
    GrassInactive = 0x4D
    Cherry = 0x4E
    DoorTop = 0x4F
    DoorBottomLock = 0x50
    DoorBottom = 0x51
    LightDoor = 0x52
    LightTrailRight = 0x53
    LightTrail = 0x54
    LightTrailLeft = 0x55
    LightDoorEndLevel = 0x56
    DoorBottomLockStuck = 0x57
    DrawBridgeChain = 0x58
    Whale = 0x59
    WhaleEye = 0x5A
    Phanto = 0x5B
    TreeBackgroundLeft = 0x5C
    TreeBackgroundMiddleLeft = 0x5D
    TreeBackgroundRight = 0x5E
    TreeBackgroundMiddleRight = 0x5F
    WhaleTopLeft = 0x60
    WhaleTop = 0x61
    WhaleTopRight = 0x62
    WhaleTail = 0x63
    JumpThroughMachineBlock = 0x64
    Bridge = 0x65
    BridgeShadow = 0x66
    ConveyorLeft = 0x67
    ConveyorRight = 0x68
    MushroomBlock = 0x69
    Unused6AMushroomBlock = 0x6A
    Unused6BMushroomBlock = 0x6B
    POWBlock = 0x6C
    Unused6D = 0x6D
    SolidBrick1 = 0x6E
    JarTopPointer = 0x6F
    JarMiddle = 0x70
    JarBottom = 0x71
    JarSmall = 0x72
    JarTopGeneric = 0x73
    JarTopNonEnterable = 0x74
    LogLeft = 0x75
    LogMiddle = 0x76
    LogRight = 0x77
    LogRightTree = 0x78
    LogPillarTop1 = 0x79
    LogPillarMiddle1 = 0x7A
    Unused7B = 0x7B
    Unused7C = 0x7C
    Unused7D = 0x7D
    Unused7E = 0x7E
    Unused7F = 0x7F
    Ladder = 0x80
    LadderShadow = 0x81
    PalmTreeTrunk = 0x82
    DarkDoor = 0x83
    PyramidLeftAngle = 0x84
    PyramidLeft = 0x85
    PyramidRight = 0x86
    PyramidRightAngle = 0x87
    StarBg1 = 0x88
    StarBg2 = 0x89
    QuicksandSlow = 0x8A
    QuicksandFast = 0x8B
    HornTopLeft = 0x8C
    HornTopRight = 0x8D
    HornBottomLeft = 0x8E
    HornBottomRight = 0x8F
    BackgroundBrick = 0x90
    JumpThroughSand = 0x91
    JumpThroughWoodBlock = 0x92
    DiggableSand = 0x93
    LadderStandable = 0x94
    LadderStandableShadow = 0x95
    JumpThroughSandBlock = 0x96
    JumpThroughBrick = 0x97
    NothingBlock = 0x98
    SolidSand = 0x99
    NothingBlock2 = 0x9A
    SolidBrick2 = 0x9B
    GroundBrick2 = 0x9C
    BombableBrick = 0x9D
    JarWall = 0x9E
    RockWallAngle = 0x9F
    RockWall = 0xA0
    RockWallOffset = 0xA1
    SolidRoundBrick2 = 0xA2
    SolidBrick2Wall = 0xA3
    SolidWood = 0xA4
    RockWallEyeLeft = 0xA5 
    RockWallEyeRight = 0xA6 
    RockWallMouth = 0xA7 
    WindowTop = 0xA8 
    DoorwayTop = 0xA9
    ColumnPillarTop2 = 0xAA
    ColumnPillarMiddle2 = 0xAB
    UnusedAC = 0xAC
    UnusedAD = 0xAD
    UnusedAE = 0xAE
    UnusedAF = 0xAF
    UnusedB0 = 0xB0 
    UnusedB1 = 0xB1
    UnusedB2 = 0xB2
    UnusedB3 = 0xB3 
    UnusedB4 = 0xB4 
    UnusedB5 = 0xB5 
    UnusedB6 = 0xB6 
    UnusedB7 = 0xB7
    UnusedB8 = 0xB8 
    UnusedB9 = 0xB9
    UnusedBA = 0xBA 
    UnusedBB = 0xBB
    UnusedBC = 0xBC 
    UnusedBD = 0xBD 
    UnusedBE = 0xBE 
    UnusedBF = 0xBF 
    PalmTreeTop = 0xC0
    VineTop = 0xC1
    Vine = 0xC2
    VineBottom = 0xC3
    ClimbableSky = 0xC4
    UnusedC5 = 0xC5
    JarOutsideBackground = 0xC6 
    GreenPlatformLeft = 0xC7
    GreenPlatformMiddle = 0xC8
    GreenPlatformRight = 0xC9
    GreenPlatformTopLeft = 0xCA
    MushroomTopLeft = 0xCB
    GreenPlatformTop = 0xCC
    MushroomTopMiddle = 0xCD
    GreenPlatformTopRight = 0xCE
    MushroomTopRight = 0xCF
    GreenPlatformTopLeftOverlap = 0xD0
    GreenPlatformTopRightOverlap = 0xD1
    GreenPlatformTopLeftOverlapEdge = 0xD2
    GreenPlatformTopRightOverlapEdge = 0xD3
    VineStandable = 0xD4
    SolidGrass = 0xD5
    SolidBrick3 = 0xD6
    GroundBrick3 = 0xD7 
    UnusedD8 = 0xD8
    UnusedD9 = 0xD9
    UnusedDA = 0xDA
    UnusedDB = 0xDB
    UnusedDC = 0xDC
    UnusedDD = 0xDD
    UnusedDE = 0xDE
    UnusedDF = 0xDF
    UnusedE0 = 0xE0
    UnusedE1 = 0xE1
    UnusedE2 = 0xE2
    UnusedE3 = 0xE3
    UnusedE4 = 0xE4
    UnusedE5 = 0xE5
    UnusedE6 = 0xE6
    UnusedE7 = 0xE7
    UnusedE8 = 0xE8
    UnusedE9 = 0xE9
    UnusedEA = 0xEA
    UnusedEB = 0xEB
    UnusedEC = 0xEC
    UnusedED = 0xED
    UnusedEE = 0xEE
    UnusedEF = 0xEF
    UnusedF0 = 0xF0
    UnusedF1 = 0xF1
    UnusedF2 = 0xF2
    UnusedF3 = 0xF3
    UnusedF4 = 0xF4
    UnusedF5 = 0xF5
    UnusedF6 = 0xF6
    UnusedF7 = 0xF7
    UnusedF8 = 0xF8
    UnusedF9 = 0xF9
    UnusedFA = 0xFA
    UnusedFB = 0xFB
    UnusedFC = 0xFC
    UnusedFD = 0xFD
    UnusedFE = 0xFE
    UnusedFF = 0xFF

class EquipName(IntEnum):
    DefaultMush = 0
    PowerThrow = 1
    PowerCharge = 2
    PowerGrip = 3
    StoreItem = 4
    FallDefense = 5
    ImmuneFire = 6
    ImmuneElec = 7
    Secret = 8
    AllTerrain = 9
    HiJumpBoot = 10
    FloatBoots = 11
    MasterKey = 12
    AirHop = 13
    BombGlove = 14
    EggGlove = 15
    Map = 16
    EquipMush = 17
    UnlockM = 18
    UnlockL = 19
    UnlockT = 20
    UnlockP = 21
    Fragment = 22
    Crystal = 23

class EnemyName(IntEnum):
    Heart = 0x00
    ShyguyRed = 0x01
    Tweeter = 0x02
    ShyguyPink = 0x03
    Porcupo = 0x04
    SnifitRed = 0x05
    SnifitGray = 0x06
    SnifitPink = 0x07
    Ostro = 0x08
    BobOmb = 0x09
    AlbatossCarryingBobOmb = 0x0A
    AlbatossStartRight = 0x0B
    AlbatossStartLeft = 0x0C
    NinjiRunning = 0x0D
    NinjiJumping = 0x0E
    BeezoDiving = 0x0F
    BeezoStraight = 0x10
    WartBubble = 0x11
    Pidgit = 0x12
    Trouter = 0x13
    Hoopstar = 0x14
    JarGeneratorShyguy = 0x15
    JarGeneratorBobOmb = 0x16
    Phanto = 0x17
    CobratJar = 0x18
    CobratSand = 0x19
    Pokey = 0x1A
    Bullet = 0x1B
    Birdo = 0x1C
    Mouser = 0x1D
    Egg = 0x1E
    Tryclyde = 0x1F
    Fireball = 0x20
    Clawgrip = 0x21
    ClawgripRock = 0x22
    PanserStationaryFiresAngled = 0x23
    PanserWalking = 0x24
    PanserStationaryFiresUp = 0x25
    Autobomb = 0x26
    AutobombFire = 0x27
    WhaleSpout = 0x28
    Flurry = 0x29
    Fryguy = 0x2A
    FryguySplit = 0x2B
    Wart = 0x2C
    HawkmouthBoss = 0x2D
    Spark1 = 0x2E 
    Spark2 = 0x2F 
    Spark3 = 0x30 
    Spark4 = 0x31 
    VegetableSmall = 0x32
    VegetableLarge = 0x33
    VegetableWart = 0x34
    Shell = 0x35
    Coin = 0x36
    Bomb = 0x37
    Rocket = 0x38
    MushroomBlock = 0x39
    POWBlock = 0x3A
    FallingLogs = 0x3B
    SubspaceDoor = 0x3C
    Key = 0x3D
    SubspacePotion = 0x3E
    Mushroom = 0x3F
    Mushroom1up = 0x40
    FlyingCarpet = 0x41
    HawkmouthRight = 0x42
    HawkmouthLeft = 0x43
    CrystalBall = 0x44
    Starman = 0x45
    Stopwatch = 0x46
    AttackAlbatossCarryingBobOmb = 0x47
    AttackBeezo = 0x48
    StopAttack = 0x49
    VegetableThrower = 0x4A 
    Enemy4B = 0x4B 
    Enemy4C = 0x4C 
    Enemy4D = 0x4D 
    Enemy4E = 0x4E 
    Enemy4F = 0x4F 
    Enemy50 = 0x50 
    Enemy51 = 0x51 
    Enemy52 = 0x52 
    Enemy53 = 0x53 
    Enemy54 = 0x54 
    Enemy55 = 0x55 
    Enemy56 = 0x56 
    Enemy57 = 0x57 
    Enemy58 = 0x58 
    Enemy59 = 0x59 
    Enemy5A = 0x5A 
    Enemy5B = 0x5B 
    BossBirdo = 0x5C
    BossMouser = 0x5D
    BossEgg = 0x5E
    BossTryclyde = 0x5F
    BossFireball = 0x60
    BossClawgrip = 0x61
    BossClawgripRock = 0x62
    BossPanserStationaryFiresAngled = 0x63
    BossPanserWalking = 0x64
    BossPanserStationaryFiresUp = 0x65
    BossAutobomb = 0x66
    BossAutobombFire = 0x67
    BossWhaleSpout = 0x68
    BossFlurry = 0x69
    BossFryguy = 0x6A
    BossFryguySplit = 0x6B
    BossWart = 0x6C
    BossHawkmouthBoss = 0x6D
    BossSpark1 = 0x6E
    BossSpark2 = 0x6F
    BossSpark3 = 0x70
    BossSpark4 = 0x71
    BossVegetableSmall = 0x72
    BossVegetableLarge = 0x73
    BossVegetableWart = 0x74
    BossShell = 0x75
    BossCoin = 0x76
    BossBomb = 0x77
    BossRocket = 0x78
    BossMushroomBlock = 0x79
    BossPOWBlock = 0x7A
    BossFallingLogs = 0x7B
    BossSubspaceDoor = 0x7C
    BossKey = 0x7D
    BossSubspacePotion = 0x7E
    BossMushroom = 0x7F


ClimbableTiles = [
    TileName.Vine,
    TileName.VineStandable,
    TileName.VineBottom,
    TileName.ClimbableSky,
    TileName.Chain,
    TileName.Ladder,
    TileName.LadderShadow,
    TileName.LadderStandable,
    TileName.LadderStandableShadow,
    TileName.ChainStandable
]

JarTiles = [
    TileName.JarBottom,
    TileName.JarMiddle,
    TileName.JarTopGeneric,
    TileName.JarTopPointer,
    TileName.JarTopNonEnterable
]

DoorTiles = [
    TileName.DoorBottom,
    TileName.DoorBottomLock,
    TileName.LightDoor,
    TileName.LightDoorEndLevel,
    TileName.DarkDoor
]

SpecialTiles = [
    TileName.DiggableSand,
    TileName.MushroomBlock
]

VitalTiles = [
    TileName.SubspaceMushroom1,
    TileName.SubspaceMushroom2,
    TileName.GrassPotion,
    TileName.GrassRocket
]
