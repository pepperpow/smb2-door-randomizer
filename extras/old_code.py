
# def get_option_pair(layout):
#     # Get value based on type of button we're looking at, boolean if z.Get() returns number from checkbox
#     # Reduce lists of values into a single value if len == 1, strip out elements in object that are just Text '/'
#     # (this is done just cuz I like the slash between two numbers, this will be obvious when other panels are enabled)
#     # (Think this was written purely so we didn't need unique ids for any buttons, but probably overthought about it)
#     my_opts = { x[0].Get(): [z.Get() if not isinstance(z, sg.Checkbox) else z.Get() == 1 for z in y] for x,y in zip(layout['words'], layout['options'])}
#     return {x:y[0] if len(y) == 1 else [z for z in y if z != '/'] for x,y in my_opts.items()}

    # def update_button(self, button, profile):
    #     # update character buttons
    #     if profile is None: my_image = 'icons/char1.png'
    #     if profile in ['Random']: my_image = 'icons/random.png'
    #     if isinstance(profile, dict):
    #         my_image = profile['profile_image']
    #         if self.characters_locked[self.window_num]:
    #             my_image = character.base64_to_bytesio(profile['profile_image'])
    #             my_image = character.paste_character_image(my_image, 'icons/locked.png')
    #         button.Update(image_data=my_image)
    #     elif isinstance(my_image, str):
    #         if self.characters_locked[self.window_num]:
    #             my_image = character.paste_character_image(my_image, 'icons/locked.png')
    #             button.Update(image_data=my_image)
    #         else:
    #             button.Update(image_filename=my_image)

        # character stuff, to reimplement later
        # if 'char' in event:
        #     window_char_layout = [ [sg.Button('Load Custom')],
        #             [sg.Button('Set as Random')],
        #             [sg.Button('Reset to Default')],
        #             [sg.Button('Toggle Lock')],
        #             ]
        #     my_window = sg.Window('char', layout=window_char_layout, keep_on_top=True, force_toplevel=True, grab_anywhere=True, margins=(20, 20))
        #     window_num = int(event[-1])
        #     sub_event, sub_values = my_window.read()
        #     if sub_event in [None, 'Close']: 
        #         pass
        #     if sub_event in ['Load Custom']: 
        #         my_file = sg.PopupGetFile('', file_types=[('character file', '.zip .png')], no_window=True)
        #         self.characters_loaded[window_num] = character.load_character_file(my_file)
        #     if sub_event in ['Set as Random']: 
        #         self.characters_loaded[window_num] = 'Random'
        #     if sub_event in ['Reset to Default']: 
        #         self.characters_loaded[window_num] = None
        #     if sub_event in ['Toggle Lock']: 
        #         self.characters_locked[window_num] = not self.characters_locked[window_num]
        #     profile = self.characters_loaded[window_num]
        #     button = self.window['char{}'.format(window_num)]
        #     self.update_button(button, profile)

        #     print('okay', sub_event)
        #     my_window.close()
        #     return True

        # if event in ['All Default', 'All Random', 'Lock All', 'Unlock All']:
        #     for window_num in range(4):
        #         button = self.window['char{}'.format(window_num)]
        #         if event in ['All Default']: self.characters_loaded[window_num] = None
        #         if event in ['All Random']:  self.characters_loaded[window_num] = 'Random'
        #         if event in ['Lock All']:    self.characters_locked[window_num] = True
        #         if event in ['Unlock All']:  self.characters_locked[window_num] = False
        #         profile = self.characters_loaded[window_num]
        #         self.update_button(button, profile)
        #     return True
    # characters_locked = my_opts['charlock']
    # my_boss_cnt = values['bossCnt'] if 'Generate' in event else metadata.get('boss', 1)
    # my_crys_cnt = values['crysCnt'] if 'Generate' in event else metadata.get('crys', 0)

    # my_new_rom[my_mem_locs['CrystalCondition']] = my_crys_cnt
    # my_new_rom[my_mem_locs['BossCondition']] = my_boss_cnt

    # Rom Setup Options
    # my_starting_equipment = [0, 0, 0]
    # room_chars = []

    # if values['presetSurvival']:
    #     my_new_rom[my_mem_locs['IndependentLives']] = 1
    #     my_new_rom[my_mem_locs['ContinueGame'] + 1] = 5
    #     my_new_rom[my_mem_locs['SetNumContinues'] + 1] = 0
    
            # This isn't applied to linear levels... leaving this for future posterity
            # if 'basegame' in room['path'] and (not any([x in event for x in ['basic', 'Linear', 'string']])):
            #     my_id = room['id']
            #     for c in level_patches.get(tuple(my_id), []):
            #         modify.apply_command(data, c)
            #     room['data'] = data
            #     room['enemies'].extend(enemy_patches.get(tuple(my_id), []))
    # if my_new_rom[my_mem_locs['CrystalCondition']] > 0:
    #     custom_text_lines.append('GET {} CRYSTALS'.format(my_new_rom[my_mem_locs['CrystalCondition']]))
    # if my_new_rom[my_mem_locs['BossCondition']] > 0:
    #     custom_text_lines.append('DEFEAT {} BOSSES'.format(my_new_rom[my_mem_locs['BossCondition']]))
    # if my_new_rom[my_mem_locs['RescueCondition']] > 0:
    #     custom_text_lines.append('Rescue All')

# tbl = [0xFB]*33 + [0xCE] + \
#         [0xFB]*(ord('0') - ord('!') - 1) + \
#         [x + 0x99 + 7 for x in range(48,58)] + \
#         [0xfb] * 7 + \
#         [x + 0x99 for x in range(65,91)] + [0xFB]*6 +\
#         [x + 0x99 for x in range(65,91)] + [0xfb]*5
    # Part 2: Survival
    # if 'rescue' in event.lower() or 'Generate' in event and values['rescueFlag']:
    #     my_new_rom[my_mem_locs['RescueCondition']] = 0x1
    # if (not any(characters_locked) or all(characters_locked)):
    #     if my_new_rom[my_mem_locs['RescueCondition']] > 0 or all(characters_locked):
    #         # my_new_rom[my_mem_locs['CharacterInitialLock']] = random.choice([0b1110, 0b1101, 0b1011, 0b0111])
    #         my_new_rom[my_mem_locs['CharacterInitialLock']] = 0b1110
    # else:
    #     my_new_rom[my_mem_locs['CharacterInitialLock']] = sum([2**x for cnt, x in enumerate([0,1,2,3]) if characters_locked[cnt]])

    # Generate

    if 'Generate' not in event:
    # if values['presetSecret']:
    #     my_starting_equipment[0] = EquipName.Secret
    # item_pool = [EquipName.Fragment]*12 + [EquipName.EquipMush]*3 + [EquipName(x) for x in range(1,16)]
    # invert_rate = curse_rate = 30
    # boss_range = mini_boss_range = [-1, 1]
    else:
        # TODO: put this in one line because :)
        item_pool = [EquipName.Fragment]*my_opts['Mushroom Fragments'] + [EquipName.EquipMush]*my_opts['Mushrooms']
        item_pool_equips = []
        while len(item_pool_equips) < my_opts['Upgrades']:
            item_pool_equips += random.sample([EquipName(x) for x in range(EquipName.PowerThrow,EquipName.EggGlove + 1)], k=15)
        item_pool += item_pool_equips[:my_opts['Upgrades']] + random.choices([x for x in range(24, 24+7)], k = my_opts['Common Items']) + [EquipName.Crystal]*my_opts['Crystals']
        if my_opts['Survival Mode']:
            my_new_rom[my_mem_locs['IndependentLives']] = 1
            item_pool += [EquipName.UnlockM, EquipName.UnlockL, EquipName.UnlockT, EquipName.UnlockP]
        elif my_new_rom[my_mem_locs['RescueCondition']] > 0:
            item_pool += [[EquipName.UnlockM, EquipName.UnlockL, EquipName.UnlockT, EquipName.UnlockP][x] for x in range(4) if characters_locked[x]]
        invert_rate = my_opts['Inverted Rate']*10
        curse_rate = my_opts['Curse Rate']*10
        if my_opts['Start with Secret Detection']:
            my_starting_equipment[0] = EquipName.Secret
        my_new_rom[my_mem_locs['ContinueGame'] + 1] = my_opts['Extra Lives']
        my_new_rom[my_mem_locs['SetNumContinues'] + 1] = my_opts['Continues']
        my_new_rom[my_mem_locs['FreeHealth']] = 16 * my_opts['Extra Hits']
        my_new_rom[my_mem_locs['ChampionChance']] = int(255 * my_opts['Enemy Champion Chance'] / 100)
        boss_range = my_opts['Boss Health Range']
        mini_boss_range = my_opts['Mini-Boss Health Range']

    # if my_opts['Starting Gift']:
    #     my_starting_equipment[1] = random.choice([EquipName.EquipMush]*2 + [EquipName(x) for x in range(1,16)])

    # mem_loc = my_mem_locs['StartingEquipment']
    # my_new_rom[mem_loc:mem_loc+3] = my_starting_equipment

    random.shuffle(item_pool)
    item_pool = [EquipName.Fragment]*10 + item_pool

    # setup levels
            # if random.randrange(0, 1000) < invert_rate and room['has_boss'] == -1:
            #     data, e, d = modify.invert_level(data, room)
            #     room['data'] = data
            #     room['enemies'] = e
            #     room['doors'] = d
            #     room['inverted'] = True
            # room['curse'] = random.randrange(0, 1000) < curse_rate
            # room['mush_item'] = [item_pool.pop() if x > -1 else 0 for x in room['has_mush']]
            # print(room['mush_item'])
            
            # def write
        # my_level_data = [0x00, 0x90, 0x0F, 0xC0, 0x18]
        # Probably stop resetting memory by taking a whole 5 bytes
        # Try at least reducing this by a byte
        # if my_info.get('curse', False):
        #     my_level_data += bytes([0xfc, 0x05, 0xbc, 0x01, 0xff])
        # else:
        #     my_level_data += bytes([0xfc, 0x05, 0xbc, 0x01, 0x00])
        # my_level_data += bytes([0xfe])
        # if 'mush_item' in my_info:
        #     my_level_data += bytes([0xfc, 0x76, 0x00, 0x02, *my_info['mush_item']])
        # if 'hawkmouth' in my_info:
        #     my_level_data += bytes([0xfc, 0x73, 0xF1, 0x01, my_info['hawkmouth']])
        # my_level_data += bytes([0xfc, 0x73, 0xF2, 0x01, np.uint8(my_info.get('boss_hp', 0))])
        # if my_info.get('force_char') is not None:
        #     my_level_data += bytes([0xfc, 0x00, 0x8f, 0x01, np.uint8(my_info.get('force_char', 0))])
            # my_function = (my_mem_locs['CustomCopyChar'] % 0x4000) + 0xc000
            # my_func_ptr = [my_function >> 8, my_function % 256]
            # my_level_data += bytes([0xfa, *my_func_ptr])
        # my_level_data += bytes([0xfc, 0x06, 0x35, 0x1, world_num])



def map_stringer(my_rom, levels, bosses, metadata, my_mem_locs, toggle=False):

    _my_map, slots, edges_by_level = map_maker(levels, bosses, metadata)

    levels_data = []
    for room_cnt in sorted(slots.keys()):
        room_name = slots[room_cnt]
        my_info = room_name

        data = my_info['data']
        _my_pages = my_info['header']['pages'] + 1
        my_room_map = np.array([(x) for x in data]).reshape((150,16))
        for row_num, _row in enumerate(my_room_map):
            if not my_info['header']['vertical']:
                targets = [x for x in range(0, 150, 15)] + [x for x in range(14, 150, 15)] + [x for x in range(13, 150, 15)]
            else:
                targets = [0] +  [x + my_info['header']['pages']*15 for x in [13, 14]]
            if row_num in targets:
                my_room_map[row_num] = [TileName.SolidBrick0 if x in ClimbableTiles else x for x in my_room_map[row_num]]

        data = my_room_map.reshape((150*16,))

        my_enemies = my_info['enemies']
        commands = [x for x in token.tokenize(data, not my_info['header']['vertical'], True)]
        
        door_data = []
        door_type = []
        for p in range(10):
            my_edge = edges_by_level.get((room_cnt, p))
            if my_edge is not None:
                this_room, this_page = my_edge
                sub_room = slots[this_room]
                sub_info = sub_room
                if my_info['has_boss'] > -1:
                    while len(door_data) < my_info['has_boss']:
                        door_data.append(None)
                        door_type.append(None)
                    door_data.append(( this_room//10, this_page + ((this_room%10)<<4) ))
                    break
                elif sub_info['has_boss'] > -1:
                    this_page = 0
                    door_type.append(4)
                else:
                    if sub_info['is_jar'] > 0:
                        door_type.append(5)
                    elif my_info['is_jar'] > 0:
                        door_type.append(-1)
                    elif sub_info['header']['music'] == my_info['header']['music'] == 0:
                        door_type.append(0)
                    elif sub_info['header']['music'] == my_info['header']['music']:
                        door_type.append(1)
                    elif 0 == sub_info['header']['music'] < my_info['header']['music']:
                        door_type.append(2)
                    elif sub_info['header']['music'] > my_info['header']['music'] == 0:
                        door_type.append(1)
                    else:
                       door_type.append(0)
                door_data.append(( this_room//10, this_page + ((this_room%10)<<4) ))
            else:
                door_data.append(None)
                door_type.append(None)

        if my_info['has_boss'] > -1:
            new_world = my_info['world']
        else:
            new_world = my_info['convert_world']
        header = my_info['header']
        header['unk3'] = new_world
        world_num = my_info['world']
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

        for c in commands:
            c.tiles = ''.join([chr(convertTile[new_world].get(ord(x), ord(x))) if ord(x) not in tilesInWorld[world_num] else x for x in c.tiles])
        
        my_enemies = [e for e in my_enemies if e[0] not in [EnemyName.HawkmouthBoss, EnemyName.HawkmouthLeft, EnemyName.HawkmouthRight]]

        my_enemies = [[convertEnemy[new_world].get(e[0], e[0]), e[1], e[2], e[3]] if e[0] not in enemiesInWorld[world_num] else e for e in my_enemies]


        door_defs = [[chr(TileName.DoorTop), chr(TileName.DoorBottom)],
                        [chr(TileName.DarkDoor)]*2,
                        [chr(TileName.LightDoor)]*2,
                        [chr(TileName.DarkDoor), chr(TileName.DarkDoor), chr(TileName.JumpthroughBrick)],
                        [chr(TileName.DoorTop), chr(TileName.DoorBottomLock)],
                        [chr(TileName.JarTopPointer), chr(TileName.JarBottom)],
                        ]

        for cnt, d in enumerate(door_data):
            if my_info['has_boss'] > -1 or my_info['is_jar']:
                break
            if d is None:
                continue
            else:
                p = find_sturdy_surface(cnt, my_room_map)
                if p is None:
                    positions = [(x,y) for x in range(0, 16) for y in [l + cnt*15 + 2 for l in range(13)]]
                    random.shuffle(positions)
                    p = positions[0]
                    # print('WHATAPPEND...', room_cnt, cnt, my_info['header'])
                door_command = token.smb2command(0, cnt, p[0], (p[1] - 3)%15, 'VLINEAR', ''.join([chr(TileName.Sky)]+door_defs[door_type[cnt]]), 0, 999)
                commands.append(door_command)

        if my_info['has_boss'] > -1 and False:
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
        

        my_info['enemies'] = my_enemies

        my_level_data = token.commands_to_level(
            commands, SimpleNamespace(**header), door_data, world_num, my_mem_locs, is_jar=my_info['is_jar'])
        my_level_data = bytearray(smb2.write_header_bytes(header)) + my_level_data
        levels_data.append((my_level_data, world_num, my_enemies, my_info))

    return levels_data


def map_maker(levels, bosses, metadata, toggle=False):
    np.set_printoptions(threshold=np.inf, linewidth=400)
    dimensions = (80, 80)
    my_map = np.empty(dimensions, dtype=object)
    my_map.fill('.')
    candidates = []
    occupied, slots, edges = {}, {}, {}
    black_list = set()
    # pick level
    levels = [x for x in [item for sublist in levels for item in sublist] if x is not None]
    for room_cnt, room_name in enumerate(levels + bosses):
        slots[room_cnt] = room_name
        # if level is Not Valid
        my_info = room_name
        data = my_info['data']
        pages = my_info['header']['pages']
        # invert outside of level_order functions
        my_room_map = np.array([(x) for x in data]).reshape((150,16))
        commands = [x for x in token.tokenize(data, not my_info['header']['vertical'], True)]
        
        # if we are out of candidates (shouldn't happen mid run), start from center
        if len(candidates) == 0:
            candidates = [ ( np.array((dimensions[0]//2,dimensions[1]//2)), None ) ]
        random.shuffle(candidates)

        # create jitter (variations along x or y axis), then shuffle
        my_jitters = [np.array([-x, 0]) for x in range(pages + 1)] if my_info['header']['vertical'] \
            else [np.array([0, -x]) for x in range(pages + 1)] 
        random.shuffle(my_jitters)

        # measure success, if we reach end of a for loop without a position made, we have a problem
        success = False

        my_info['sturdy_pages'] = [x for x in range(pages + 1) if find_sturdy_surface(x, my_room_map)]
        
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
                n_pos = target_pos + jitter
                adjusted_coords = [n_pos + np.array([x, 0]) for x in range(pages + 1)] if my_info['header']['vertical']\
                    else  [n_pos + np.array([0, x]) for x in range(pages + 1)]
                if any([tuple(x) in occupied for x in adjusted_coords]):
                    continue
                try: [my_map[p[0], p[1]] for p in adjusted_coords]
                except: continue
            
                # IF HERE, THEN WE HAVE SOME SUCCESS
                # create our edge, then map out new candidates/overlaps, label our new stuff
                for page, n_pos in enumerate(adjusted_coords):
                    if tuple(n_pos) == tuple(target_pos):
                        solid_success = page in my_info['sturdy_pages']
                        if solid_success and target_room is not None:
                            edges[tuple(n_pos)] = tuple(target_room)
                            edges[tuple(target_room)] = tuple(n_pos)
                if not solid_success: continue
                for page, n_pos in enumerate(adjusted_coords):
                    key = str(room_cnt % 10)
                    if my_info['is_jar'] > 0: key = 'J'
                    for c in [x for x in commands if x.page == page]:
                        if any([chr(x) in c.tiles for x in [TileName.SubspaceMushroom1, TileName.SubspaceMushroom2]]):
                            key = 'M'; break
                    if my_info['has_boss'] > -1: key = 'B'
                    my_map[n_pos[0],n_pos[1]] = key
                    occupied[tuple(n_pos)] = (room_cnt, page)
                # label our new candidate positions
                for page, n_pos in enumerate(adjusted_coords):
                    if my_info['has_boss'] > -1 or my_info['is_jar'] > 0:
                        break
                    solid_success = page in my_info['sturdy_pages']
                    if solid_success:
                        my_new_places = [n_pos + np.array(x) for x in poses if tuple( n_pos + np.array(x) ) not in occupied]
                        for new_n_pos in my_new_places:
                            try:
                                my_map[new_n_pos[0],new_n_pos[1]] = '+'
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
            room_name, page = slots[my_room[0]], my_room[1]
            my_info = room_name
            solid_success = page in my_info['sturdy_pages']
            if solid_success:
                room_name, page = slots[my_target_room[0]], my_target_room[1]
                my_info = room_name
                solid_success = page in my_info['sturdy_pages']
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
        slots[slot]['connections'] = my_nodes

    return my_map, slots, edges_by_level

randomizer_config_form = {
    "Objective": [
        {
            "name": "Default",
            "options": [
                {"tag": "Complete the following objectives, then find a level exit", "options": [ ]},
                {"name": "Defeat Final Boss", "desc": "Require the 'final boss' room to activate a winning exit",
                    "val": True},
                {"name": "Collect X Crystals", "desc": "Find X amount of crystals across the game",
                    "val": 0, "class": "mem_location", "max": 20,
                    "mem_loc_name": "CrystalCondition"},
                {"name": "Defeat X Bosses", "desc": "Defeat X amount of bosses hidden around or at the end of levels",
                    "val": 0, "class": "mem_location", "max": 7,
                    "mem_loc_name": "BossCondition"},
                {"name": "Rescue All Characters", "desc": "Must leave the game with all 4 characters unlocked",
                    "val": False, "class": "mem_location",
                    "mem_loc_name": "RescueCondition"},
            ]
        }
    ],
    "Level Randomization": [
        {
            "name": "Default",
            "options": [
                {"name": "Randomize World Appearance", "desc": "Randomize palette/tiles/music",
                    "val": [ "Per Similar", "Per World", "Per Level", "Per Room" ]},
                {"name": "Randomize Palettes", "desc": "Palette Randomization",
                    "val": False},
                {"name": "Randomize Music", "desc": "Music Randomization",
                    "val": False},
                {"name": "Randomize World Tileset", "desc": "Randomize World Tile appearance (possible softlocks unknown)",
                    "val": False},
                {"name": "Game Scale", "desc": "Number of Levels to compile together",
                    "val": "20", "max": "21"},
                {"name": "Curse Rate", "desc": "Rate at which rooms will spawn an active Phanto",
                    "val": "0.5"},
                {"name": "Inverted Rate", "desc": "Rate at which rooms will be inverted",
                    "val": "0.5"}
            ]
        },
        {
            "name": "World Order Randomizer",
            "options": [
                {"name": "Scramble Levels in World", "desc": "Scramble levels from within a World",
                    "val": False}
            ]
        },
        {
            "name": "Level Order Randomizer",
            "options": []
        },
        {
            "name": "Simple Door Randomizer",
            "options": [
                {"name": "Door Chance", "desc": "Possibility of spawning one of X doors",
                    "val": "60.0", "max": "100"},
                {"name": "Max Possible Doors", "desc": "Max amount of extra doors",
                    "val": "3", "max": "9", "min": "1"}
            ]
        },
        {
            "name": "Door Randomizer V1",
            "options": [
                {"name": "Scramble Levels in Hub", "desc": "Scramble levels from within a Hub, versus linear sets",
                    "val": False},
                {"name": "Continue after Boss Kill", "desc": "Using a continue places at boss door",
                    "val": False},
            ],
            "option_beta": [
                {"name": "Number of Hubs", "desc": "Number of hubs to generate, which can be traversed between",
                    "val": 1, "min": 1, "max": 7}
            ]
        }
    ],
