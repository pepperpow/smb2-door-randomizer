import random

import game_lib.smb2 as smb2
from game_lib.smb2 import TileName, EnemyName

def find_sturdy_surface(page, my_room_map, vertical):
    # this used numpy... before
    # x = 1, 2 ... 15
    # y = 2 .. 14?
    if vertical:
        my_map = my_room_map[15*page:15*page+15]
        positions = [(x, y) for x in range(1, 14) for y in range(4,14)]
    else:
        my_map = [x[page*16:page*16+16] for x in my_room_map]
        positions = [(x, y) for x in range(1, 14) for y in range(4,14)]
    random.shuffle(positions)
    for p in positions:
        tile_solid = my_map[p[1]][p[0]]
        if tile_solid in [TileName.Spikes,TileName.POWBlock,TileName.MushroomBlock]:
            continue
        if smb2.get_solidness(tile_solid) > 1:
            my_tile = my_map[p[1]-1][p[0]]
            if my_tile in smb2.VitalTiles:
                continue
            if smb2.get_solidness(my_map[p[1]-1][p[0]]) < 2:
                return p
    return None

def rotate_me_room(room, vertical):
    # return a map as a 2d array
    my_pages = room.header['pages'] + 1
    if vertical:
        my_room_map = [room.data[i:i+16] for i in range(0, len(room.data), 16)]
    else:
        my_room_map = [room.data[i:i+160][:16*my_pages] for i in range(0, len(room.data), 160)]
        # if my_pages < 10:
        #     my_room_map = [x + [TileName.Sky]*(10-my_pages)*16 for x in my_room_map]
    return my_room_map


def invert_level(room):
    my_pages = room.header['pages'] + 1
    room.flags['inverted'] = True

    # rotate and invert lines
    if room.vertical:
        my_room_map = [room.data[i:i+16][::-1] for i in range(0, len(room.data), 16)]
    else:
        my_room_map = [room.data[i:i+160][:16*my_pages][::-1] for i in range(0, len(room.data), 160)]
        if my_pages < 10:
            my_room_map = [x + [TileName.Sky]*(10-my_pages)*16 for x in my_room_map]
    my_room_map = [item for sublist in my_room_map for item in sublist]
    my_room_map = [invertTile.get(x, x) for x in my_room_map]

    new_enemies = [flip_enemy(e, room.vertical, my_pages) for e in room.enemies]

    if room.vertical:
        new_doors = room.doors
    else:
        new_doors = {room.header['pages'] - int(x): room.doors[x] for x in room.doors}

    return my_room_map, new_enemies, new_doors


def shuffle_mush(room):
    my_mushes = [x for x in room.data if x in [TileName.SubspaceMushroom1, TileName.SubspaceMushroom2]]
    import pdb; pdb.set_trace()

valid_tiles = [TileName.GrassPotion]

swappable_veg = [TileName.GrassLargeVeggie, TileName.GrassSmallVeggie]

swappable_pow = [TileName.GrassShell, TileName.GrassPow, TileName.GrassBobOmb]

def shuffle_herbs(room):
    # GrassCoin = 0x43
    # GrassLargeVeggie = 0x44
    # GrassSmallVeggie = 0x45
    # GrassRocket = 0x46
    # GrassShell = 0x47
    # GrassBomb = 0x48
    # GrassPotion = 0x49
    # Grass1UP = 0x4A
    # GrassPow = 0x4B
    # GrassBobOmb = 0x4C
    my_bushes = [x for x in room.data if x in valid_tiles + swappable_pow + swappable_veg]
    import pdb; pdb.set_trace()


def flip_enemy(e, vertical, my_pages):
    birdo_type = e['type'] in [EnemyName.Birdo, EnemyName.BossBirdo] and e['x'] in [0xA, 0xB]
    return {
        'x': 15 - e['x'] if not birdo_type else e['x'],
        'y': e['y'],
        'page': e['page'] if vertical else my_pages - 1 - e['page'],
        'name': e['name'],
        'type': invertEnemy.get(e['type'], e['type'])
    }


def apply_command(data, c):
    if 'V' in c.command:
        spots = [(c.x + (c.y*16 + c.page*240) + p*16) for p in range(len(c.tiles))]
    else:
        spots = [((c.x + p)//16)*240 + (c.y*16 + c.page*240) + (c.x+p)%16 for p in range(len(c.tiles))]
    for x, t in zip(spots, c.tiles):
        data[x] = ord(t)


def query_tiles(room, x, y, page, length, vertical_command=False):
    if room.vertical:
        my_room_map = [room.data[i:i+16] for i in range(0, len(room.data), 16)]
    else:
        my_room_map = [room.data[i:i+160] for i in range(0, len(room.data), 160)]

    if vertical_command:
        y += page*15
        my_room_rows = my_room_map[y:y+length]
        return [item for sublist in [row[x] for row in my_room_rows] for item in sublist]
    else:
        x += page*16
        return my_room_map[y][x:x+length]


def convertMyEnemy(e, old_world, new_world):
    og_enemies = enemiesInWorld[new_world]
    new_enemies = convertEnemyFromOldTo[new_world]
    new_enemies.update(convertEnemyTo[new_world])
    if e[0] in new_enemies and not e[0] in og_enemies:
        new_enemy_id = new_enemies[e[0]]
        offset = enemyOffset.get(e[0], (0,0))
        return (new_enemy_id, e[1]+offset[0], e[2]+offset[1], e[3])
    return e


def convertMyTile(t, old_world, new_world):
    og_tiles = tilesInWorld[new_world]
    new_tiles = convertTileFromOldTo[new_world]
    new_tiles.update(convertTileTo[new_world])
    if t in new_tiles and not t in og_tiles:
        new_t = new_tiles[t]
        return new_t
        # if new_t not in tilesInWorld[old_world]:
    return t


convertFromIce = {
    TileName.FrozenRock: TileName.RockWall,
    TileName.JumpThroughIce: TileName.Bridge
}

convertIntoIce = {
    **{y:x for x,y in convertFromIce.items()}
}

convertFromWhale = {
    TileName.WhaleTail: TileName.JumpThroughBlock,
    TileName.Whale: TileName.Sky,
    TileName.WhaleEye: TileName.Sky,
    TileName.WhaleTopLeft: TileName.JumpThroughBlock,
    TileName.WhaleTop: TileName.JumpThroughBlock,
    TileName.WhaleTopRight: TileName.JumpThroughBlock,
    TileName.WaterWhale: TileName.WaterTop,
    TileName.WaterWhaleTail: TileName.WaterTop,
}

convertIntoSand = {
        TileName.SolidGrass: TileName.SolidSand,
        TileName.LogPillarTop0: TileName.CactusTop,
        TileName.LogPillarMiddle0: TileName.CactusMiddle,
        TileName.LogPillarTop1: TileName.CactusTop,
        TileName.LogPillarMiddle1: TileName.CactusMiddle,
        TileName.JumpThroughBrick: TileName.JumpThroughSand,
        TileName.JumpThroughBlock: TileName.JumpThroughSandBlock,
}

convertFromSand = {
        TileName.CactusTop: TileName.LogPillarTop0,
        TileName.CactusMiddle: TileName.LogPillarMiddle0,
        TileName.ColumnPillarTop2: TileName.LogPillarTop0,
        TileName.ColumnPillarMiddle2: TileName.LogPillarMiddle0,
        TileName.JumpThroughSand: TileName.JumpThroughBrick,
        TileName.JumpThroughSandBlock: TileName.JumpThroughBlock
}

convertFromWood = {
        TileName.TreeBackgroundLeft: TileName.Sky,
        TileName.TreeBackgroundRight: TileName.Sky,
        TileName.TreeBackgroundMiddleLeft: TileName.Sky,
        TileName.TreeBackgroundMiddleRight: TileName.Sky,
        TileName.SolidWood: TileName.SolidBlock
}

convertFromWart = {
    TileName.JumpThroughMachineBlock: TileName.JumpThroughBlock,
    TileName.GroundBrick0: TileName.SolidBrick0,
    TileName.GroundBrick2: TileName.SolidBrick1,
    TileName.GroundBrick3: TileName.SolidBrick2,
    TileName.HornBottomLeft: TileName.JarSmall,
    TileName.HornBottomRight: TileName.JarSmall,
    TileName.HornTopLeft: TileName.JarSmall,
    TileName.HornTopRight: TileName.JarSmall,
}

defaultConvert = {
    'normal': {
        **convertFromIce,
        **convertFromSand,
        **convertFromWhale,
        **convertFromWood,
        **convertFromWart,
    }, 
    'sand': {
        **convertFromIce,
        **convertFromWhale,
        **convertFromWood,
        **convertFromWart,
    },
    'ice': {
        **convertFromSand,
        **convertFromWood,
        **convertFromWart,
    }
}

convertTileFromOldTo = {
    0: defaultConvert['normal'],
    1: defaultConvert['sand'],
    2: defaultConvert['normal'],
    3: defaultConvert['ice'],
    4: defaultConvert['normal'],
    5: {
        **convertFromIce,
        **convertFromWart,
        **convertFromWhale,
    },
    6: {
        **convertFromIce,
        **convertFromSand,
        **convertFromWhale,
        **convertFromWood,
    },

}

convertTileTo = {
    0:{
        TileName.CactusTop: TileName.LogPillarTop0,
        TileName.CactusMiddle: TileName.LogPillarMiddle0,
        TileName.ColumnPillarTop2: TileName.LogPillarTop0,
        TileName.ColumnPillarMiddle2: TileName.LogPillarMiddle0,
        TileName.GroundBrick2: TileName.RockWall
    },
    1:{
        **convertIntoSand,
        TileName.GroundBrick2: TileName.RockWall
    },
    2:{
        TileName.CactusTop: TileName.LogPillarTop0,
        TileName.CactusMiddle: TileName.LogPillarMiddle0,
        TileName.ColumnPillarTop2: TileName.LogPillarTop0,
        TileName.ColumnPillarMiddle2: TileName.LogPillarMiddle0,
        TileName.GroundBrick2: TileName.RockWall
    },
    3:{
        **convertIntoIce,
        TileName.LogLeft: TileName.JumpThroughIce,
        TileName.LogMiddle: TileName.JumpThroughIce,
        TileName.LogRight: TileName.JumpThroughIce,
        TileName.LogRightTree: TileName.JumpThroughIce,
        TileName.CactusTop: TileName.LogPillarTop0,
        TileName.CactusMiddle: TileName.LogPillarMiddle0,
        TileName.ColumnPillarTop2: TileName.LogPillarTop0,
        TileName.ColumnPillarMiddle2: TileName.LogPillarMiddle0,
        TileName.GroundBrick2: TileName.FrozenRock
    },
    4:{
        TileName.GroundBrick2: TileName.RockWall
    },
    5:{
        **convertIntoSand,
        TileName.GroundBrick2: TileName.RockWall
    },
    6:
    {
        TileName.FrozenRock: TileName.SolidBrick0,
        TileName.JumpThroughIce: TileName.ConveyorLeft,
        TileName.GreenPlatformTopLeft: TileName.MushroomTopLeft,
        TileName.GreenPlatformTop: TileName.MushroomTopMiddle,
        TileName.GreenPlatformTopRight: TileName.MushroomTopRight,
        TileName.GreenPlatformTopLeftOverlap: TileName.MushroomTopLeft,
        TileName.GreenPlatformTopLeftOverlapEdge: TileName.MushroomTopLeft,
        TileName.GreenPlatformTopRightOverlap: TileName.MushroomTopRight,
        TileName.GreenPlatformTopRightOverlapEdge: TileName.MushroomTopRight,
        TileName.GreenPlatformLeft: TileName.HouseLeft,
        TileName.GreenPlatformMiddle: TileName.HouseMiddle,
        TileName.GreenPlatformRight: TileName.HouseRight,
        TileName.PalmTreeTop: TileName.LadderStandable,
        TileName.VineTop: TileName.LadderStandable,
        TileName.PalmTreeTrunk: TileName.Ladder,
        TileName.Vine: TileName.Ladder,
        TileName.VineBottom: TileName.Ladder,
        TileName.VineStandable: TileName.LadderStandable,
        TileName.LogPillarTop0: TileName.ColumnPillarTop2,
        TileName.LogPillarTop1: TileName.ColumnPillarTop2,
        TileName.LogPillarMiddle0: TileName.ColumnPillarMiddle2,
        TileName.LogPillarMiddle1: TileName.ColumnPillarMiddle2,
        TileName.LogLeft: TileName.SolidBrick0,
        TileName.LogMiddle: TileName.SolidBrick1,
        TileName.LogRight: TileName.SolidBrick2,
        TileName.LogRightTree: TileName.SolidBrick2,
        TileName.SolidGrass: TileName.GroundBrick0,
        TileName.SolidSand: TileName.GroundBrick2,
        TileName.RockWall: TileName.GroundBrick3,
        TileName.RockWallAngle: TileName.GroundBrick3,
        TileName.RockWallOffset: TileName.GroundBrick3,
    }
}

tilesInWorld = {
    x: [t for t in y.values()] for x,y in convertTileTo.items()
}

enemyOffset = {
    EnemyName.CobratJar: (0, -1),
    EnemyName.CobratSand: (0, -1)
}

enemiesIceConvert = {
    EnemyName.WhaleSpout: EnemyName.Trouter,
    EnemyName.Flurry: EnemyName.BobOmb,
    EnemyName.Autobomb: EnemyName.NinjiRunning
}

enemiesSandConvert = {
    EnemyName.Pokey: EnemyName.Trouter,
    EnemyName.CobratJar: EnemyName.NinjiJumping,
    EnemyName.CobratSand: EnemyName.NinjiRunning
}

enemiesLandConvert = {
    EnemyName.Ostro: EnemyName.NinjiRunning
}

convertEnemyFromOldTo = {
    0:{
        **enemiesIceConvert,
        **enemiesSandConvert,
    },
    1:{
        **enemiesIceConvert,
        **enemiesLandConvert,
    },
    2:{
        **enemiesIceConvert,
        **enemiesSandConvert,
    },
    3:{
        **enemiesLandConvert,
    },
    4:{
        **enemiesIceConvert,
        **enemiesSandConvert,
    },
    5:{
        **enemiesIceConvert,
        **enemiesLandConvert,
    },
    6:{
        **enemiesSandConvert,
        **enemiesLandConvert,
        **enemiesIceConvert,
    }
}

convertEnemyTo = {
    0: {},
    1: {},
    2: {},
    3: {
        EnemyName.CobratJar: EnemyName.WhaleSpout,
        EnemyName.CobratSand: EnemyName.WhaleSpout
    },
    4: {},
    5: {},
    6: {},
}

enemiesInWorld = {
    x: [e for e in y.values()] for x,y in convertEnemyTo.items()
}

# i just ripped this from the game should probably use enums
invertTile = {
	0x75: 0x77, 0x77: 0x75, 0xCA: 0xce, 0xCE: 0xca, 0xC7: 0xc9, 0xC9: 0xc7, 0xD0: 0xd1, 0xD1: 0xd0,
	0x01: 0x02, 0x02: 0x01, 0x84: 0x87, 0x87: 0x84, 0x60: 0x62, 0x62: 0x60, 0x13: 0x15, 0x15: 0x13,
	0x53: 0x55, 0x55: 0x53, 0xCB: 0xcf, 0xCF: 0xcb, 0x09: 0x0d, 0x0D: 0x09, 0xd3: 0xd0, }

invertEnemy = {
    EnemyName.AlbatossStartLeft: EnemyName.AlbatossStartRight,
    EnemyName.AlbatossStartRight: EnemyName.AlbatossStartLeft,
    EnemyName.HawkmouthLeft: EnemyName.HawkmouthRight,
    EnemyName.HawkmouthRight: EnemyName.HawkmouthLeft
}
