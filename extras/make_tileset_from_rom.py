import argparse
import os, sys


NES_palette = [
    [124,124,124], [0,0,252], [0,0,188], [68,40,188], [148,0,132], [168,0,32], [168,16,0], [136,20,0], [80,48,0], [0,120,0], [0,104,0], [0,88,0], [0,64,88], [0,0,0], [0,0,0], [0,0,0], [188,188,188], [0,120,248], [0,88,248], [104,68,252], [216,0,204], [228,0,88], [248,56,0], [228,92,16], [172,124,0], [0,184,0], [0,168,0], [0,168,68], [0,136,136], [0,0,0], [0,0,0], [0,0,0],
    [248,248,248], [60,188,252], [104,136,252], [152,120,248], [248,120,248], [248,88,152], [248,120,88], [252,160,68], [248,184,0], [184,248,24], [88,216,84], [88,248,152], [0,232,216], [120,120,120], [0,0,0], [0,0,0], [252,252,252], [164,228,252], [184,184,248], [216,184,248], [248,184,248], [248,164,192], [240,208,176], [252,224,168], [248,216,120], [216,248,120], [184,248,184], [184,248,216], [0,252,252], [248,216,248], [0,0,0], [0,0,0]
]

def extract_tile_bytes(contents, mem_locs={}):
#     // 8000, 16 * 7, 12 * 3
        mem_loc = mem_locs['WorldBackgroundPalettePointersHi']
        mem_loc_2 = mem_locs['WorldBackgroundPalettePointersLo']
        pal_ptrs = [mem_locs['prg-6-7'] + ((x<<8) + y) - 0x8000 for x, y in zip(
            contents[mem_loc:mem_loc+14], contents[mem_loc_2:mem_loc_2+14]
        )]
        print(pal_ptrs)
        b_pals = [[(y) for y in contents[x:x+16*8]] for x in pal_ptrs[:7]]
        b_pals = [[x[i:i+4] for i in range(0, len(x), 4)] for x in b_pals]
        print(b_pals)
        s_pals = [[(y) for y in contents[x:x+12*4]] for x in pal_ptrs[7:]]
        s_pals = [[x[i:i+4] for i in range(0, len(x), 4)] for x in s_pals]
        print(s_pals)

        mem_loc = mem_locs['TileQuadPointersLo']
        mem_loc_2 = mem_locs['TileQuadPointersHi']
        quad_ptrs = [mem_locs['prg-30-31'] + ((x<<8) + y) - 0xc000 for x, y in zip(
                contents[mem_loc_2:mem_loc_2+4], contents[mem_loc:mem_loc+4]
            )]
        print([(x) for x in quad_ptrs])
        quad_data = [[(y) for y in contents[x:x+256]] for x in quad_ptrs]
        quads = [[q[i:i+4] for i in range(0, len(q), 4)] for q in quad_data ]

        mem_loc = mem_locs['EnemyTilemap1']
        spr_table_1 = [x for x in contents[mem_loc:mem_loc+0x100]]
        spr_table_1 = [spr_table_1[i:i+2] for i in range(0, len(spr_table_1), 2)]
        mem_loc = mem_locs['EnemyTilemap2']
        spr_table_2 = [x for x in contents[mem_loc:mem_loc+0x100]]
        spr_table_2 = [spr_table_2[i:i+2] for i in range(0, len(spr_table_2), 2)]

        return b_pals, s_pals, quads, spr_table_1, spr_table_2

def extract_chr(my_rom):
    pass

if __name__ == '__main__':
    argget = argparse.ArgumentParser(description='Test Description')

    # config
    argget.add_argument('file', type=str, help='filename')
    argget.add_argument('world', type=int, help='filename')
    argget.add_argument('--spr', action='store_true')
    args = argget.parse_args()

    from os import path
    sys.path.insert(0, os.path.split( sys.path[0] )[0])
    import lib.disasm as disasm
    with open(args.file, 'rb') as f:
        my_rom = bytearray(f.read())
        print(args.file)
        _my_header, my_rom = my_rom[:16], my_rom[16:]
    with open(os.path.join( os.path.dirname(args.file), 'smb2.lst' )) as f:
        my_mem_locs = disasm.getMemoryLocationsFromLst(f.read(), bank_num=8)

    b_pal, s_pal, quads, tbl_1, tbl_2 = extract_tile_bytes(my_rom, my_mem_locs)
    print(tbl_1, tbl_2)

    world_sheet = [0x10, 0x12, 0x10, 0x14, 0x0a, 0x10, 0x16][args.world]
    world_sheet_enemy = [0xc, 0xd, 0xc, 0xe, 0xd, 0xc, 0xf][args.world]

    my_chr = my_rom[0x40000:]
    a_s = [my_chr[i:i + 0x400] for i in range(0, len(my_chr), 0x400)]

    if not args.spr:
        loaded_sheets = [item for sublist in\
        [a_s[world_sheet], a_s[world_sheet + 1], a_s[0x18], a_s[0x19]] for item in sublist]
    else:
        loaded_sheets = [item for sublist in\
        [a_s[0x0], a_s[0x8], a_s[0x9], a_s[world_sheet_enemy],
        a_s[world_sheet], a_s[world_sheet + 1], a_s[0x18], a_s[0x19]] for item in sublist]

    my_pal = b_pal[args.world][0]

    from PIL import Image, ImageOps
    import numpy
    my_bits = []
    sprite_by_num = []
    sheet_count = len(loaded_sheets) // 1024
    for x in range(0,1024*sheet_count,16):
        my_bits = []
        l, r = loaded_sheets[x:x + 8], loaded_sheets[x + 8: x + 16]
        for x, y in zip(l, r):
            bits = []
            # print(x, y)
            for p in range(8):
                my_bit_num = (((x) >> (7 - p)) & 1) +\
                    2*(((y) >> (7 - p)) & 1)
                my_color = my_pal[my_bit_num] % 64
                bits.extend((my_bit_num,))
            my_bits.extend(bits)
            # print(bits)
            # print(l, r)
        sprite_by_num.append(my_bits)



    if not args.spr:
        image_data = Image.new('RGB', (16*16, 16*4*4))
        world = args.world
        for pal_num in range(7):
            for num, table in enumerate(quads):
                pal = [NES_palette[x] for x in b_pal[world][num + 4*pal_num]]
                quad_table = []
                tile = []
                for quad in table:
                    data = [sprite_by_num[x] for x in quad]
                    sprites = [Image.frombytes('RGB', (8,8), bytes([item for sublist in [pal[x] for x in x] for item in sublist] ), 'raw', 'RGB') for x in data]
                    idata = Image.new('RGB', (16,16))
                    positions = [(0,0), (8,0), (0,8), (8,8)]
                    [idata.paste(x, box=p) for x,p in zip(sprites, positions)]
                    tile.append(idata)
                    # image_data = Image.frombytes('L', (8*4,8*4), bytes([x*64 for x in data]), 'raw', 'L')
                [image_data.paste(x, box=((cnt%16)*16, num*64+(cnt//16)*16)) for cnt,x in enumerate(tile)]
            # sheet = Image.new('L', (16, 16))
            # for cnt, im in enumerate(image_data):
            #     sheet.paste(im, ((cnt%2)*4, (cnt//2)*2))
            #     sheet.show()
            image_data.save('world{}p{}.png'.format(world, pal_num))
    else:
        image_data = Image.new('RGB', (16*16, 16*4*4))
        mem_loc = my_mem_locs['EnemyAnimationTable']
        anim_table = my_rom[mem_loc:mem_loc+256]
        print(anim_table)
        mem_loc = my_mem_locs['ObjectAttributeTable']
        attrib_table = my_rom[mem_loc:mem_loc+256]
        my_s_pal = [(x & 0b11) for x in attrib_table]
        mirrored = [(x & 0b10000) > 0 for x in attrib_table]
        mem_loc = my_mem_locs['EnemyArray_46E_Data']
        draw_table = [(x & 0x10) > 0 for x in my_rom[mem_loc:mem_loc+256]]
        world = args.world
        print(draw_table)
        print(mirrored)
        for pal_num in range(4):
            tile = []
            for x in range(0,128):
                if 0x4b <= x < 0x5c:
                    idata = Image.new('RGB', (16,16), color=(128,0,0))
                    tile.append(idata)
                    continue
                elif x >= 0x5C:
                    x = x % 0x5C + 0x1C
                y = anim_table[x]
                if y == 0xff:
                    idata = Image.new('RGB', (16,16), color=(128,0,0))
                    tile.append(idata)
                    continue
                wow = (my_s_pal[x] + 2)%3
                pal = [(0,127,127)] + [NES_palette[x%64] for x in s_pal[world][wow + 3 * pal_num]][1:]
                y = y//2
                spr = tbl_2[y] if draw_table[x] else tbl_1[y]
                spr = [x + 0xFF if (x & 1) == 1 else x for x in spr]
                spr = [item for sublist in [[x, x+1] for x in spr] for item in sublist]
                print(x, spr, [x for x in (tbl_2[y] if draw_table[x] else tbl_1[y])], mirrored[x], my_s_pal[x], draw_table[x])
                data = [sprite_by_num[x] for x in spr]
                sprites = [Image.frombytes('RGB', (8,8), bytes([item for sublist in [pal[x] for x in x] for item in sublist] ), 'raw', 'RGB') for x in data]
                if mirrored[x]:
                    sprites = sprites[:2] + [ImageOps.mirror(x) for x in sprites[2:]]
                idata = Image.new('RGB', (16,16))
                positions = [(0,0), (0,8), (8,0), (8,8)]
                [idata.paste(x, box=p) for x,p in zip(sprites, positions)]
                tile.append(idata)
                # image_data = Image.frombytes('L', (8*4,8*4), bytes([x*64 for x in data]), 'raw', 'L')
            [image_data.paste(x, box=((cnt%16)*16, (cnt//16)*16)) for cnt,x in enumerate(tile)]
            image_data.save('tilesets/world{}spr{}.png'.format(world, pal_num))
        # sheet = Image.new('L', (16, 16))
        # for cnt, im in enumerate(image_data):
        #     sheet.paste(im, ((cnt%2)*4, (cnt//2)*2))
        #     sheet.show()

