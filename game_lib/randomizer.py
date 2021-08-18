import random, copy
from binascii import crc32

import game_lib.smb2 as smb2
import game_lib.level_modify as modify
import game_lib.level_builder as builder
import game_lib.character as character

def write_seed_to_screen(my_rom, my_mem_locs, text):
    for cnt, line in enumerate(text, 2):
        line_loc = my_mem_locs['FunkyLittleSeedBlock'+str(cnt if cnt > 1 else '')] + 3
        my_rom[line_loc:line_loc+len(line)] = [smb2.char_to_tbl[ord(x)] for x in line]


def randomize_rom(my_rom, my_mem_locs, values, game):
    """
    Randomizer our Rom File
    """    
    my_new_rom = copy.copy(my_rom)
    current_seed = values['seed']
    event, metadata = values['event'], values['meta']

    # Rom Setup part 1
    # TODO: yeah part 1 and 2 could be reduced to a few lines with proper keys
    random.seed(current_seed)

    my_k = values['levelAmount'] if 'Generate' in event else metadata.get('k', 12)
    my_new_rom[my_mem_locs['StartingTransition'] + 1] = 0
    my_new_rom[my_mem_locs['StartingPage'] + 1] = 0

    if 'Survival' in values['presetCharRule']:
        my_new_rom[my_mem_locs['IndependentLives']] = 1
        my_new_rom[my_mem_locs['SetNumContinues'] + 1] = 0
        my_new_rom[my_mem_locs['ContinueGame'] + 1] = 5 if values['presetBonusLives'] else 3
    else:
        my_new_rom[my_mem_locs['IndependentLives']] = 0
        my_new_rom[my_mem_locs['SetNumContinues'] + 1] = 2
        my_new_rom[my_mem_locs['ContinueGame'] + 1] = 10 if values['presetBonusLives'] else 5

    my_new_rom[my_mem_locs['FreeHealth']] = 10 if values['presetBonusHealth'] else 0

    my_new_rom[my_mem_locs['ContinueGame'] + 1] = max(1, (my_new_rom[my_mem_locs['ContinueGame'] + 1] + values['extraLives']))

    if 'Anytime' not in values['presetCharRule']:
        my_new_rom[my_mem_locs['HandlePlayer_ChangeCharInput']] = 0x60
    if not values['presetSecret']:
        my_new_rom[my_mem_locs['DetectSecret']] = 0x60
    my_new_rom[my_mem_locs['ChampionChance']] = 10

    # Gather infomation about levels
    random.seed(current_seed)
    
    all_levels = [i for sublist in game.worlds for i in sublist if i[0] or any(i)] # remove empty levels
    my_boss_rooms = [x for x in [i for sublist in all_levels for i in sublist] if x is not None and x.has_boss]

    if 'string' in event:
        my_choices = builder.room_stringer(all_levels, my_k)
    else:
        my_choices = random.sample(all_levels, k=my_k)

    # Modify Levels to inject bosses every third Level
    if any(x in event for x in ['basic', 'Linear', 'string']):
        for cnt, level in enumerate(my_choices):
            # print('non-null rooms', len([x for x in my_choices[cnt] if x]))
            my_choices[cnt] = [room if room not in my_boss_rooms else None for room in level]
            if cnt % 3 == 2:
                open_room = my_choices[cnt].index(None)
                # print('open room', open_room)
                my_choices[cnt][open_room] = random.choice(my_boss_rooms)
                print('Adding Boss Room')

    # Set up Level variables and patch Original Levels
    for level in my_choices:
        level_world = random.randint(0,6)
        char_world = random.randint(0,3)
        invert_chance = random.random()
        for room in level:
            if room is None: continue

            if "Force Character" in values['presetCharRule']:
                room.flags['force_character'] = char_world if values['charPer'] == 'level' else random.randint(0,3)

            if room.has_boss or any([e['name'] in [smb2.EnemyName.Birdo, smb2.EnemyName.HawkmouthBoss] for e in room.enemies]):
                room.flags['boss_health'] = random.randint(values['bossMin'], values['bossMax'])

            if values['presetInvert'] and not room.has_boss:
                invert_chance = invert_chance if values['invertPer'] == 'level' else random.random()
                if invert_chance*100 < values['invertChance']:
                    room.data, room.enemies, room.doors = modify.invert_level(room)

            if values['presetWorldShuffle'] and not room.has_boss and not room.is_jar:
                room.flags['convert_world'] = level_world if values ['worldPer'] == 'level' else random.randint(0,6)
            else:
                room.flags['convert_world'] = room.world

        # patch levels if they need them here
    
    if any(x in event for x in ['basic', 'Linear', 'string']):
        rooms_data = builder.level_stringer(my_new_rom, my_choices, my_mem_locs)
        write_rooms_to_rom(my_new_rom, rooms_data, my_mem_locs)
        my_new_rom[my_mem_locs['BossCondition']] = 0

    # print('Winning Level ID', my_new_rom[my_mem_locs['WinLevel']])
    print('TransitionSTart', my_new_rom[my_mem_locs['StartingTransition'] + 1])
    print('pageStart', my_new_rom[my_mem_locs['StartingPage'] + 1])

    # Sky Palette Randomizer
    if values['presetSkyShuffle']:
        mem_loc = my_mem_locs['World1BackgroundPalettes']
        for x in range(0, 7*4*(7*4 + 3*3), 4):
            my_sky = my_new_rom[mem_loc + x]
            if my_sky in [0xff]:
                continue
            elif my_sky > 0x10:
                my_new_rom[mem_loc + x] = random.choice([x for x in range(0x10, 0x1C)] + [x for x in range(0x21, 0x2C)])
            else:
                my_new_rom[mem_loc + x] = random.randint(0x1, 0x0c)

    return my_new_rom

RANDOM_NAMES_EXTRA = [
    'HABBER', 'BABBER', 'BOB',
    'ISLE', 'IWOL', 'YOINK', 'ROBERT'
]

def randomize_characters(my_rom, values, active_chars, mem_locs):
    if values['presetRandomCharacters']:
        char_list = active_chars
        if len(char_list) > 0:
            if len(char_list) < 4:
                char_list = char_list * 4
            char_loaded = [character.load_character_file(x) for x in random.sample(char_list, k=4)] 
            character.apply_characters_to_rom(my_rom, char_loaded, mem_locs)

    if values['presetRandomNames']:
        random_names = [x for x in active_chars]
        random_names = [character.os.path.basename(x).split('.')[0].split(',')[0] for x in random_names]
        random_names = random.choices(random_names + RANDOM_NAMES_EXTRA, k=4)
        for n, x in enumerate(random_names):
            character.write_names(my_rom, n, x, mem_locs)

    # rewrite this to not be agnostic to each player
    # should randomize player palettes built into the game AND from files
    if values['presetRandomCharPal']:
        shuffle_pal(my_rom, mem_locs)

    if values['presetRandomStats']:
        shuffle_stats(my_rom, mem_locs)


def randomize_text(my_rom, values, mem_locs):
    # Custom Text
    current_seed = values['seed']
    event, metadata = values['event'], values['meta']
    my_k = values['levelAmount'] if 'Generate' in event else metadata.get('k', 12)

    custom_text_lines = ['WITH {} LEVELS'.format(my_k) ]
    if my_rom[mem_locs['WinLevel']] != 0xFF:
        custom_text_lines.append('DEFEAT ENDBOSS')
    if my_rom[mem_locs['IndependentLives']] > 0:
        custom_text_lines.append('{} Life Survival'.format(my_rom[mem_locs['ContinueGame'] + 1]))
    custom_text_lines = custom_text_lines[:3]
    while len(custom_text_lines) < 3:
        custom_text_lines.append('')
    custom_text_lines.append('BTN A for Story')

    crc_str = hex(crc32(my_rom[:0x40000])).upper()[2:]
    write_seed_to_screen(my_rom, mem_locs, [
        *custom_text_lines,
        'SEED     {}'.format(current_seed), 
        'PRG CRC32{}{}'.format(' '*(10 - len(crc_str)), crc_str)
    ])

    # TitleStoryText_Line01
    loc = mem_locs['TitleStoryText_Line01']
    og_bytes = my_rom[loc:loc+14*20]
    og_story = ''.join([smb2.reverseTbl.get(x, chr(x-0x99)) for x in og_bytes])
    og_story = ' '.join([og_story[i:i+20].strip() for i in range(0, len(og_story), 20)])

    loc = mem_locs['TEXT_Mario'] + 4
    my_names = [my_rom[x:x+8] for x in [loc + 13*x for x in range(4)]]
    my_names = [''.join([smb2.reverseTbl.get(c, chr(c-0x99)) for c in x]).strip() for x in my_names]
    og_story = og_story.replace('MARIO', random.choice(my_names))

    import textwrap
    og_story = textwrap.fill(og_story, 20).split('\n')
    for x in range(14):
        loc = mem_locs['TitleStoryText_Line01']+20*x
        if x > len(og_story):
            my_rom[loc:loc+20] = [0xFB]*20
        else:
            my_rom[loc:loc+20] = ([smb2.tbl.get(x, 0xCF) for x in og_story[x]] + [0xFB]*20)[:20]



def shuffle_pal(my_rom, my_mem_locs):
    for char_num in range(4):
        char_num_a = character.CHAR_ORDER[char_num]
        char_num_b = character.CHAR_ORDER_SELECT[char_num]
        loc = my_mem_locs['MarioPalette'] + char_num_a*4
        p = my_rom[loc:loc+4]
        for n in range(4):
            if p[n]%0x10 not in [0x0, 0xD, 0xE, 0xF]:
                p[n] = 0x10*(p[n]//0x10) + random.randint(0x1, 0xB)
        for loc in [loc, my_mem_locs['PlayerSelectSpritePalettes_Mario'] + char_num_b*7 + 3]:
            my_rom[loc:loc+4] = bytes(p)


def shuffle_stats(my_rom, my_mem_locs):
    stat_ranges = {
        "pickup": (0,6),
        "jump": (6,12),
        "quicksand": (12,13),
        "float": (13,14),
        "gravity": (14,17),
        "speed": (17,22)
    }
    game_stat_locs = [my_mem_locs[x] for x in ['MarioStats', 'ToadStats', 'LuigiStats', 'PrincessStats']]
    my_stats = {x:[] for x in stat_ranges}
    for loc in game_stat_locs:
        stat_bytes = my_rom[loc:loc+22]
        for stat in stat_ranges:
            a,b=stat_ranges[stat]
            my_stats[stat].append([x for x in stat_bytes[a:b]])

    fix_r = random.choices([0,1,2,3],k=4)
    for stat, stat_data in my_stats.items():
        if stat in ['jump', 'gravity']:
            stat_data = [stat_data[x] for x in fix_r]
        else:
            random.shuffle(stat_data)

    for n, loc in enumerate(game_stat_locs):
        for stat in stat_ranges:
            new_stats = my_stats[stat][n]
            a,b=stat_ranges[stat]
            if stat == 'pickup':
                new_stats = [x + random.randint(-3,4) for x in new_stats]
            if stat == 'float':
                new_stats = [new_stats[0] + random.randint(-10,10)]
            if stat == 'jump':
                jump_no_obj = random.randint(-10,10)
                jump_obj = jump_no_obj + random.randint(0, 10)
                for pos, x in enumerate([jump_no_obj, jump_obj]):
                    new_stats[pos] += x
                    new_stats[pos+2] += x
                    new_stats[pos+4] += x
            if stat == 'gravity':
                change = random.randint(0,1) if new_stats[0] < 4 else random.randint(-1,0)
                new_stats = [new_stats[0]+change, new_stats[1]+change, new_stats[2]]
            if stat == 'run':
                for pos, x in enumerate([random.randint(-6, 4), random.randint(-4, 12), random.randint(-0, 0)]):
                    new_stats[pos] += x
                    new_stats[pos+3] -= x
            print(new_stats, stat)
            my_rom[loc+a:loc+b] = [x if x > 0 else 0 for x in new_stats]


BANK_SIZE = 0x4000

def write_rooms_to_rom(my_rom, room_datas, my_mem_locs):
    new_bank, enemy_bank = [], []
    enemy_locs = my_mem_locs['EnemyData_Level_1_1_Area0']
    bnk_num = 0x7

    for room_cnt, my_room in enumerate(room_datas):
        if my_room is None: continue
        if len(new_bank) + 240 >= BANK_SIZE:
            print('Next_Bank:', bnk_num)
            my_rom[bnk_num*BANK_SIZE: bnk_num*BANK_SIZE + len(new_bank)] = new_bank
            bnk_num += 1
            new_bank = []

        my_data, extra_byte_blocks = [], []
        # 0x634 == tileset
        # 0x4ee == is_jar
        # BossHP = $73F2
        if my_room.info.is_jar != 1:
            my_function = (my_mem_locs['LoadWorldCHRBanks'] % 0x4000) + 0xc000
            my_func_ptr = [my_function >> 8, my_function % 256]
            extra_byte_blocks.append(bytes([0xfc, 0x06, 0x34, 0x01, my_room.world] + [0xfa, *my_func_ptr]))
        if 'boss_health' in my_room.info.flags:
            extra_byte_blocks.append(bytes([0xfc, 0x73, 0xf2, 0x01, (256 + my_room.info.flags['boss_health'])&0xFF ]))
        if 'force_character' in my_room.info.flags:
            extra_byte_blocks.append(bytes([0xfc, 0x00, 0x8f, 0x01, my_room.info.flags['force_character']]))

        my_segments = my_room.data
        final_segment, my_segments = my_segments[-1], my_segments[:-1]
        for segment in my_segments:
            my_data += segment
            my_ptr_loc = 0x8000 + len(new_bank) + len(my_data) + 4
            my_data += [0xfe] + [my_ptr_loc % 256, my_ptr_loc >> 8] + [0xff]
        my_data += final_segment
        for block in extra_byte_blocks:
            my_data += block
        my_data += [0xff, 0xff]

        my_ptr_loc = 0x8000 + len(new_bank)

        # Add Raw Level Data to ROM
        new_bank.extend(bytearray(my_data))

        print('Bank {} Bytes'.format(bnk_num), len(new_bank), '/', BANK_SIZE)

        # Apply new Pointers
        my_rom[my_mem_locs['LevelDataBank'] + room_cnt] = bnk_num
        my_rom[my_mem_locs['LevelDataPointersHi'] + room_cnt] = my_ptr_loc >> 8
        my_rom[my_mem_locs['LevelDataPointersLo'] + room_cnt] = my_ptr_loc % 256

        # Apply new enemy ptrs and data
        my_emy_loc = ( enemy_locs % 0x8000) + len(enemy_bank) + 0x8000
        my_rom[my_mem_locs['EnemyPointers_Level_1_1_Hi'] + ( room_cnt % 10 ) + (room_cnt//10)*20] = my_emy_loc >> 8
        my_rom[my_mem_locs['EnemyPointers_Level_1_1_Lo'] + ( room_cnt % 10 ) + (room_cnt//10)*20] = my_emy_loc % 256
        if my_room.info.is_jar:
            print('IN THIS JAR,', my_room.info.is_jar, [(str(smb2.EnemyName(x[0])), *x[1:]) for x in my_room.enemies])
        enemy_tuples = [tuple(x) for x in my_room.enemies]
        my_amy_bytes = [x for x in smb2.enemies_to_bytes(enemy_tuples, my_room.info.vertical)]
        if my_room.info.is_jar == 1:
            my_amy_bytes = [1]*10 + my_amy_bytes
        enemy_bank.extend(my_amy_bytes)

    my_rom[bnk_num*BANK_SIZE: bnk_num*BANK_SIZE + len(new_bank)] = new_bank
    my_rom[enemy_locs: enemy_locs + len(enemy_bank)] = enemy_bank
