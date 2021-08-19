import random, copy
from re import I
from types import SimpleNamespace

import game_lib.smb2 as smb2
from game_lib.smb2 import ClimbableTiles, EnemyName, TileName
from game_lib.level_modify import convertMyTile, convertMyEnemy, apply_command
import game_lib.level_tokenize as token
from game_lib.level_modify import rotate_me_room, find_sturdy_surface


c_rand = ['blue', 'black', 'green', 'purple']
up = [0, -1]
down = [0, 1]
left = [-1, 0]
right = [1, 0]
poses = [up, down, left, right]

add_tup = lambda a,b: tuple([a[x]+b[x] for x in range(len(a))])

# consider: graph theory to manage levels that only go one way...
#   each level starts as a node, and internally has a path to each page or section of pages
#   long since considered using A* pathing to determine this, but for another time or another programmer
def map_maker(rooms, bosses):
    shape = 80
    my_map = [ ['.' for y in range(shape)] for x in range(shape)]
    candidates = []
    occupied, slots, edges = {}, {}, {}
    black_list = set()

    rooms = sorted(rooms, key=lambda x: x.header['pages'] == 0)

    for room_cnt, room in enumerate(rooms + bosses):
        slots[room_cnt] = room
        # if level is Not Valid
        pages = room.header['pages']
        # invert outside of level_order functions
        # my_room_map = np.array([(x) for x in room.data]).reshape((150,16))
        commands = [x for x in token.tokenize(room.data, not room.vertical, True)]
        
        # if we are out of candidates (shouldn't happen mid run), start from center
        if len(candidates) == 0:
            candidates = [ ( (shape//2, shape//2), None ) ]
        random.shuffle(candidates)

        # create jitter (variations along x or y axis), then shuffle
        my_jitters = [(-x, 0) for x in range(pages + 1)] if room.vertical else [(0, -x) for x in range(pages + 1)] 
        random.shuffle(my_jitters)

        # measure success, if we reach end of a for loop without a position made, we have a problem
        success = False

        my_room_2d_array = rotate_me_room(room, room.vertical)
        room.flags['sturdy_pages'] = [x for x in range(pages + 1) if find_sturdy_surface(x, my_room_2d_array, room.vertical)]
        
        # of our candidates...
        for target_pos, target_room in candidates:
            if target_room is not None and (tuple(target_room) in edges or tuple(target_room) in black_list):
                continue
            # place at x,y + jitter, calc spaces from x,y + jitter to Z amount of pages
            # if we have any occupied positions, skip
            # TODO: also make sure we don't pick candidates that already have a door associated
            # try to get all positions, if any give us an exception Out Of Bounds, BAIL
            # TODO: expand map in circumstances of an exception(?)
            for jitter in my_jitters:
                n_pos = add_tup(target_pos, jitter)
                if room.vertical:
                    adjusted_coords = [add_tup(n_pos, (x, 0)) for x in range(pages + 1)]
                else:
                    adjusted_coords = [add_tup(n_pos, (0, x)) for x in range(pages + 1)]

                if any([tuple(x) in occupied for x in adjusted_coords]): continue
                try: [my_map[p[0]][p[1]] for p in adjusted_coords]
                except: 
                    continue
            
                # IF HERE, THEN WE HAVE SOME SUCCESS
                # create our edge, then map out new candidates/overlaps, label our new stuff
                for page, n_pos in enumerate(adjusted_coords):
                    if tuple(n_pos) == tuple(target_pos):
                        solid_success = page in room.flags['sturdy_pages']
                        if solid_success and target_room is not None:
                            edges[tuple(n_pos)] = tuple(target_room)
                            edges[tuple(target_room)] = tuple(n_pos)
                if not solid_success: 
                    print('no solid...')
                    continue
                for page, n_pos in enumerate(adjusted_coords):
                    key = str(room_cnt % 10)
                    if room.is_jar > 0: key = 'J'
                    for c in [x for x in commands if x.page == page]:
                        if any([chr(x) in c.tiles for x in [TileName.SubspaceMushroom1, TileName.SubspaceMushroom2]]):
                            key = 'M'; break
                    if room.has_boss: key = 'B'
                    my_map[n_pos[0]][n_pos[1]] = key
                    occupied[tuple(n_pos)] = (room_cnt, page)
                # label our new candidate positions
                for page, n_pos in enumerate(adjusted_coords):
                    if room.has_boss:
                        break
                    solid_success = page in room.flags['sturdy_pages']
                    if solid_success:
                        my_new_places = [add_tup(n_pos, x) for x in poses if add_tup(n_pos, x) not in occupied]
                        for new_n_pos in my_new_places:
                            try:
                                my_map[new_n_pos[0]][new_n_pos[1]] = '+'
                                candidates.append((new_n_pos, n_pos))
                            except:
                                continue
                success = True; break
            if success: break
        if not success:
            pass
            # print('this happened')
            # print((room_cnt, room_name))
    # print(my_map)

    for target_pos, target_room in candidates:
        target_pos = tuple(target_pos)
        if target_room is None or target_room is not None and (tuple(target_room) in edges or tuple(target_room) not in occupied):
            continue
        target_room = tuple(target_room)
        if target_pos in occupied and target_pos not in edges:
            if random.randint(0, 1000) > 100:
                continue
            my_room, my_target_room = occupied[target_room], occupied[target_pos]
            room, page = slots[my_room[0]], my_room[1]
            solid_success = page in room.flags['sturdy_pages']
            if solid_success:
                room, page = slots[my_target_room[0]], my_target_room[1]
                solid_success = page in room.flags['sturdy_pages']
                if solid_success:
                    edges[tuple(target_pos)] = tuple(target_room)
                    edges[tuple(target_room)] = tuple(target_pos)
        pass

    edges_by_level = {} 
    for edge in edges:
        _level, page = occupied[edge]
        edges_by_level[occupied[edge]] = occupied[edges[edge]]
        
    for slot in slots:
        my_nodes = []
        for p in range(10):
            if (slot, p) in edges_by_level:
                my_nodes.append(edges_by_level[(slot, p)][0])
        slots[slot].flags['connections'] = my_nodes
    
    min_x, max_x = shape, 0
    min_y, max_y = shape, 0

    for row in range(shape):
        for col in range(shape):
            if my_map[row][col] != '.':
                min_x = min(col, min_x)
                max_x = max(col, max_x)
                min_y = min(row, min_y)
                max_y = max(row, max_y)
    
    my_map = my_map[min_y:max_y+1]
    for row in range(len(my_map)):
        my_map[row] = my_map[row][min_x:max_x+1]

    return my_map, slots, edges_by_level


def map_stringer(slots, edges_by_level, my_mem_locs, boss_lock=False):
    levels_data = []
    # normal, dark, light, dark solid, locked, jar
    door_defs = [[chr(TileName.DoorTop), chr(TileName.DoorBottom)],
                    [chr(TileName.DarkDoor)]*2,
                    [chr(TileName.LightDoor)]*2,
                    [chr(TileName.DarkDoor), chr(TileName.DarkDoor), chr(TileName.JumpthroughBrick)],
                    [chr(TileName.DoorTop), chr(TileName.DoorBottomLock) if boss_lock else chr(TileName.DoorBottom)],
                    [chr(TileName.JarTopPointer), chr(TileName.JarBottom)],
                    ]
    for room_cnt in sorted(slots.keys()):
        room = slots[room_cnt]

        my_room_map = rotate_me_room(room, room.vertical)

        # remove vines...
        if not room.vertical:
            targets = [0] + [13, 14]
        else:
            targets = [0] +  [x + room.header['pages']*15 for x in [13, 14]]
        for row in targets:
            my_room_map[row] = [x if x not in ClimbableTiles else TileName.JumpThroughBlock for x in my_room_map[row]]
        
        if not room.vertical: # fill room back to 10 pages
            my_pages = room.header['pages'] + 1
            if my_pages < 10:
                my_room_map = [x + [TileName.Sky]*(10-my_pages)*16 for x in my_room_map]
        room.data = [item for sublist in my_room_map for item in sublist]

        my_enemies = room.enemies
        commands = [x for x in token.tokenize(room.data, not room.vertical, True)]
        
        door_data = []
        door_type = []
        for p in range(10):
            my_edge = edges_by_level.get((room_cnt, p))
            if my_edge is not None:
                this_room, this_page = my_edge
                sub_room = slots[this_room]
                if room.has_boss:
                    door_data.append(( this_room//10, this_page + ((this_room%10)<<4) ))
                    continue
                elif sub_room.has_boss:
                    this_page = 0
                    door_type.append(4)
                else:
                    # make a visible door
                    my_music, sub_music = room.header['music'], sub_room.header['music']
                    if sub_room.is_jar:
                        door_type.append(5)
                    elif room.is_jar:
                        door_type.append(-1)
                    elif sub_music == my_music == 0:
                        door_type.append(0)
                    elif sub_music == my_music:
                        door_type.append(1)
                    elif 0 == sub_music < my_music:
                        door_type.append(2)
                    elif sub_music > my_music == 0:
                        door_type.append(1)
                    else:
                       door_type.append(0)
                door_data.append(( this_room//10, this_page + ((this_room%10)<<4) ))
            else:
                door_data.append(None)
                door_type.append(None)

        my_world = room.world
        new_world = room.flags['convert_world'] if my_world < 6 and not room.has_boss else my_world
        new_world = room.flags['convert_world'] if EnemyName.Pidgit not in [e['type'] for e in my_enemies] else my_world
        room.header['unk3'] = new_world
        my_enemies = [[e['type'], e['x'], e['y'], e['page']] for e in my_enemies]

        if my_world != new_world:
            if room.header['pala'] == 1 and new_world in [3]: # snow doesn't use dark, but we can fix that later
                room.header['pala'] = 0
            for c in commands:
                c.tiles = ''.join([chr(convertMyTile(ord(t), my_world, new_world)) for t in c.tiles])
            
            my_enemies = [convertMyEnemy(e, my_world, new_world) for e in my_enemies]

        for c in commands:
            for ch in [chr(x) for x in [TileName.DarkDoor, TileName.LightDoor, TileName.DoorBottom, TileName.DoorTop, TileName.DoorwayTop, TileName.DoorBottomLock]]:
                if ch in c.tiles:
                    c.tiles = c.tiles.replace(ch, chr(TileName.JumpThroughBlock))
            for ch in [chr(x) for x in [TileName.LightTrail, TileName.LightTrailRight, TileName.LightTrailLeft]]:
                if ch in c.tiles:
                    c.tiles = c.tiles.replace(ch, chr(TileName.Sky))
            for ch in [chr(x) for x in [TileName.JarTopGeneric, TileName.JarTopNonEnterable, TileName.JarTopPointer]]:
                if ch in c.tiles:
                    c.tiles = c.tiles.replace(ch, chr(TileName.JarTopNonEnterable))
            for ch in [chr(x) for x in [TileName.GrassRocket]]:
                if ch in c.tiles:
                    c.tiles = c.tiles.replace(ch, chr(TileName.GrassPotion))

        my_enemies = [e if e[0] != EnemyName.CrystalBall else (EnemyName.Key, *e[1:]) for e in my_enemies if e[0] not in [EnemyName.HawkmouthBoss, EnemyName.HawkmouthLeft, EnemyName.HawkmouthRight]]


        for cnt, d in enumerate(door_data):
            if room.has_boss or room.is_jar: break
            if d is None: continue
            else:
                my_top_tile = TileName.BridgeShadow if door_type[cnt] != 5 else TileName.Sky
                p = find_sturdy_surface(cnt, my_room_map, room.vertical)
                if p is None:
                    print('FLINCH')
                    positions = [(x,y) for x in range(1, 15) for y in [l for l in range(5, 14)]]
                    random.shuffle(positions)
                    p = positions[0]
                    my_door_tiles = [chr(my_top_tile)]+door_defs[door_type[cnt]]+[chr(TileName.BridgeShadow)]
                    # uh oh... this is a bad condition
                else:
                    my_door_tiles = [chr(my_top_tile)] + door_defs[door_type[cnt]]
                if door_type[cnt] == 4:
                    my_enemies.append((EnemyName.Phanto, p[0], (p[1]), cnt))
                print(room.vertical, cnt, p, d)
                door_command = token.smb2command(0, cnt, p[0], (p[1] - 3), 'VLINEAR', ''.join(my_door_tiles), 0, 999)
                commands.append(door_command)

        if False: # lock boss doors
            distance, max_dist = 0, random.randint(2,4)
            current_room = room_name
            def check_room_depth_key(my_id, meta, distance, max_dist, visited=None):
                sub_info = metadata[my_id]
                visited = set([my_id]) if visited is None else visited
                my_nodes = []
                if EnemyName.Key in [x[0] for x in sub_info['enemies']] or distance == max_dist:
                    return [my_id]
                for sub in sub_info['connections']:
                    current_room = slots[sub]
                    if current_room not in visited:
                        visited.add(current_room)
                        my_nodes.append(current_room)
                        my_nodes.extend(check_room_depth_key(current_room, metadata, distance + 1, max_dist, visited))
                        visited.discard(current_room)
                return my_nodes
            
            my_nodes = check_room_depth_key(current_room, metadata, distance, max_dist)
            my_nodes = [x for x in my_nodes if x != current_room]
            if len(my_nodes) > 0:
                sub_num = random.choice(my_nodes)
                sub_info = metadata[sub_num]
                if sub_info and EnemyName.Key not in [x[0] for x in sub_info['enemies']]:
                    sub_data = sub_info['data']
                    sub_map = np.array([(x) for x in sub_data]).reshape((150,16))
                    my_page = random.choice(sub_info['sturdy_pages'])
                    surface = find_sturdy_surface(my_page, sub_map)
                    surface = (surface[0]%16, (surface[1]-1)%15)
                    sub_info['enemies'].append(([EnemyName.Key, *surface, my_page]))
                    sub_info['enemies'].append(([EnemyName.Phanto, surface[0], max(surface[1]-2, 2), my_page]))
                    # print(sub_info['enemies'])

        my_header_bytes = smb2.write_header_bytes(room.header)
        my_level_data = [my_header_bytes + segment for segment in token.commands_to_level(commands, door_data, room.header['pages'])]

        if room.is_jar:
            room.is_jar = 2

        levels_data.append(
            SimpleNamespace(**{
                "world": new_world,
                "data": my_level_data,
                "enemies": my_enemies,
                "info": room
            }))

    return levels_data
