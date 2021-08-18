import argparse
import glob, json, os, re, shutil

import game_lib.smb2 as smb2
from game_lib.smb2 import EnemyName, TileName, ClimbableTiles, DoorTiles
from game_lib.level_tokenize import level_h, tokenize

file_defaults = {
    # "layers": [],
    # "tilesets": [],
    # "properties": [],
    "backgroundcolor":"#55aaff",
    "orientation":"orthogonal",
    "renderorder":"right-down",
    "tiledversion":"1.7.1",
    "tileheight":16,
    "tilewidth":16,
    "type":"map",
    "version":"1.6",
    "compressionlevel":-1,
    "infinite":False,
    "height":15,
    "width":16
}

layer_defaults = {
    "name":"Level", "type":"tilelayer",
    "id":1, "opacity":1, "visible":True,
    "x":0, "y":0
}

emy_defaults = {
    "name":"Enemies", "type":"objectgroup",
    "id":2, "opacity":0.5, "visible":True, 
    "x":0, "y":0
}
obj_default = {
        # "gid":1,
        "height":16,
        "width":16,
        # "id":1,
        # "name":"",
        "rotation":0,
        # "type":"",
        "visible":True,
        # "x":544,
        # "y":80
    }

custom_defaults = {
        "name":"fff",
        "type":"string",
        "value":"ff"
    }

trans_name = 'transition_page{}'

def handle_dir(dir):
    my_files = glob.glob(os.path.join(dir, '*.json'))
    my_files.sort(key=lambda f: int(re.sub('\D', '', f)))
    my_levels = [my_files[i:i+10] for i in range(0, len(my_files), 10)]

    files_to_write = {}

    for level in my_levels:
        jar_accessed = {}
        level_total = []
        for room in level:
            if os.path.isfile(room):
                with open(room) as f:
                    my_level = json.load(f)

                parsed_file = {
                    "id": my_level['my_level_num'],
                    "world": my_level['my_level_world_num'],
                    **smb2.read_header(my_level['my_header'])
                }

                pages = parsed_file["pages"]+1
                isVertical = parsed_file["vertical"]
                final_file = { 
                    "id": my_level['my_level_num'], 
                    "pages": pages-1, **file_defaults }
                final_file['height'] = 15*pages if isVertical else 15
                final_file['width'] = 160 if not isVertical else 16
                h, w = final_file['height'], final_file['width']
                my_level_data = my_level['my_level'] if isVertical else level_h(my_level['my_level'])
                my_enemies = smb2.enemy_data_to_json(my_level['my_enemies'], 11)

                final_file['layers'] = [{
                        "data":[x+1 for x in my_level_data[:h*w]],
                        "height":final_file['height'],
                        "width":final_file['width'],
                        **layer_defaults
                    },
                    {
                        "objects":[
                            {
                                "x":emy[1]*16 + (16*16*(emy[3]) if not isVertical else 0),
                                "y":16 + emy[2]*16 + (16*16*(emy[3]) if isVertical else 0),
                                "page": emy[3],
                                "name":str(EnemyName(emy[0])).split('.')[-1],
                                "gid":emy[0]+257,
                                **obj_default
                            } for emy in my_enemies
                        ],
                        **emy_defaults
                    }
                ]
                final_file['tilesets'] = [
                { "firstgid":1, "source":"tilesets\/world0p0.json" },
                { "firstgid":257, "source":"tilesets\/world1spr0.json" } ]

                doors = my_level['my_ptrs']
                doors = [doors[i:i+2] for i in range(0, len(doors), 2)]
                doors_ptrs = {x: smb2.parse_door_ptr(tuple(doors[x])) for x in range(10) if tuple(doors[x]) != (0,0)}
                for x,ptr in doors_ptrs.items():
                    parsed_file['doorptr_page{}'.format(x)] = "{},{}".format(ptr[1] + (10 if ptr[0] > parsed_file['id']//10 else 0), ptr[2])

                my_commands = tokenize(my_level_data, not isVertical, True)
                for c in my_commands:
                    if chr(TileName.JarTopGeneric) in c.tiles:
                        jar_accessed[4] = 1
                    if doors_ptrs.get(c.page):
                        my_dest = doors_ptrs[c.page]
                        if chr(TileName.JarTopPointer) in c.tiles:
                            jar_accessed[my_dest[1]] = 2
                            parsed_file[trans_name.format(c.page)] = 'jar'
                        if any([chr(x) in c.tiles for x in smb2.DoorTiles]):
                            parsed_file[trans_name.format(c.page)] = 'door'
                        if not parsed_file.get(trans_name.format(c.page)):
                            if any([chr(x) in c.tiles for x in smb2.ClimbableTiles]):
                                parsed_file[trans_name.format(c.page)] = 'vine'
                    if chr(TileName.SubspaceMushroom1) in c.tiles:
                        parsed_file['mush_1'] = c.page
                    if chr(TileName.SubspaceMushroom2) in c.tiles:
                        parsed_file['mush_2'] = c.page

                final_file['properties'] = [ {
                        "name": x, "value": y,
                        "type": 'int' if isinstance(y, int) else 'string'
                    } for x, y in parsed_file.items() if x != 'vertical' ]
                level_total.append(final_file)

                print(parsed_file)

        # add Jar shiftings
        for x in level_total:
            is_jar_prop = { "name": 'is_jar', "type": 'int', "value": 0 }

            if x['id']%10 in jar_accessed:
                is_jar_prop['value'] = jar_accessed[x['id']%10]

            if is_jar_prop['value'] != 1:
                x['layers'][1]['objects'] = [e for e in x['layers'][1]['objects'] if e['page'] <= x['pages']]
            else:
                for e in x['layers'][1]['objects']: 
                    e['y'] = e['y']%256
                    e['page'] = 0

            x['properties'].append(is_jar_prop)
            print('writing', x['id'])
            my_name = os.path.join('output', '{}.json'.format(x['id']))
            with open(my_name, 'w') as f:
                json.dump({k:v for k,v in x.items() if k not in ['id', 'pages']}, f, indent=2)
            
    

if __name__ == '__main__':
    argget = argparse.ArgumentParser(description='RAW to Tiled')

    # config
    argget.add_argument('dir', type=str, help='dir_of_raws')
    argget.add_argument('tileset_dir', type=str, help='dir_of_tilesets_dir')
    args = argget.parse_args()

    output_dir = os.path.join(args.dir, 'output')
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    
    output_tilesets = os.path.join(output_dir, 'tilesets')

    try:
        shutil.copytree(args.tileset_dir, output_tilesets)
    except Exception as e:
        print('Attempted to copy tilesets, proceeding after Exception;;')

    # just work in that dir from now on
    os.chdir(args.dir)

    handle_dir('./')





