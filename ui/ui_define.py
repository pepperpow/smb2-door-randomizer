
my_title = {'type':'text', 'val':'Select one of the following to automatically generate a playable ROM'}

frame_level_randomizer_basic = {'type':'frame', 'title':'Level Randomizer (Basic)', 'val':[
    [{'type':'text', 'val':'Play the game as intended, just with scrambled levels!', 'font':('', 8)}], # 1
    [{'type':'img', 'val':"ui/icons/testicon1.png"},
        {'type':'button', 'val':'3 levels', 'key':"basicMini", 'font':('System', 12), 'meta':{'k':3}},
        {'type':'button', 'val':'9 levels', 'key':"basicShort", 'font':('System', 12), 'meta':{'k':9}},
        {'type':'button', 'val':'15 levels', 'key':"basicMedium", 'font':('System', 12), 'meta':{'k':15}},
        {'type':'button', 'val':'20 levels', 'key':"basicLong", 'font':('System', 12), 'meta':{'k':20}}], # 2
    [{'type':'text', 'val':'Randomly string rooms together into new levels', 'font':('', 8)}], # 3
    [{'type':'text', 'val':'  (Still being tested as of 0.49!  Deselect World 7 in Level Select, or use openworld)'}], # 4
    [{'type':'img', 'val':"ui/icons/testicon1a.png"},
        {'type':'button', 'val':'3 levels', 'key':"stringMini", 'font':('System', 12), 'meta':{'k':3}},
        {'type':'button', 'val':'9 levels', 'key':"stringShort", 'font':('System', 12), 'meta':{'k':9}},
        {'type':'button', 'val':'15 levels', 'key':"stringMedium", 'font':('System', 12), 'meta':{'k':15}},
        {'type':'button', 'val':'20 levels', 'key':"stringLong", 'font':('System', 12), 'meta':{'k':20}}, ] # 5
    ]} # end of frame 
    

frame_level_randomizer_map = {'type':'frame', 'title':'Door Randomizer Beta', 'val':[
    [{'type':'text', 'val':'Boss Hunter'}],
    [{'type':'text', 'val':'Find and defeat X amount of bosses, locked behind doors'}],
    [{'type':'text', 'val':'(Still being tested as of 0.49!  MANUALLY select only openworld levels in Level Select)'}],
    [{'type':'img', 'val':"ui/icons/testicon2.png"},
        {'type':'button', 'val':'1 Boss', 'key':"bossWart", 'font':('System', 12), 'meta':{'k': 12, 'boss': 1}},
        {'type':'button', 'val':'3 Bosses', 'key':"bossShort", 'font':('System', 12), 'meta':{'k': 12, 'boss': 3}},
        {'type':'button', 'val':'5 Bosses', 'key':"bossMedium", 'font':('System', 12), 'meta':{'k': 15, 'boss': 5}},
        {'type':'button', 'val':'7 Bosses', 'key':"bossLong", 'font':('System', 12), 'meta':{'k': 20, 'boss': 7}}],
    [ {'type':'checkbox', 'val':'Shuffle Level Order', 'key':'betaShuffleLevel'}, 
    {'type':'checkbox', 'val':'Shuffle Room Order', 'key':'betaShuffleRoom'}, 
    {'type':'checkbox', 'val':'Lock Boss Doors', 'key':'betaLockedDoors'} ]
    ], 'key':'betaMap'} 

bonus_settings_1 = {'type':'column', 'just':'center', 'val':[[
        {'type':'checkbox', 'val':'Extra Lives', 'key':'presetBonusLives'}, 
        {'type':'checkbox', 'val':'Bonus Health', 'key':'presetBonusHealth'},
        {'type':'checkbox', 'val':'Secret Detection', 'key':'presetSecret'}, ]]
        }
        # 'just':'right', 'pad':(10,0)} # justifcation, pad

bonus_settings_2 = {'type':'column', 'just':'center', 'val':[[
        {'type':'checkbox', 'val':'Inverted Levels', 'key':'presetInvert', 'default':True},
        {'type':'checkbox', 'val':'Randomize Sky', 'key':'presetSkyShuffle', 'default':True},
        {'type':'checkbox', 'val':'Shuffle World Enemy/Tiles', 'key':'presetWorldShuffle', 'default':True}]]
        }

char_rules = {'type':'column', 'val':[
        {'type':'select', 'title': 'Character Rules', 'val': ['Select Character After Death', 'Survival Mode, lives per character', 'Force Character per Room', 'Select Anytime (select+LR}'], 'key':'presetCharRule'},
    ]}

char_stuff = {'type':'column', 'val':[[
         {'type':'text', 'val': 'Default Characters', 'key':'presetRandomCharacters'},
         {'type':'checkbox', 'val': 'Random Palettes', 'key':'presetRandomCharPal'},
         {'type':'checkbox', 'val': 'Random Stats', 'key':'presetRandomStats'},
         {'type':'checkbox', 'val': 'Random Names', 'key':'presetRandomNames'},
    ]]}

other_stuff = {'type':'column', 'val':[[
         {'type':'button', 'val': 'Character Select', }, #'#e7cb52'},
         {'type':'button', 'val': 'Level Select', }, #'#e7cb52'},
         {'type':'button', 'val': 'More Settings', }, #'#e7cb52'},
    ]]}

extra_settings = {'type':'frame', 'title':'Extra Settings', 'val':[
    [bonus_settings_1],
    [bonus_settings_2],
    [char_rules],
    [char_stuff],
    [other_stuff],
]}

layout_quick = [
    [my_title],
    [frame_level_randomizer_basic],
    [frame_level_randomizer_map],
    [extra_settings]
    ]

# [('text', 'Crystal Finder')],
# [('text', 'Find and collect X amount of orbs by defeating Birdos, finding at end of levels or in subspace', font=('', 8))],
# [('img', filename="icons/testicon3.png"), ('img', filename="icons/testicon3a.png"),
#     ('button', 'Short (5)', "crystalShort", font=('System', 12), metadata={'k':12, 'crys': 5}),
#     ('button', 'Medium (12)', "crystalMedium", font=('System', 12), metadata={'k':15, 'crys': 12}),
#     ('button', 'Long (20)', "crystalLong", font=('System', 12), metadata={'k':20, 'crys': 20})],

#     # select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, size=(30, 0), auto_size_text=True, no_scrollbar=True) default_value...
#     # sg.Listbox(['Select Character After Death', 'Survival Mode, lives per character', 'Force Character per Room', 'Select Anytime (select+LR)'], 
#     #     select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, size=(30, 0), auto_size_text=True, no_scrollbar=True, 'presetCharRule',
#     #     default_values='Select Character After Death'),

# # sg.Tab('Levels', layout_level_select), 
# # option_def = {}
# # { 'title': 'All Characters Rescued', 'desc': 'Must not have any characters missing'}
# # {"title": "Randomize Mushroom Locations", "desc": "Completely randomizes mushroom locations", "val": False},
# # {"title": "Mushrooms", "desc": "Number of mushrooms in item pool", "val": "4"},
# # {"title": "Mushroom Fragments", "desc": "Number of mushrooms in item pool", "val": "16"},
# # {"title": "Powerups", "desc": "Number of powerups in item pool", "val": "16"},
# # {"title": "Upgrades", "desc": "Number of upgrades in item pool", "val": "13"},
# # {"title": "Common Items", "desc": "Number of common items in item pool", "val": "8"},
# # {"title": "Crystals", "desc": "Number of crystals in item pool", "val": "0"},
# # {"title": "TODO: Finish adding additional mushroom locations", "desc": "", "val": "1"},
# # {"title": "Doki Doki Mode (unimplemented)", "desc": "Removes shrinking and running", "val": False, "class": "", "mem_loc_name": "DokiMode"},
# # {"title": "Independent Player Powerups", "desc": "Upgrades are only for individual characters", "val": False, "class": "mem_location", "mem_loc_name": "IndependentPlayers"},
# # {"title": "Starting Gift", "desc": "Gives a random upgrade to each character", "val": False},
# # {"title": "Enemy Champion Chance", "desc": "Percent chance of 'champion' enemies", "val": 8.25},
# # {"title": "Enemy Randomization", "desc": "Enemy randomizer (hard)", "val": False},
# # {"title": "Enemy Scaling Range", "desc": "Range of which enemies can decrease/increase in difficulty", "val": 1, "min": 0, "max": 10},
# # {"title": "Enemy Max Score Percent", "desc": "Scales how much more dangerous enemies can be overall", "val": 50.0, "min": 0, "max": 200},
# # {"title": "Boss Drops", "desc": "Bosses will drop something on death", "val": [ "Nothing", "Mushrooms and Fragments", "Major Items", "Full Item Pool" ]},                
# # {"title": "TODO: Add Enemy Randomization and Boss Drops", "desc": "", "val": "1"},