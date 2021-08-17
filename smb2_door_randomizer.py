import game_lib.randomizer as randomizer
import game_lib.disasm as disasm
import glob, os, random, re
import PySimpleGUI as sg
import threading

import ui_define
valid_seed_chrs = [str(x) for x in range(10)] + [chr(x) for x in range(65,65+26)]

version = 0.45
class Application():
    def __init__(self, filename) -> None:
        self.state = {
            'load_fail': 0,
            'my_header': None,
            'my_rom': None,
            'my_mem_locs': None,
            'thread_state': 0
        }

        self.queue = []

        self.header, self.rom = None, None 

        self.characters_loaded = [None]*4
        self.characters_locked = [False]*4

        self.current_seed = ''.join(random.choices(valid_seed_chrs, k=10))
        
        self.level_sets = {}
        for game in glob.glob(os.path.join('my_levels', '*')):
            game_name = os.path.basename(game)
            my_rooms = glob.glob(os.path.join(game, '*.json'))
            my_rooms.sort(key=lambda f: int(re.sub('\D', '', f)))
            my_levels = [my_rooms[i:i+10] for i in range(0, len(my_rooms), 10)]
            self.level_sets.update({
                '{} World {} Level {}'.format(game_name, 1+(num//3), 1+(num%3) ): level for num, level in enumerate(my_levels)
            })
        self.active_levels = {x:self.level_sets[x] for x in self.level_sets if 'basegame' in x}

        self.characters = []
        for char_set in glob.glob(os.path.join('my_characters', '*')):
            my_char_sets = glob.glob(os.path.join(char_set, '*'))
            for char in my_char_sets:
                self.characters.append(char)
        self.active_chars = [x for x in self.characters if 'base' in x]

        if os.path.isfile(filename):
            self.load_my_rom(filename, True)

        self.window = sg.Window('SMB2 Door Randomizer', ui_define.layout_main, finalize=True)
        self.seed_box = ui_define.seed_box
        self.seed_box.Update(self.current_seed)

        self.extra_settings = {
            "invertChance": 10,
            "extraLives": 0,
            "bossMin": -2,
            "bossMax": 2,
            "worldPer": 'level',
            "invertPer": 'level',
            "charPer": 'level',
        }

    def isRomExist(self):
        # check rom exists
        if self.rom is None:
            sg.PopupError('ROM is not loaded')
            return False
        return True

    def load_my_rom(self, my_file, auto_load=False):
        # global load_fail, my_header, my_rom, my_mem_locs
        with open(my_file, 'rb') as f:
            my_rom_data = bytearray(f.read())
            my_rom = disasm.try_to_patch_this_rom_okay(my_rom_data)
            if my_rom is None and auto_load:
                sg.PopupError('ROM did not autoload correctly, is this a bad ROM?')
            elif my_rom is None and self.state['load_fail'] == 0:
                _yeah = sg.PopupError('This ROM did not patch correctly, this randomizer requires either the original or Revision A of Super Mario Bros. 2 (U).nes.\n' +
                    'If you\'d like to force load the ROM, attempt to load the file again')
                self.state['load_fail'] += 1
            elif my_rom is None:
                if sg.PopupYesNo('This ROM did not patch correctly, would you like to force load this ROM?') == 'Yes':
                    my_rom = disasm.try_to_patch_this_rom_okay(my_rom_data, force=True)
                    self.state['my_header'], self.state['my_rom'] = my_rom[:16], my_rom[16:]
            else:
                self.state['my_header'], self.state['my_rom'] = my_rom[:16], my_rom[16:]
                self.state['load_fail'] = 0
                if auto_load:
                    sg.PopupQuickMessage('ROM has been Autoloaded!', auto_close_duration=5)
            self.rom = my_rom

        path_lst = os.path.join('patch_data', 'smb2.lst')
        path_loc = os.path.join('patch_data', 'memory_locations.json')

        import json
        if os.path.isfile(path_lst):
            with open(path_lst) as f:
                self.state['my_mem_locs'] = disasm.getMemoryLocationsFromLst(f.read(), bank_num=8)
            with open(path_loc, 'w') as f:
                json.dump(self.state['my_mem_locs'], f, indent=2)
        
        if os.path.isfile(path_loc):
            with open(path_loc) as f:
                self.state['my_mem_locs'] = json.load(f)
        else:
            sg.PopupError('Missing vital file "memory_locations.json')
            
    
    def run(self):
        # run window
        # Threads
        if self.state['thread_state'] == 1:
            small_window = sg.Window('Loading', [[sg.Image('icons/animatedwow.gif', key='image')], [sg.Text('Loading gam.................', key='taxt')]], keep_on_top=True, no_titlebar=True, grab_anywhere=True)
            while self.state['thread_state'] == 1:
                event, _values = small_window.read(timeout=100)
                small_window['image'].update_animation('icons/animatedwow.gif', time_between_frames=100)
            small_window.close()
        if self.state['thread_state'] == 2:
            sg.PopupAutoClose('Rom outputted to smb2-output.nes!')
            self.state['thread_state'] = 0
        if self.state['thread_state'] == 3:
            sg.PopupError(self.queue.pop())
            self.state['thread_state'] = 0
        event, values = self.window.read()
        print('Event:', event)

        # Exit if user closes window or clicks cancel
        if event in [None, 'Cancel']:
            return False
        
        # Load File
        if event in ['Load File']:
            my_file = sg.PopupGetFile('', file_types=[('NES', '.nes .bin')], no_window=True)
            if my_file != '': self.load_my_rom(my_file)
            return True

        # Seed Options
        if event in ['seedbox']:
            my_val = self.seed_box.Get()[:10].upper()
            if len([x for x in my_val if x not in valid_seed_chrs]) > 0:
                my_val = self.current_seed
            if my_val != self.seed_box.Get():
                self.seed_box.Update(my_val)
            self.current_seed = my_val
            print('new seed', self.current_seed)
            return True
        if event in ['Randomize Seed']:
            self.current_seed = ''.join(random.choices(valid_seed_chrs, k=10))
            self.seed_box.Update(self.current_seed)
            print('new seed', self.current_seed)
            return True
        
        if 'Character Select' in event:
            select_layout = [
            [sg.Text('Select Characters to randomize into selection')],
            [sg.Text('Drag or Ctrl+Click to select multi')],
            [sg.Listbox(self.characters, key='character_list',\
                select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, size=(40, 10), auto_size_text=True,\
                default_values=self.active_chars)],
            [sg.OK(), sg.Cancel()]]

            # Create the Window
            window = sg.Window('Character Select', select_layout)
            # Event Loop to process "events"
            while True:             
                event, values = window.read()
                if event in (sg.WIN_CLOSED, 'Cancel'): break
                if event in ('OK'):
                    self.active_chars = window['character_list'].get()
                    print('\n'.join(self.active_chars))
                    break

            window.close()
            return True

        if 'Level Select' in event:
            l_select_layout = [
            [sg.Text('Select Levels to randomize into selection')],
            [sg.Text('Drag or Ctrl+Click to select multi')],
            [sg.Listbox([str(x) for x in self.level_sets.keys()], key='level_list',\
                select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, size=(40, 10), auto_size_text=True,\
                default_values=[str(x) for x in self.active_levels.keys()])],
            [sg.OK(), sg.Cancel()]]

            # Create the Window
            window = sg.Window('Level Select', l_select_layout)
            # Event Loop to process "events"
            while True:             
                event, values = window.read()
                if event in (sg.WIN_CLOSED, 'Cancel'): break
                if event in ('OK'):
                    self.active_levels = {x: self.level_sets[x] for x in window['level_list'].get()}
                    print('\n'.join(self.active_levels))
                    break

            window.close()
            return True


        if 'Extra Settings' in event:
            types_affect = ['room', 'level']
            ex = self.extra_settings
            l_select_layout = [
            [sg.Column([
            [sg.Text('Extra Settings')],
            [sg.Text('Invert Chance')],
            [sg.Text('Even More Bonus Lives')],
            [sg.Text('Boss Health Minus Range')],
            [sg.Text('Boss Health Plus Range')],
            [sg.Text('World Randomization per')],
            [sg.Text('Inverted Levels per')],
            [sg.Text('Force Character per')]
            ]),
            sg.Column([
            [sg.Text('-')],
            [sg.Combo([*range(0, 101)], 
                default_value=ex['invertChance'])],
            [sg.Combo([*range(-10, 101)],
                default_value=ex['extraLives'])],
            [sg.Combo([*range(-2,0)], readonly=True,
                default_value=ex['bossMin'])],
            [sg.Combo([*range(-2,11)], readonly=True,
                default_value=ex['bossMax'])],
            [sg.Combo(types_affect, readonly=True,
                default_value=ex['worldPer'])],
            [sg.Combo(types_affect, readonly=True,
                default_value=ex['invertPer'])],
            [sg.Combo(types_affect, readonly=True,
                default_value=ex['charPer'])],
            ])],
            [sg.OK(), sg.Cancel()]]

            # Create the Window
            window = sg.Window('Option Select', l_select_layout)
            # Event Loop to process "events"
            while True:             
                event, values = window.read()
                if event in (sg.WIN_CLOSED, 'Cancel'): break
                if event in ('OK'):
                    for n, x in enumerate(self.extra_settings.keys()):
                        self.extra_settings[x] = values[n]
                    print(self.extra_settings)
                    break

            window.close()
            return True

        # If our ROM dne, throw a dialog
        if not self.isRomExist():
            return True

        # boss preset
        elif any(x in event for x in ['boss', 'crystal', 'rescue', 'survival', 'string', 'basic', 'Generate']):
            # There ought to be a better way to poll all window elements into an options dictionary
            meta = self.window[event].metadata
            self.state['thread_state'] = 1

            def thread_logic(): 
                try:
                    random.seed(self.current_seed)

                    values['event'], values['meta'] = event, meta
                    values['seed'], values['worldsets'] = self.current_seed, self.level_sets
                    values['presetCharRule'] = values['presetCharRule'][0]

                    for x in self.extra_settings:
                        values[x] = self.extra_settings[x]

                    game = randomizer.smb2.LevelStorage(sorted(self.active_levels.values()))

                    my_new_rom = randomizer.randomize_rom(self.state['my_rom'], self.state['my_mem_locs'], values, game); 

                    randomizer.randomize_characters(my_new_rom, values, self.active_chars, self.state['my_mem_locs'])

                    randomizer.randomize_text(my_new_rom, values, self.state['my_mem_locs'])

                    with open('smb2-output.nes', 'wb') as f:
                        f.write(self.state['my_header'])
                        f.write(my_new_rom)
                    self.state['thread_state'] = 2
                except Exception as e:
                    self.queue.append('Error has occurred:' + str(e))
                    self.state['thread_state'] = 3
                    raise e
            self.window.finalize()
            threading.Thread(target=thread_logic, daemon=True).start()
        return True

# window = self.create_window()

import argparse

if __name__ == '__main__':
    argget = argparse.ArgumentParser(description='Args for randomizer')
    argget.add_argument('--file', type=str, help='filename')
    argget.add_argument('--toggle', action='store_true', help='')
    args = argget.parse_args()

    if not os.path.isfile('first_run'):
        import textwrap
        string = 'If this is your first time running, it is encouraged to read the documentation or README.md to understand the changes between the original game and the current game!'
        sg.Popup(textwrap.fill(string, 40))
        with open('first_run', 'x'):
            pass
    
    my_app = Application('smb2.nes')

    while my_app.run():
        pass
    
    my_app.window.close()
    
# Event Loop to process "events" and get the "values" of the inputs
