from zipfile import ZipFile
from PIL import Image, ImageOps
import json, os, base64
from math import sqrt
from io import BytesIO

NES_palette = [ [124,124,124], [0,0,252], [0,0,188], [68,40,188], [148,0,132], [168,0,32], [168,16,0], [136,20,0], [80,48,0], [0,120,0], [0,104,0], [0,88,0], [0,64,88], [0,0,0], [0,0,0], [0,0,0], [188,188,188], [0,120,248], [0,88,248], [104,68,252], [216,0,204], [228,0,88], [248,56,0], [228,92,16], [172,124,0], [0,184,0], [0,168,0], [0,168,68], [0,136,136], [0,0,0], [0,0,0], [0,0,0], [248,248,248], [60,188,252], [104,136,252], [152,120,248], [248,120,248], [248,88,152], [248,120,88], [252,160,68], [248,184,0], [184,248,24], [88,216,84], [88,248,152], [0,232,216], [120,120,120], [0,0,0], [0,0,0], [252,252,252], [164,228,252], [184,184,248], [216,184,248], [248,184,248], [248,164,192], [240,208,176], [252,224,168], [248,216,120], [216,248,120], [184,248,184], [184,248,216], [0,252,252], [248,216,248], [0,0,0], [0,0,0] ]


def load_character_file(my_file):
    if os.path.splitext(my_file)[1] in ['.zip']:
        profile = unpack_character(my_file)
    if os.path.splitext(my_file)[1] in ['.png']:
        profile = image_to_character(my_file)
    return profile


def unpack_character_sheet(my_sheet):
    data = []
    data_img = list(my_sheet.getdata())
    data_img = [data_img[i:i+8] for i in range(0, len(data_img), 8)]
    for b in [data_img[i:i+8] for i in range(0, len(data_img), 8)]:
        byte_l, byte_r = [], []
        for line in b:
            l_bits = [(x&1) > 0 for x in line]
            byte_l.append('0b' + ''.join(['1' if x else '0' for x in l_bits]))
            r_bits = [(x&2) > 0 for x in line]
            byte_r.append('0b' + ''.join(['1' if x else '0' for x in r_bits]))
        data.extend([int(x, base=2) for x in byte_l])
        data.extend([int(x, base=2) for x in byte_r])
    return data


def colorDifference (pal1, pal2):
    return sqrt(sum([(c1 - c2)**2 for c1, c2 in zip(pal1, pal2)]))


def get_nearest_color (color, color_set):
    color = color[:3]
    diff_min = 99999
    target_color = 0
    for c in color_set:
        diff = colorDifference(color, c)
        if (diff < diff_min):
            diff_min = diff
            target_color = c
    return target_color


def unpack_character(zip_file):
    with ZipFile(zip_file) as zf:
        with zf.open('profile.json') as f:
            my_profile = json.load(f)
        my_profile['sheet_data'] = []
        for s in range(4):
            with zf.open('sheet{}.png'.format(s)) as f:
                my_sheet = Image.open(f)
                data = unpack_character_sheet(my_sheet)
                my_profile['sheet_data'].append(data)
        with zf.open('profile.png'.format(s)) as f:
            profile_image = Image.open(f)
            buffered = BytesIO()
            profile_image.save(buffered, format="PNG")
            my_profile['profile_image'] = base64.b64encode(buffered.getvalue())
    return my_profile


def remove_transparency(im):
    # Seriously I Just WANT THE PALETTE TO EXCLUDE ALPHA..
    return im.convert('P')


def image_to_character(image_file):
    # this needs to be reworked a lot, too many lines
    my_img = remove_transparency(Image.open(image_file))

    file_name = os.path.basename(image_file.split('.')[0])
    if ',' in file_name:
        cmds = [x for x in reversed(file_name.split(','))]
        my_name = cmds.pop()
        long = any([x in cmds for x in ['wide', 'long']])
    else:
        cmds = []
        my_name = file_name
        long = False

    print('Character Commands:', cmds)

    all_tiles, et_tiles = [], {}
    frame_data, frame_meta = [], []
    frame_ex, frame_ex_meta = [], []
    background_color = my_img.convert('RGB').getpixel((0,0))
    profile_image = Image.new('RGB', (32, 32), color=background_color)
    if long: profile_image.paste( my_img.crop((0,0, 24, 32)), (4,0) )
    else: profile_image.paste( my_img.crop((0,0, 16, 32)), (8,0) )
    profile_image = ImageOps.scale(profile_image, 3, Image.NEAREST)

    def frame_compare(half, frame_data, frame_meta, et_tiles):
        id, id_flip = tuple(half.getdata()), tuple(list(half.getdata())[:-1])
        if all([x == 0 for x in id]):
            frame_data[-1].append(0xFB); frame_meta[-1].append(False); return
        if id_flip in et_tiles:
            id = id_flip; frame_meta[-1].append(True)
        else:
            frame_meta[-1].append(False)
        if id not in et_tiles:
            et_tiles[id] = len(et_tiles)
            all_tiles.append(half)
        index = et_tiles[id]
        frame_data[-1].append(index)

    # I don't think we need so much in TWO seperate sets of loops...
    # can probably combine these
    # I Wrote all this with a really poor understanding of image manipulation and numpy...
    frame_num = 12
    if long:
        for row_cnt, row in enumerate([my_img.crop((0, y, my_img.width, y + 32)) for y in range(0, my_img.height, 32)]):
            for spr in [row.crop((x, 0, x + 24, 32)) for x in range(0, my_img.width, 24)]:
                frame_data.append([]); frame_meta.append([]);
                for half in [spr.crop(p) for p in [(0,0,8,16), (0,16,8,32)] + [(8,0,16,16), (16,0,24,16), (8,16,16,32), (16,16,24,32)]]:
                    frame_compare(half, frame_data, frame_meta, et_tiles)
                frame_meta[-1] = frame_meta[-1][2:]
            if len(frame_data) < frame_num: continue
            elif len(frame_data) % frame_num > 0: raise ValueError('Incorrect number of frames')
            else: break
        row_cnt += 1
        my_img = my_img.crop((0, row_cnt*32, my_img.width, my_img.height))

        
    for row in [my_img.crop((0, y, my_img.width, y + 32)) for y in range(0, my_img.height, 32)]:
        for spr in [row.crop((x, 0, x + 16, 32)) for x in range(0, my_img.width, 16)]:
            frame_data.append([]); frame_meta.append([])
            for half in [spr.crop(p) for p in [(0,0,8,16), (8,0,16,16), (0,16,8,32), (8,16,16,32)]]:
                frame_compare(half, frame_data, frame_meta, et_tiles)

    main_sprites = frame_data[:(frame_num*2)]
    main_meta = frame_meta[:frame_num*2]
    sheets, player_frames, used_sprites, uses_sheet = [], [], [], []
    for cnt, player_sheet in enumerate([main_sprites[i:i+frame_num] for i in range(0, len(main_sprites), frame_num)]):
        sheet_num = cnt*2
        while len(player_frames) < sheet_num + 1:
            used_sprites.append({}); player_frames.append([])
            sheets.append(Image.new('P', (8, 16*8*4)))
        for full_sprite in player_sheet:
            sprite_length = len([s for s in set(full_sprite) if s not in used_sprites[-1]])
            if sprite_length + len(used_sprites[-1]) >= 27:
                used_sprites.append({}); player_frames.append([])
                sheets.append(Image.new('P', (8, 16*8*4)))
            for s in full_sprite:
                if s == 0xFB:
                    continue
                if s not in used_sprites[-1]:
                    spr_pos = len(used_sprites[-1])
                    spr_pos = spr_pos + 4 if spr_pos >= 26 else spr_pos
                    position = (0, (spr_pos*16))
                    sheets[-1].paste(all_tiles[s], position)
                    used_sprites[-1][s] = len(used_sprites[-1])
            player_frames[-1].append([used_sprites[-1][s] if s != 0xfb else 0xfb for s in full_sprite])
            if len(player_frames[-1][-1]) == 6:
                frame_ex.append(player_frames[-1][-1][:2])
                player_frames[-1][-1] = player_frames[-1][-1][2:]
            uses_sheet.append(len(sheets) - 1)
    while len(sheets) < sheet_num + 2:
        player_frames.append([])
        sheets.append(Image.new('P', (8, 16*8*4)))
    [sheet.putpalette([0,0,0,64,64,64,128,128,128,178,178,178]*64) for sheet in sheets]

    # select/victory sprites
    sub_sprites = frame_data[(frame_num*2):]
    sub_meta = frame_meta[(frame_num*2):]
    bonus_sprites = []
    position = 0
    for sprite, meta in zip(sub_sprites, sub_meta):
        position = 0
        bonus_sprites.append(Image.new('P', (8, 64)))
        for s,m in zip(sprite, meta):
            my_tiles = Image.new('P', (8, 16)) if s == 0xfb else all_tiles[s]
            my_tiles = my_tiles if not m else ImageOps.mirror(my_tiles)
            bonus_sprites[-1].paste(my_tiles, (0, position))
            position += 16
        bonus_sprites[-1].putpalette([0,0,0,64,64,64,128,128,128,178,178,178]*64)

    my_pal = [x for x in my_img.palette.getdata()[1]][0:16]
    my_nes_pal = []
    if my_img.palette.mode == 'RGB':
        for p in range(0,12,3):
            p = my_pal[p:p+3]
            my_color = get_nearest_color (tuple(p), NES_palette)
            my_nes_pal.append(NES_palette.index(my_color))
    else:
        for p in range(0,16,4):
            p = my_pal[p:p+3]
            my_color = get_nearest_color (tuple(p), NES_palette)
            my_nes_pal.append(NES_palette.index(my_color))

    profile = {
                'name': my_name,
                'player_frames': [item for sublist in player_frames for item in sublist],
                'palette': my_nes_pal,
                'sheet_num': uses_sheet,
                'meta_info': main_meta,
                'ex_frames': frame_ex,
                'ex_meta': frame_ex_meta,
                'carry': [256-12,256-4,14,6],
                **{x:False for x in CHAR_FLAGS}
            }
    while len(cmds):
        cmd = cmds.pop().lower()
        if cmd in CHAR_FLAGS:
            profile[cmd] = True
        if cmd in ['carry']:
            carry_info = []
            [carry_info.append((256 - int(cmds.pop())) % 256 ) for x in range(2)]
            [carry_info.append(min(abs(int(cmds.pop())), 16)) for x in range(2)]
            profile['carry'] = carry_info

    profile['sheet_data'] = [unpack_character_sheet(x) for x in sheets]
    profile['extra_data'] = [unpack_character_sheet(x) for x in bonus_sprites]

    buffered = BytesIO()
    profile_image.save(buffered, format="PNG")
    profile['profile_image'] = base64.b64encode(buffered.getvalue())
    return profile

CHAR_ORDER, CHAR_ORDER_SELECT = [0, 3, 1, 2], [0, 1, 3, 2]
SHEET_NUMS = [0, 0x3c, 4, 0x80]
EYEFRAME_NUM = 0x3E
    
CHAR_FLAGS = {
    'wide': 0b1000000,
    'stand': 0b1,
    'flutter': 0b100,
    'pwalk': 0b1000,
    'bjump': 0b10000,
    'smb1': 0b100000,
    }

def apply_characters_to_rom(my_rom, list_of_char, my_mem_locs):
    for char_num, my_profile in enumerate(list_of_char):
        if not isinstance(my_profile, dict):
            continue
        mem_loc =  0x40000 # hardcoded to expanded PRG/CHR
        poof_tiles = my_rom[mem_loc+0x340:mem_loc+0x3C0]
        char_num = CHAR_ORDER_SELECT[char_num]

        for s in range(4):
            data = my_profile['sheet_data'][s]
            mem_loc = SHEET_NUMS[s] * 0x400 + 0x40000 + 0x400 * char_num
            my_rom[mem_loc:mem_loc+0x400] = data
            my_rom[mem_loc+0x340:mem_loc+0x3C0] = poof_tiles
            eye_sprite = my_profile['extra_data'][4][64:96]
            my_rom[mem_loc+0x3E0:mem_loc+0x400] = eye_sprite
            mem_loc = my_mem_locs['CharacterEyeTiles'] + CHAR_ORDER[char_num]
            my_rom[mem_loc] = EYEFRAME_NUM

        char_num_a = CHAR_ORDER[char_num]
        char_num_b = CHAR_ORDER_SELECT[char_num]

        lar = 'Character{}_Frames'.format(['One', 'Two', 'Tre', 'Four'][char_num_a])
        mem_loc_frames = [my_mem_locs[lar], my_mem_locs[lar+'Small']]
        player_frames = my_profile['player_frames']
        player_frames = [player_frames[:len(player_frames)//2], player_frames[len(player_frames)//2:]]
        for cnt, sheet_set in enumerate(player_frames):
            mem_loc = mem_loc_frames[cnt]
            sheet_set = [l*2 if l < 0x80 else 0xFB for s in sheet_set for l in s]
            my_rom[mem_loc:mem_loc+len(sheet_set)] = bytearray(sheet_set)

        lar = 'Character{}MetaFrames'.format(['One', 'Two', 'Three', 'Four'][char_num_a])
        mem_loc_frames = [my_mem_locs[lar], my_mem_locs[lar+'Small']]
        meta_frames = my_profile['meta_info']
        meta_frames = [meta_frames[:len(meta_frames)//2], meta_frames[len(meta_frames)//2:]]

        lar = 'ExtraFrames{}'.format(['One', 'Two', 'Tre', 'For'][char_num_a])
        mem_loc = my_mem_locs[lar]
        ex_frames = [item*2 if item < 0x80 else 0xfb for sublist in my_profile['ex_frames'] for item in sublist]
        my_rom[mem_loc:mem_loc+len(ex_frames)] = ex_frames

        for cnt, meta_set in enumerate(meta_frames):
            mem_loc = mem_loc_frames[cnt]
            for m_cnt, m_frame in enumerate(meta_set):
                meta_item = 0
                for pow, m in zip([0,2,1,3], m_frame):
                    meta_item += 2**pow if m else 0
                meta_item += 128 if my_profile['sheet_num'][cnt*len(meta_set) + m_cnt] % 2 > 0 else 0
                my_rom[mem_loc+m_cnt] = meta_item
        
        # CustomCharFlag_Standing = %00000001
        # CustomCharFlag_Running = %00000010 unused
        # CustomCharFlag_Fluttering = %00000100
        # CustomCharFlag_PeachWalk = %00001000
        # CustomCharFlag_WeaponCherry = %00010000 unused
        # CustomCharFlag_StoreCherry = %00100000 unused
        # CustomCharFlag_AirControl = %01000000 unused
        # CustomCharFlag_WideSprite = %10000000
        mem_loc = my_mem_locs['DokiMode'] + char_num_a
        my_rom[mem_loc] = 0
        for x in CHAR_FLAGS:
            if my_profile.get(x):
                my_rom[mem_loc] |= CHAR_FLAGS[x]
        
        mem_loc = my_mem_locs['CarryYOffsetBigLo'] + char_num_a
        my_rom[mem_loc] = my_profile['carry'][0]
        my_rom[mem_loc+4] = 0xFF if my_profile['carry'][0] > 128 else 0
        my_rom[mem_loc+8] = my_profile['carry'][1]
        my_rom[mem_loc+12] = 0xFF if my_profile['carry'][1] > 128 else 0

        mem_loc = my_mem_locs['MarioPalette'] + char_num_a*4
        p = [0xf] + my_profile['palette'][1:]
        my_rom[mem_loc:mem_loc+4] = bytes(p)
            
        mem_loc = my_mem_locs['PlayerSelectSpritePalettes_Mario'] + char_num_b*7 + 3
        my_rom[mem_loc:mem_loc+4] = bytes(p)
        
        mem_loc = my_mem_locs['CharacterYOffsetCrouch'] + char_num_a
        my_rom[mem_loc] = my_profile['carry'][2]
        my_rom[mem_loc+4] = my_profile['carry'][3]
        
        write_names(my_rom, char_num, my_profile['name'], my_mem_locs)

    bonus_stuff = [[], [], [], []]

    for cnt, char in enumerate([list_of_char[x] for x in range(4)]):
        if not isinstance(char, dict):
            for s in range(4):
                mem_loc = 48 * 0x400 + 0x40000 + 0x200 * s + 0x80 * cnt
                bonus_stuff[s].append(my_rom[mem_loc:mem_loc+0x80])
        else:
            for s in range(4):
                bonus_stuff[s].append(char['extra_data'][s])

    for cnt in range(4):
        mem_loc = 48 * 0x400 + 0x40000 + 0x200 * cnt
        my_rom[mem_loc:mem_loc+0x200] = [item for sublist in bonus_stuff[cnt] for item in sublist]

def write_names(my_rom, char_num, name, my_mem_locs):
    char_num_a = CHAR_ORDER[char_num]

    mem_loc = my_mem_locs['TEXT_Mario'] + 4 + 13*char_num_a
    my_rom[mem_loc:mem_loc+8] = list([ord(x) + 0x99 for x in name.upper()]+[0xfb]*8)[:8]

    mem_loc = my_mem_locs['EndingCelebrationText_MARIO'] + 4 + 13*char_num_a
    my_rom[mem_loc:mem_loc+8] = list([ord(x) + 0x99 for x in name.upper()]+[0xfb]*8)[:8]

def paste_character_image(data, overlay):
    my_img = Image.open(data)
    lock = Image.open(overlay)
    my_img.paste(lock, (0,0), lock)
    buffered = BytesIO()
    my_img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue())

def base64_to_bytesio(item):
    return BytesIO(base64.b64decode(item))
