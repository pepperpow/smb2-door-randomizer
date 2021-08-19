
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
    # my_crys_cnt = values['crysCnt'] if 'Generate' in event else metadata.get('crys', 0)

    # my_new_rom[my_mem_locs['CrystalCondition']] = my_crys_cnt

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
