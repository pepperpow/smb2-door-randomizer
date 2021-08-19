import PySimpleGUI as sg

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

objective_tagline = "Complete the following objectives, then find a level exit"
randomization_tagline = "How to randomize our Levels"

seed_box = sg.InputText('', change_submits=True, key='seedbox', size=(30, None))

# option_def = {}
    # {"name": "Inverted Rate", "desc": "Rate at which rooms will be inverted", "val": "0.5"},
    # [{'name': 'Crystal Count Required/Total', 'desc': 'Amount of crystals required to complete the game'},
    # { 'name': 'Boss Count Required/Total', 'desc': 'Amount of bosses defeated to complete the game'},
    # { 'name': 'Final Boss Exit Required', 'desc': 'Final Boss Exit must be used to finished the game'},
    # { 'name': 'All Characters Rescued', 'desc': 'Must not have any characters missing'}
    # {"name": "Randomize Mushroom Locations", "desc": "Completely randomizes mushroom locations", "val": False},
    # {"name": "Mushrooms", "desc": "Number of mushrooms in item pool", "val": "4"},
    # {"name": "Mushroom Fragments", "desc": "Number of mushrooms in item pool", "val": "16"},
    # {"name": "Powerups", "desc": "Number of powerups in item pool", "val": "16"},
    # {"name": "Upgrades", "desc": "Number of upgrades in item pool", "val": "13"},
    # {"name": "Common Items", "desc": "Number of common items in item pool", "val": "8"},
    # {"name": "Crystals", "desc": "Number of crystals in item pool", "val": "0"},
    # {"name": "TODO: Finish adding additional mushroom locations", "desc": "", "val": "1"},
    # {"name": "Doki Doki Mode (unimplemented)", "desc": "Removes shrinking and running", "val": False, "class": "", "mem_loc_name": "DokiMode"},
    # {"name": "Debug (cheat)", "desc": "Gives debug mode (A+B+START+SELECT), prone to issues with subspace/jars", "val": False, "class": "mem_location", "mem_loc_name": "DebugSet"},
    # {"name": "Ground Breaker (cheat)", "desc": "Lets the player pick up any ground tile", "val": False, "class": "mem_location", "mem_loc_name": "GBreaker"},
    # {"name": "Maxed Upgrades (cheat)", "desc": "Gives players all upgrades", "val": False}, 
    # {"name": "Maxed Health", "desc": "Maxed amount of extra health", "val": "14", "class": "mem_location", "mem_loc_name": "MaxedHealth", "min": -1, "max": 14},
    # {"name": "Include CRC Hash on Title", "desc": "Writes CRC hash to title screen (but will modify outputted file hash)", "val": False}, 
    # {"name": "Independent Player Powerups", "desc": "Upgrades are only for individual characters", "val": False, "class": "mem_location", "mem_loc_name": "IndependentPlayers"},
    # {"name": "Add Rescue Items", "desc": "Adds items to rescue lost characters", "val": False},
    # {"name": "Starting Gift", "desc": "Gives a random upgrade to each character", "val": False},
    # {"name": "Enemy Champion Chance", "desc": "Percent chance of 'champion' enemies", "val": 8.25},
    # {"name": "Enemy Randomization", "desc": "Enemy randomizer (hard)", "val": False},
    # {"name": "Enemy Scaling Range", "desc": "Range of which enemies can decrease/increase in difficulty", "val": 1, "min": 0, "max": 10},
    # {"name": "Enemy Max Score Percent", "desc": "Scales how much more dangerous enemies can be overall", "val": 50.0, "min": 0, "max": 200},
    # {"name": "Boss Drops", "desc": "Bosses will drop something on death", "val": [ "Nothing", "Mushrooms and Fragments", "Major Items", "Full Item Pool" ]},                
    # {"name": "Boss Health Range", "desc": "", "val": "7"},
    # {"name": "Mini-Boss Health Range", "desc": "", "val": "1"},
    # {"name": "Randomize Boss Arenas", "desc": "Duplicate arenas", "val": False},
    # {"name": "End with Wart", "desc": "Last boss is always Wart", "val": False}
    # {"name": "TODO: Add Enemy Randomization and Boss Drops", "desc": "", "val": "1"},

# All the stuff inside your window.
# ly_objective = {
#     'words': [[sg.Text(x['name'], tooltip=x['desc'])] for x in option_def['objective'] ],
#     'options':  [ ]
# }

# ...

# ly_objects = {
#     'words': [[sg.Text(x['name'], tooltip=x['desc'])] for x in option_def['objects']] ,
#     'options':  [ ]
# }

# layout_enemies = [
#     [sg.Column([x + y for x, y in zip(ly_enemy['options'], ly_enemy['words'])])],
# ]

# ...

# layout_objects = [
#     [sg.Column([x + y for x, y in zip(ly_objects['options'], ly_objects['words'])])],
# ]


layout_char_select = [
        [sg.Text('Character Options')],
        [sg.Text('- Click on each slot to set/apply custom options')],
        [sg.Button(key='char{}'.format(x), image_filename='icons/char1.png') for x in range(4)] +  
        [sg.Column([
            [sg.Button('All Default')],
            [sg.Button('All Random')],
            [sg.Button('Lock All')],
            [sg.Button('Unlock All')],
        ])]
]

layout_quick = [
    [sg.Text('Select one of the following to automatically generate a playable ROM')],
    [sg.Frame('Level Randomizer (Basic)', [
    [sg.Text('Play the game as intended, just with scrambled levels!', font=('', 8))],
    [ sg.Image(key="imga", filename="icons/testicon1.png"),
        sg.Button('3 levels', key="basicMini", font=('System', 12), metadata={'k':3}),
        sg.Button('9 levels', key="basicShort", font=('System', 12), metadata={'k':9}),
        sg.Button('15 levels', key="basicMedium", font=('System', 12), metadata={'k':15}),
        sg.Button('20 levels', key="basicLong", font=('System', 12), metadata={'k':20})],
    [sg.Text('Randomly string rooms together into new levels', font=('', 8))],
    [sg.Text('  (Still being tested as of 0.49!  Deselect 7-2 in Level Select, or use openworld', font=('', 8))],
    [ sg.Image(key="imgb", filename="icons/testicon1a.png"),
        sg.Button('3 levels', key="stringMini", font=('System', 12), metadata={'k':3}),
        sg.Button('9 levels', key="stringShort", font=('System', 12), metadata={'k':9}),
        sg.Button('15 levels', key="stringMedium", font=('System', 12), metadata={'k':15}),
        sg.Button('20 levels', key="stringLong", font=('System', 12), metadata={'k':20})],
    ])],
    [sg.Frame('Door Randomizer Beta', [
    [sg.Text('Boss Hunter')],
    [sg.Text('Find and defeat X amount of bosses, locked behind doors', font=('', 8))],
    [sg.Text('  (Still being tested as of 0.49!  MANUALLY select only openworld levels in Level Select)', font=('', 8))],
    [sg.Image(filename="icons/testicon2.png"),
        sg.Button('1 Boss', key="bossWart", font=('System', 12), metadata= {'k': 12, 'boss': 1}),
        sg.Button('3 Bosses', key="bossShort", font=('System', 12), metadata= {'k': 12, 'boss': 3}),
        sg.Button('5 Bosses', key="bossMedium", font=('System', 12), metadata={'k': 15, 'boss': 5}),
        sg.Button('7 Bosses', key="bossLong", font=('System', 12), metadata=  {'k': 20, 'boss': 7})],
    [
    sg.Checkbox('Shuffle Level Order', key='betaShuffleLevel'), 
    sg.Checkbox('Room Order', key='betaShuffleRoom'), 
    sg.Checkbox('Lock Boss Doors', key='betaLockedDoors')
    ],
    ], key='betaMap'), 
    ],
    # [sg.Text('Crystal Finder')],
    # [sg.Text('Find and collect X amount of orbs by defeating Birdos, finding at end of levels or in subspace', font=('', 8))],
    # [sg.Image(filename="icons/testicon3.png"), sg.Image(filename="icons/testicon3a.png"),
    #     sg.Button('Short (5)', key="crystalShort", font=('System', 12), metadata={'k':12, 'crys': 5}),
    #     sg.Button('Medium (12)', key="crystalMedium", font=('System', 12), metadata={'k':15, 'crys': 12}),
    #     sg.Button('Long (20)', key="crystalLong", font=('System', 12), metadata={'k':20, 'crys': 20})],
    # [sg.Text('Rescue Mission')],
    # [sg.Text('Find and unlock all characters in your roster, plus additional objectives', font=('', 8))],
    # [sg.Image(filename="icons/testicon4.png"),
    # sg.Image(filename="icons/testicon5.png"),
    #     sg.Button('Rescue All', key="rescueShort", font=('System', 12), metadata={'k':12}),
    #     sg.Button('Boss Rescue (3)', key="rescueMedium", font=('System', 12), metadata={'k':15, 'boss': 3})],
    [sg.Column([[
        sg.Checkbox('Extra Lives', key='presetBonusLives'), 
        sg.Checkbox('Bonus Health', key='presetBonusHealth'),
        sg.Checkbox('Secret Detection', key='presetSecret'),
        ]], justification='right', pad=(10,0)),
    ],
    [sg.Column([[
        sg.Checkbox('Inverted Levels', key='presetInvert', default=True),
        sg.Checkbox('Randomize Sky', key='presetSkyShuffle', default=True),
        sg.Checkbox('Shuffle World Enemy/Tiles', key='presetWorldShuffle', default=True),
        ]], justification='right', pad=(10,0)),
    ],
    [
        sg.HorizontalSeparator()
    ],
    [sg.Column([[
        sg.Text('Character Rules'),
        sg.Listbox(['Select Character After Death', 'Survival Mode, lives per character', 'Force Character per Room', 'Select Anytime (select+LR)'], 
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, size=(30, 0), auto_size_text=True, no_scrollbar=True, key='presetCharRule',
            default_values='Select Character After Death'),
        ]], justification='right', pad=(10,0)),
    ],
    [sg.Column([[
        sg.Checkbox('Random Characters', key='presetRandomCharacters'),
        sg.Checkbox('Palettes', key='presetRandomCharPal'),
        sg.Checkbox('Stats', key='presetRandomStats'),
        sg.Checkbox('Names', key='presetRandomNames'),
        ]], justification='right', pad=(10,0)),
    ],
    [sg.Column([[ 
        sg.Button('Character Select', button_color='#e7cb52'),
        sg.Button('Level Select', button_color='#e7cb52'),
        sg.Button('Extra Settings', button_color='#e7cb52'),
        # sg.Button('Enable Beta', button_color='#e7cb52'),
        ]] , justification='right', pad=(10,0)) ]
]

# layout_canvas = sg.Canvas(size=(150,150))

# layout_advanced = [
#         [sg.TabGroup([
#         [sg.Tab('Main', layout), 
#         sg.Tab('Objects', layout_objects), sg.Tab('Enemies', layout_enemies),
#         sg.Tab('Other', layout_other)]], 
#         )],
#         [sg.Column([[sg.Button('Generate Open')]], justification='right')],
#         [sg.Column([[sg.Button('Generate Linear')]], justification='right')]
# ]

layout_main = [
    [sg.Button('Load File'), sg.Text('Seed'), seed_box, sg.Button('Randomize Seed')],
    [sg.TabGroup(
        [ 
            [sg.Tab('Quick Start', layout_quick, element_justification='left' , pad=(20,20)),
            # sg.Tab('Debug Output', [[sg.Output(size=(80,20), expand_y=True, font=('', 7))]])
        ] ])]
]
# sg.Tab('Levels', layout_level_select), 