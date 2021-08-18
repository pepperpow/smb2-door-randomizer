
import random, copy
from types import SimpleNamespace

import game_lib.smb2 as smb2
from game_lib.smb2 import ClimbableTiles, EnemyName
import game_lib.level_tokenize as token
from game_lib.level_modify import convertMyTile, convertMyEnemy, apply_command

c_rand = ['blue', 'black', 'green', 'purple']
up = [0, -1]
down = [0, 1]
left = [-1, 0]
right = [1, 0]
poses = [up, down, left, right]

# consider: graph theory to manage levels that only go one way...
#   each level starts as a node, and internally has a path to each page or section of pages
#   long since considered using A* pathing to determine this, but for another time or another programmer
def make_next_level_door(dest_room, cnt):
    if dest_room is not None:
        invert, dest_pages = dest_room.flags.get('inverted'), dest_room.header['pages']
        return [cnt + 1, dest_pages if invert else 0]
    else:
        return [cnt + 1, 0]

def level_stringer(my_rom, levels, my_mem_locs):
    """String Levels Together

    Args:
        my_rom (ByteArray): rom
        levels (list): Array of levels (room*10)
        my_mem_locs (dict): Memory Locations in rom

    Returns:
        list: List of levels to write to rom, formatted as {"info": Room, "data": list, "enemies": list, "world": int}
    """
    levels_data = []
    for cnt, choice in enumerate(levels):
        try:
            boss_room = [room is not None and room.has_boss for room in choice].index(True)
        except ValueError:
            boss_room = -1

        for room_cnt, my_room in enumerate(choice, cnt * 10):
            if my_room is None:
                levels_data.append(None)
                continue

            data = my_room.data
            my_enemies = my_room.enemies
            commands = [x for x in token.tokenize(data, horiz=not my_room.vertical, single=True)]

            door_data = []
            # TODO: Write metadata to point to file specifically
            for page in range(10):
                my_door = my_room.doors.get(page, None)
                my_enemy_of_page = [x for x in my_enemies if x['page'] == page]

                if room_cnt == 0 and my_room.flags.get('inverted') and not my_room.vertical:
                    my_rom[my_mem_locs['StartingPage'] + 1] = my_room.header['pages']

                hawkmouth_end = EnemyName.HawkmouthLeft if not my_room.flags.get('inverted') else EnemyName.HawkmouthRight

                if hawkmouth_end in [EnemyName(x['type']) for x in my_enemy_of_page]:
                    if boss_room > -1:
                        door_data.append(([cnt, ( boss_room << 4 )]))
                        my_rom[my_mem_locs['WinLevel']] = cnt * 10 + boss_room 
                    else:
                        try: dest_room = levels[(cnt+1)][0]
                        except Exception: dest_room = None
                        door_data.append(make_next_level_door(dest_room, cnt))
                        my_rom[my_mem_locs['WinLevel']] = room_cnt
                elif my_room.has_boss:
                    try: dest_room = levels[(cnt+1)][0]
                    except Exception: dest_room = None
                    door_data.append(make_next_level_door(dest_room, cnt))
                elif my_door is not None:
                    dest_room = choice[my_door[0]] if my_door[0] < 10 else None
                    if dest_room is not None and dest_room.flags.get('inverted') and not dest_room.vertical:
                        door_data.append([cnt, ( my_door[0] << 4 ) + dest_room.header['pages'] - my_door[1]])
                    else:
                        door_data.append([cnt, ( my_door[0] << 4 ) + my_door[1]])
                else:
                    door_data.append(None)

            my_world = my_room.world
            new_world = my_room.flags['convert_world'] if my_world < 6 and not my_room.has_boss else my_world
            my_room.header['unk3'] = new_world
            my_enemies = [[e['type'], e['x'], e['y'], e['page']] for e in my_enemies]

            if my_world != new_world:
                if my_room.header['pala'] == 1 and new_world in [3]: # snow doesn't use dark, but we can fix that later
                    my_room.header['pala'] = 0
                for c in commands:
                    c.tiles = ''.join([chr(convertMyTile(ord(t), my_world, new_world)) for t in c.tiles])
                
                my_enemies = [convertMyEnemy(e, my_world, new_world) for e in my_enemies]

            my_header_bytes = smb2.write_header_bytes(my_room.header)
            my_level_data = [my_header_bytes + segment for segment in token.commands_to_level(commands, door_data, my_room.header['pages'])]

            levels_data.append(
                SimpleNamespace(**{
                    "world": new_world,
                    "data": my_level_data,
                    "enemies": my_enemies,
                    "info": my_room
                }))
    return levels_data


hawks = [EnemyName.HawkmouthLeft, EnemyName.HawkmouthRight]

# tl.smb2command(0, 4, 9, 12, 'REPEAT', ''.join([chr(TileName.Sky)]*30), 0, 999),

def room_stringer(levels, number_of_levels):
    # TODO: String Rooms together
    all_rooms = [i for sub in levels for i in sub]
    all_start_rooms = [x[0] for x in levels]
    all_end_rooms = [x for x in all_rooms if x and x not in all_start_rooms and len([e for e in x.enemies if EnemyName(e['type']) in hawks])]
    all_boss_rooms = [x for x in all_rooms if x and x.has_boss]
    all_rooms = [r for r in all_rooms if r not in all_start_rooms + all_end_rooms + all_boss_rooms]
    rooms_by_door_size = {x:[] for x in range(11)}
    for r in all_rooms:
        if r: rooms_by_door_size[len(r.doors)].append(r)
    my_levels = []
    for _ in range(number_of_levels):
        my_new_level = []
        start = copy.deepcopy(random.choice(all_start_rooms))
        end = copy.deepcopy(random.choice(all_end_rooms))

        start_entrance = sorted(start.doors.keys())[-1]

        if len(end.doors) == 1:
            end_entrance = 0
        else:
            valid_doors = [x for x in end.doors if end.doors[x][0] < 10]
            end_entrance = sorted(valid_doors)[0]

        print(start_entrance, end_entrance, len(start.doors), len(end.doors))

        start.doors[start_entrance] = (1, end_entrance)

        end.doors[end_entrance] = (0, start_entrance)

        my_new_level += [start, end] + [None]*8
        my_levels.append(my_new_level)
    return my_levels

