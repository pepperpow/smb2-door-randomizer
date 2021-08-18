import random

import game_lib.smb2 as smb2
from game_lib.smb2 import TileName, EnemyName

def find_sturdy_surface(page, my_room_map):
    # this used numpy...
    positions = [(x+1,y) for x in range(14) for y in [l + page*15 + 2 for l in range(13)]]
    random.shuffle(positions)
    for p in positions:
        tile_solid = my_room_map[p[1], p[0]]
        if tile_solid in [TileName.Spikes,TileName.POWBlock]:
            continue
        if smb2.get_solidness(tile_solid) > 1:
            my_tile = my_room_map[p[1]-1, p[0]]
            if my_tile in [TileName.SubspaceMushroom1, TileName.SubspaceMushroom2, TileName.GrassPotion]:
                continue
            if smb2.get_solidness(my_room_map[p[1]-1, p[0]]) < 2:
                return p
    return None


def invert_level(room):
    my_pages = room.header['pages'] + 1
    room.flags['inverted'] = True

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


convertFromIce = {
    TileName.FrozenRock: TileName.RockWall,
    TileName.JumpThroughIce: TileName.Bridge
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
}

convertFromSand = {
        TileName.CactusTop: TileName.LogPillarTop0,
        TileName.CactusMiddle: TileName.LogPillarMiddle0,
        TileName.ColumnPillarTop2: TileName.LogPillarTop0,
        TileName.ColumnPillarMiddle2: TileName.LogPillarMiddle0,
        TileName.JumpthroughSand: TileName.JumpthroughBrick,
        TileName.JumpthroughSandBlock: TileName.JumpThroughBlock
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

convertTile = {
    0:{
        **convertFromIce,
        **convertFromSand,
        **convertFromWart,
        **convertFromWhale,
        **convertFromWood,
        TileName.CactusTop: TileName.LogPillarTop0,
        TileName.CactusMiddle: TileName.LogPillarMiddle0,
        TileName.ColumnPillarTop2: TileName.LogPillarTop0,
        TileName.ColumnPillarMiddle2: TileName.LogPillarMiddle0,
        TileName.GroundBrick2: TileName.RockWall
    },
    1:{
        **convertFromIce,
        **convertFromWart,
        **convertFromWhale,
        **convertFromWood,
        **convertIntoSand,
        TileName.GroundBrick2: TileName.RockWall
    },
    2:{
        **convertFromIce,
        **convertFromSand,
        **convertFromWart,
        **convertFromWhale,
        **convertFromWood,
        TileName.CactusTop: TileName.LogPillarTop0,
        TileName.CactusMiddle: TileName.LogPillarMiddle0,
        TileName.ColumnPillarTop2: TileName.LogPillarTop0,
        TileName.ColumnPillarMiddle2: TileName.LogPillarMiddle0,
        TileName.GroundBrick2: TileName.RockWall
    },
    3:{
        **convertFromSand,
        **convertFromWart,
        **convertFromWood,
        TileName.LogLeft: TileName.SolidBrick0,
        TileName.LogMiddle: TileName.SolidBrick1,
        TileName.LogRight: TileName.SolidBrick2,
        TileName.CactusTop: TileName.LogPillarTop0,
        TileName.CactusMiddle: TileName.LogPillarMiddle0,
        TileName.ColumnPillarTop2: TileName.LogPillarTop0,
        TileName.ColumnPillarMiddle2: TileName.LogPillarMiddle0,
        TileName.GroundBrick2: TileName.FrozenRock
    },
    4:{
        **convertFromIce,
        **convertFromSand,
        **convertFromWart,
        **convertFromWood,
        **convertFromWhale,
        TileName.GroundBrick2: TileName.RockWall
    },
    5:{
        **convertFromIce,
        **convertIntoSand,
        **convertFromWart,
        **convertFromWhale,
        TileName.GroundBrick2: TileName.RockWall
    },
    6:
    {
        **convertFromIce,
        **convertFromSand,
        **convertFromWhale,
        **convertFromWood,
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
        TileName.SolidGrass: TileName.GroundBrick0,
        TileName.SolidSand: TileName.GroundBrick2,
        TileName.RockWall: TileName.GroundBrick3,
        TileName.RockWallAngle: TileName.GroundBrick3,
        TileName.RockWallOffset: TileName.GroundBrick3,
    }
}

tilesInWorld = {
    x: y.values() for x,y in convertTile.items()
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

def convertMyEnemy(e, old_world, new_world):
    if e[0] in convertEnemy[new_world]:
        new_enemy_id = convertEnemy[new_world][e[0]]
        offset = enemyOffset.get(e[0], (0,0))
        return (new_enemy_id, e[1]+offset[0], e[2]+offset[1], e[3])
    return e

def convertMyTile(t, old_world, new_world):
    if t in convertTile[new_world]:
        new_t = convertTile[new_world][t]
        return new_t
        # if new_t not in tilesInWorld[old_world]:
    return t

convertEnemy = {
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
        EnemyName.Pokey: EnemyName.Trouter,
        EnemyName.CobratJar: EnemyName.WhaleSpout,
        EnemyName.CobratSand: EnemyName.WhaleSpout
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

enemiesInWorld = {
    x: y.values() for x,y in convertEnemy.items()
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
