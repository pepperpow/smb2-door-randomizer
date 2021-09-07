import random
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
    my_map = [ ['.' for y in range(shape)] for x in range(shape)] # string or (coord, room_obj)
    candidates = []
    occupied, slots, edges = {}, {}, {}
    black_list = set()

    rooms = sorted(rooms, key=lambda x: x.header['pages'] == 0)
    num_of_candidates = {}

    for room_cnt, room in enumerate(rooms):
        slots[room_cnt] = room
        room.flags['my_slot'] = room_cnt
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
                room.flags['coordinates'] = adjusted_coords
                for page, n_pos in enumerate(adjusted_coords):
                    # key = str(room_cnt % 10)
                    # if room.is_jar > 0: key = 'J'
                    # for c in [x for x in commands if x.page == page]:
                    #     if any([chr(x) in c.tiles for x in [TileName.SubspaceMushroom1, TileName.SubspaceMushroom2]]):
                    #         key = 'M'; break
                    # if room.has_boss: key = 'B'
                    my_map[n_pos[0]][n_pos[1]] = (n_pos, room)
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
        if target_pos in num_of_candidates:
            num_of_candidates[target_pos] += [target_room]
        else:
            num_of_candidates[target_pos] = [target_room]

    for target_pos, target_room in candidates:
        target_pos = tuple(target_pos)
        if target_room is None:
            continue
        if target_room is not None and (tuple(target_room) in edges or tuple(target_room) not in occupied):
            continue
        if len(num_of_candidates.get(target_pos)) > 1:
            if target_pos not in occupied:
                my_map[target_pos[0]][target_pos[1]] = 'X'
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
    
    # 2321CVMV2K
    random.shuffle(candidates)
    for room_cnt, boss in enumerate(bosses, len(slots)):
        print(len(bosses), boss)
        for target_pos, target_room in candidates:
            if len(num_of_candidates.get(target_pos)) > 1:
                continue
            if target_room is None or (tuple(target_room) not in occupied or tuple(target_room) in edges):
                continue
            if target_pos in occupied:
                continue
            # 2321CVMV2K
            slots[room_cnt] = boss
            boss.flags['my_slot'] = room_cnt
            boss.flags['coordinates'] = [target_pos] * boss.header['pages']
            edges[tuple(target_pos)] = tuple(target_room)
            edges[tuple(target_room)] = tuple(target_pos)
            my_map[target_pos[0]][target_pos[1]] = (target_pos, boss)
            print(target_pos)
            occupied[tuple(target_pos)] = (room_cnt, 0)
            break

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


def map_stringer(slots, edges_by_level, boss_lock=False):
    levels_data = []
    # normal, dark, light, dark solid, locked, jar
    door_defs = [[chr(TileName.DoorTop), chr(TileName.DoorBottom)],
                    [chr(TileName.DarkDoor)]*2,
                    [chr(TileName.LightDoor)]*2,
                    [chr(TileName.DarkDoor), chr(TileName.DarkDoor), chr(TileName.JumpThroughBrick)],
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

        commands = [x for x in token.tokenize(room.data, not room.vertical, True)]
        
        door_data = []
        door_type = []
        for p in range(10):
            my_edge = edges_by_level.get((room_cnt, p))
            if my_edge is not None:
                this_room, this_page = my_edge
                sub_room = slots[this_room]
                if room.has_boss:
                    for p in range(room.header['pages'] + 1):
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
                    elif sub_music == my_music == 0: # outside
                        door_type.append(0)
                    elif sub_music == my_music: # inside
                        door_type.append(0)
                    elif 0 == sub_music < my_music: # inside to outside
                        door_type.append(2)
                    elif sub_music > my_music == 0: # outside to inside
                        door_type.append(1)
                    else:
                       door_type.append(0)
                door_data.append(( this_room//10, this_page + ((this_room%10)<<4) ))
            else:
                door_data.append(None)
                door_type.append(None)


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


        room.flags['doors'] = [n for n, x in enumerate(door_data) if x]
        for cnt, d in enumerate(door_data):
            if room.has_boss or room.is_jar: break
            if d is None: continue
            else:
                # if cnt not in edges_by_level
                if door_type[cnt] == 4:
                    my_top_tile = TileName.Phanto
                else:
                    my_coord_height = room.flags['coordinates'][cnt][0]
                    s_n, s_p = edges_by_level[(room_cnt, cnt)]
                    sub_coord = slots[s_n].flags['coordinates'][s_p][0]
                    my_top_tile = TileName.LightTrailRight if my_coord_height < sub_coord else TileName.LightTrailLeft
                    my_top_tile = TileName.LightTrail if my_coord_height == sub_coord else my_top_tile
                    my_top_tile = TileName.Phanto if door_type[cnt] == 4 else my_top_tile
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
                # room.enemies.append({'type': EnemyName.Phanto, 'x': p[0], 'y': p[1], 'page': cnt})
                print(room.vertical, cnt, p, d)
                door_command = token.smb2command(0, cnt, p[0], (p[1] - 3), 'VLINEAR', ''.join(my_door_tiles), 0, 999)
                commands.append(door_command)


        # if room.has_boss and boss_lock: # lock boss doors
        #     distance, max_dist = 0, random.randint(2,4)

        #     def check_room_depth_key(my_id, distance, max_dist, visited=None):
        #         current_room = slots[my_id]
        #         visited = set([my_id]) if visited is None else visited
        #         my_nodes = []
        #         if EnemyName.Key in [x['type'] for x in current_room.enemies] or distance == max_dist:
        #             return [current_room]
        #         for sub_id in current_room.flags['connections']:
        #             if sub_id not in visited:
        #                 visited.add(sub_id)
        #                 my_nodes.append(slots[sub_id])
        #                 my_nodes.extend(check_room_depth_key(room_cnt, distance + 1, max_dist, visited))
        #                 visited.discard(sub_id)
        #         return my_nodes
            
        #     my_nodes = check_room_depth_key(room_cnt, distance, max_dist)
        #     # my_nodes = [x for x in my_nodes if x and x != current_room]
        #     if len(my_nodes) > 0:
        #         sub_room = random.choice(my_nodes)
        #         if sub_room and EnemyName.Key not in [x['type'] for x in sub_room.enemies]:
        #             # TODO: enemies are not persistent after being processed
        #             # becomes a list of tuples instead of keeping the objects
        #             my_page = random.choice(sub_room.flags['sturdy_pages'])
        #             my_room_2d_array = rotate_me_room(sub_room, sub_room.vertical)
        #             surface = find_sturdy_surface(my_page, my_room_2d_array, sub_room.vertical)
        #             sub_room.enemies.append({'type': EnemyName.Key, 'x': surface[0], 'y': surface[1], 'page': my_page})
        #             sub_room.enemies.append({'type': EnemyName.Phanto, 'x': surface[0], 'y': surface[1], 'page': my_page})

        my_world = room.world
        new_world = room.flags['convert_world'] if my_world < 6 and not room.has_boss else my_world
        new_world = room.flags['convert_world'] if EnemyName.Pidgit not in [e['type'] for e in room.enemies] else my_world
        room.header['unk3'] = new_world

        room.enemies = [e if e['type'] != EnemyName.CrystalBall else {**e, 'type': EnemyName.Key} for e in room.enemies if e['type'] not in [EnemyName.HawkmouthBoss, EnemyName.HawkmouthLeft, EnemyName.HawkmouthRight]]

        if my_world != new_world:
            if room.header['pala'] == 1 and new_world in [3]: # snow doesn't use dark, but we can fix that later
                room.header['pala'] = 0
            for c in commands:
                c.tiles = ''.join([chr(convertMyTile(ord(t), my_world, new_world)) for t in c.tiles])
            
        my_header_bytes = smb2.write_header_bytes(room.header)
        my_level_data = [my_header_bytes + segment for segment in token.commands_to_level(commands, door_data, room.header['pages'])]

        if room.is_jar:
            room.is_jar = 2

        levels_data.append(
            {
                "world": new_world,
                "data": my_level_data,
                "info": room
            })
    
    processed_data = []
    for l in levels_data:
        room = l['info']

        my_enemies = [[e['type'], e['x'], e['y'], e['page']] for e in room.enemies]

        if l['world'] != room.world:
            my_enemies = [convertMyEnemy(e, my_world, new_world) for e in my_enemies]

        processed_data.append(
            SimpleNamespace(**{
                **l,
                'enemies': my_enemies
            }))


    return processed_data

def map_to_html(my_map):
    def format_cell(y):
        if isinstance(y, str): return ''
        output = []
        spot, y = y
        # if y.is_jar or y.has_boss: output.append('special')
        if y.flags['my_slot'] == 0: output.append('start')
        output.append('cell')
        my_doors = [x for x in y.flags['doors']]
        if not y.has_boss:
            my_num = y.flags['coordinates'].index(spot)
        else:
            my_num = 0
        if my_num in my_doors:
            output.append('world{}'.format(y.world%7))
        return ' '.join(output)

    def text_cell(y):
        if isinstance(y, str): return y
        spot, y = y
        if y.flags['my_slot'] == 0: return 'S'
        if y.is_jar: return 'J'
        if y.has_boss: return 'B'
        my_num = y.flags['coordinates'].index(spot)
        for i in ['mush_1', 'mush_2']:
            if my_num == y.header.get(i):
                return 'M,{}'.format(y.flags['my_slot'])
        return y.flags['my_slot']

    def title_cell(y):
        if isinstance(y, str): return 'EMPTY'
        spot, y = y
        my_dict = {x:y for x,y in {**y.header, **y.flags}.items() if x in ['world', 'mush1', 'mush2', 'pages']}
        my_dict['doors'] = [x for x in y.flags['doors']]
        return '\n'.join(([str((x, y)) for x,y in my_dict.items()]))

    me_table = '''<head>\
        <style>\
        td {width: 32px; height: 32px}
        .start {font-size: 30;}\
        .cell {background-color:#CCCCCC}\
        .world0 {background-color:#88E299}\
        .world1 {background-color:#FFE299}\
        .world2 {background-color:#E29292}\
        .world3 {background-color:#BFD6EE}\
        .world4 {background-color:#D6EE}\
        .world5 {background-color:#6EE}\
        .world6 {background-color:#e022}\
        .special {border: 4px dotted black;}\
        </style>\
    </head><html><table>'''
    me_rows = []
    row = '<tr>{}<tr>'
    me_rows.append(row.format(''.join([
        "<td>{}</td>".format(x) for x in ['x'] + list(range(len(my_map[0])))
    ])))
    for num, y in enumerate(my_map):
        my_col = '<td>{}</td>'.format(str(num))
        my_col += ''.join(['<td title="{}" class="{}">{}</td>\n'.format(title_cell(x), format_cell(x), text_cell(x)) for x in y])
        me_rows.append(row.format(my_col))
    me_table = me_table + ''.join(me_rows) + '</table></html>'
    return me_table