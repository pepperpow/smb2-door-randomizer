import game_lib.randomizer as randomizer
import game_lib.disasm as disasm
import glob, os, random, re
import PySimpleGUI as sg
import threading

from ui.ui_define import layout_quick

version = 0.49

valid_seed_chrs = [str(x) for x in range(10)] + [chr(x) for x in range(65,65+26)]

# TODO: why does slider not have a get function jeez
# should maybe use pop-ups instead of tabs because sheesh

sg.Slider.Get = lambda self: self.TKIntVar.get()

sg.LOOK_AND_FEEL_TABLE['SMB2'] = {
    'BACKGROUND': '#709053',
    'TEXT': '#fff4c9',
    'INPUT': '#c7e78b',
    'TEXT_INPUT': '#000000',
    'SCROLL': '#c7e78b',
    'BUTTON': ('white', '#709053'),
    'PROGRESS': ('#01826B', '#D0D0D0'),
    'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0,
    }

sg.theme('DarkAmber')   # Add a touch of color '#e7cb52'
sg.theme_button_color(('black', '#d82800'))

seed_box = sg.InputText('', change_submits=True, key='seedbox', size=(30, None))

def render_element(form, sub_n=0):
    if isinstance(form, list):
        my_element = [render_element(x, sub_n+1) for x in form]
        return my_element
    else:
        my_type = form['type'][0].capitalize() + form['type'][1:]
    
        if my_type == 'Frame':
            return sg.Frame(form['title'], render_element(form['val']), key=form.get('key'))
        if my_type == 'Column':
            return sg.Column(render_element(form['val']), key=form.get('key'))
        if my_type == 'Select':
            return [sg.Text(form['title']), 
                    sg.Combo(form['val'], key=form.get('key'), readonly=True,
                    default_value=form['val'][0])]
                # sg.Combo(my_chars_all, key='player1', readonly=True,\
                # default_value=self.state['selected_chars'][0])],
        if my_type == 'Checkbox':
            return vars(sg)[my_type](form.get('val'), key=form.get('key'), metadata=form.get('meta'), default=form.get('default', False))
        if my_type == 'Img':
            my_type = 'Image'
        if form.get('val'):
            return vars(sg)[my_type](form.get('val'), key=form.get('key'), metadata=form.get('meta'))
        else:
            return vars(sg)[my_type](key=form.get('key'), metadata=form.get('meta'))

layout_main = [
    [sg.Button('Load File'), sg.Text('Seed'), seed_box, sg.Button('Randomize Seed')],
    [sg.Column([
        [sg.TabGroup([ 
            [sg.Tab('Quick Start', render_element(layout_quick), element_justification='left' , pad=(20,20))]
        ])]
        ], vertical_scroll_only=True, expand_y=True, key='__main')
    ],
]

default_chars = ('Mario', 'Luigi', 'Toad', 'Peach')
class Application():
    """Base Application"""
    def __init__(self, filename) -> None:
        self.state = {
            'load_fail': 0,
            'i_beta_be_off': False,
            'my_header': None,
            'my_rom': None,
            'my_mem_locs': None,
            'thread_state': 0,
            'selected_chars': list(default_chars)
        }

        self.queue = []

        self.header, self.rom = None, None 

        self.current_seed = ''.join(random.choices(valid_seed_chrs, k=10))
        
        # setup sets of levels by name
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

        # set up characters
        self.characters = {}
        for char_set in glob.glob(os.path.join('my_characters', '*')):
            my_char_sets = glob.glob(os.path.join(char_set, '*.png'))
            for char in my_char_sets:
                char_base, char_name = os.path.split(char)
                char_name = os.path.basename(os.path.splitext(char_name)[0])
                if ',' in char_name:
                    cmds = [x for x in (char_name.split(','))]
                    char_name, cmds = cmds[0], cmds[1:]
                else:
                    cmds = []
                char_base = os.path.basename(char_base)
                if char_base not in ['default']:
                    if len(cmds):
                        char_name = '{} ({}): {}'.format(char_name, ','.join(cmds), char_base)
                    else:
                        char_name = '{} : {}'.format(char_name, char_base)
                    if char_base in ['base']:
                        char_name = char_name.replace(': base','')
                self.characters[char_name.capitalize()] = char
        self.active_chars = [x for x in self.characters.keys() if ':' not in x]

        # load
        if os.path.isfile(filename):
            self.load_my_rom(filename, True)

        dummy_window = sg.Window('dummy', [[sg.Text('dummy')]], finalize=True)
        my_h = dummy_window.TKroot.winfo_screenheight()
        dummy_window.close()
        self.window = sg.Window('SMB2 Door Randomizer', layout_main, titlebar_icon='ui/icons/iconApp.ico', icon='ui/icons/iconApp.ico')
        if my_h < 800:
            self.window['__main'].Scrollable = True
            self.window.Resizable = True
            self.window.Finalize()
            self.window.size = (self.window.size[0], my_h-64)
            self.window.move(20, 20)
        else:
            self.window.Finalize()

        self.seed_box = seed_box
        self.seed_box.Update(self.current_seed)

        self.extra_settings = {
            "invertChance": 20,
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
            small_window = sg.Window('Loading', [[sg.Image('ui/icons/animatedwow.gif', key='image')], [sg.Text('Loading gam.................', key='taxt')]], keep_on_top=True, no_titlebar=True, grab_anywhere=True)
            while self.state['thread_state'] == 1:
                event, _values = small_window.read(timeout=100)
                small_window['image'].update_animation('ui/icons/animatedwow.gif', time_between_frames=100)
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
            my_chars_all = ['?'] + sorted([ x for x in self.characters.keys() ])

            select_layout = [
            [sg.Text('Select Characters to each Slot')],
            [sg.Text('Slot 1'),
                sg.Combo(my_chars_all, key='player1', readonly=True,\
                default_value=self.state['selected_chars'][0])],
            [sg.Text('Slot 2'),
            sg.Combo(my_chars_all, key='player2', readonly=True,\
                default_value=self.state['selected_chars'][1])],
            [sg.Text('Slot 3'),
            sg.Combo(my_chars_all, key='player3', readonly=True,\
                default_value=self.state['selected_chars'][2])],
            [sg.Text('Slot 4'),
            sg.Combo(my_chars_all, key='player4', readonly=True,\
                default_value=self.state['selected_chars'][3])],
            [sg.OK(), sg.Cancel(), sg.Button('Random Pool')]]

            # Create the Window
            window = sg.Window('Character Select', select_layout)
            # Event Loop to process "events"
            while True:             
                event, values = window.read()
                if event in (sg.WIN_CLOSED, 'Cancel'): break
                elif event in ('Random Pool'):
                    while True:
                        select_layout_random = [
                        [sg.Text('Select Characters to randomize into selection')],
                        [sg.Text('Drag or Ctrl+Click to select multi')],
                        [sg.Listbox(my_chars_all[1:], key='character_list',\
                            select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, size=(40, 10), auto_size_text=True,\
                            default_values=self.active_chars)],
                        [sg.OK(), sg.Cancel()]]

                        window_inner = sg.Window('Character Select', select_layout_random)
                        event, values = window_inner.read()
                        if event in (sg.WIN_CLOSED, 'Cancel'): break
                        if event in ('OK'):
                            self.active_chars = window_inner['character_list'].get()
                            print('\n'.join(self.active_chars))
                            for n in range(4):
                                window['player{}'.format(n+1)].update('?')
                            window_inner.close()
                            break
                elif event in ('OK'):
                    for n in range(4):
                        self.state['selected_chars'][n] = window['player{}'.format(n+1)].get()
                    print(self.state['selected_chars'])
                    self.window['presetRandomCharacters'].update('Custom Characters')
                    if tuple(self.state['selected_chars']) == default_chars:
                        self.window['presetRandomCharacters'].update('Default Characters')
                    if tuple(self.state['selected_chars']) == tuple(['?']*4):
                        self.window['presetRandomCharacters'].update('Randomized Characters')
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


        if 'More Settings' in event:
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
        
        if 'Enable Beta' in event:
            self.state['i_beta_be_off'] = not self.state['i_beta_be_off']
            self.window['betaMap'].Update(visible=self.state['i_beta_be_off'])
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

                    if 'boss' in event:
                        open_levels = [y for x,y in self.active_levels.items() if 'openworld' in x]
                        if len(open_levels) == 0:
                            self.queue.append('Error has occurred: Map-based randomization REQUIRES openworld patched levels, select in Level Select')
                            self.state['thread_state'] = 3
                            return True
                        else:
                            game = randomizer.smb2.LevelStorage(sorted(open_levels))
                    else:
                        game = randomizer.smb2.LevelStorage(sorted(self.active_levels.values()))


                    values['presetRandomCharacters'] = 'Randomized' in self.window['presetRandomCharacters'].get()
                    my_new_rom = randomizer.randomize_rom(self.state['my_rom'], self.state['my_mem_locs'], values, game); 

                    my_actives = [x for x in self.active_chars if x not in self.state['selected_chars']]
                    if len(my_actives) == 0:
                        my_actives = ['Mario', 'Luigi', 'Toad', 'Peach']
                    elif len(my_actives) < 4:
                        my_actives = my_actives*4
                    randoms = random.sample(my_actives, k=4)

                    my_selects = [a if b == '?' else b for a, b in zip(randoms, self.state['selected_chars'])]

                    randomizer.randomize_characters(my_new_rom, values, my_selects, {x:y for x,y in self.characters.items() if x in my_selects + my_actives}, self.state['my_mem_locs'])

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
