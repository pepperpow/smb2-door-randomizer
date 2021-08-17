from types import SimpleNamespace
import re

def level_h(level):
    """
    Restructure level into horizontal
    """    
    new_level = []
    for y in range(15):
        for x in range(10):
            new_level.extend(level[y*16 + x*240: y*16 + x*240 + 16])
    return new_level
    
def get_pos_tuple(pos, horiz):
    """
    Restructure position into X,Y,page Tuple
    """    
    if horiz: return (pos % 160) // 16, pos % 16, pos // 160 
    else: return pos // 240, pos % 16, (pos % 240) // 16

fields = ['col', 'page', 'x', 'y', 'command', 'tiles', 'h', 'priority']

default_fields = (0,0,0,0,'SINGLE', ['a'], 1, 0)

def smb2command(*args):
    if len(args) > len(fields):
        raise ValueError
    values = args + default_fields[len(args):]
    my_dict = { f: v for f, v in zip(fields, values) }
    return SimpleNamespace(**my_dict)

def test_tokens():
    for x in range(6):
        yield smb2command( 0, 0, 8 - x, 1 + x, 'CAPPED', ''.join([\
            chr(x) for x in [0xca] + [0xcc]*x + [0xce]] ))
    for x in range(6):
        yield smb2command( 0, 1, 8 - x, 1 + x, 'VCAPPED', ''.join([\
            chr(x) for x in [0xca] + [0xcc]*x + [0xce]] ))
    yield smb2command( 0, 0, 0, 14, 'REPEAT', ''.join([\
        chr(x) for x in [0x39]*31] ))
    yield smb2command( 0, 2, 1, 13, 'REPEAT', ''.join([\
        chr(x) for x in [0x39]*31] ))
    yield smb2command( 0, 3, 2, 12, 'REPEAT', ''.join([\
        chr(x) for x in [0x39]*31] ))
    yield smb2command( 0, 0, 3, 0, 'VREPEAT', ''.join([\
        chr(x) for x in [0x39]*10] ))
    yield smb2command( 0, 0, 0, 0, 'LINEAR', ''.join([\
        chr(x) for x in [0xc9, 0xc3, 0xc9, 0xc9]] ))
    yield smb2command( 0, 0, 0, 0, 'VLINEAR', ''.join([\
        chr(x) for x in [0xc9, 0xc3, 0xc9, 0xc9]] ))


def tokenize(code, horiz=False, single=False):
    words = [
        r'(?P<EMPTY>[@]+)',
        r'(?P<REPEAT>.)(?P=REPEAT){1,15}',
        r'(?P<CAPPED>[^@](?P<INR>[^@])(?P=INR){1,14}[^@])',
        r'(?P<SINGLE>.)',
    ]
    tok_regex = '|'.join(words)
    stack = []
    # yield Token('LINEAR', linear_data, stack[0].line, stack[0].column)
    pg = 0
    offset = 16
    if horiz:
        offset = 160
    code = ''.join(([chr(x) for x in code]))
    for cnt, line in enumerate( [code[i:i+offset] for i in range(0, len(code), offset)]):
        # print('line', cnt)
        stack = []
        for mo in re.finditer(tok_regex, line):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() + cnt * offset
            
            if kind == 'SINGLE':
                stack.append(smb2command( column, *get_pos_tuple(column, horiz), kind, value ))
                continue
            else:
                if len(stack) == 1:
                    if single:
                        yield stack[0]
                elif len(stack) > 1:
                    # col, page, x, y, _command, _tiles, _h = stack[0]
                    obj = stack[0]
                    obj.command = 'LINEAR'
                    obj.tiles = ''.join([(x.tiles[0]) for x in stack])
                    yield obj
                stack = []
            if kind == 'EMPTY':
                continue
            yield smb2command(column, *get_pos_tuple(column, horiz), kind, value)
        if len(stack) == 1:
            if single:
                yield stack[0]
        elif len(stack) > 1:
            obj = stack[0]
            obj.command = 'LINEAR'
            obj.tiles = ''.join([(x.tiles[0]) for x in stack])
            yield obj


def stack_manage(stack):
    commands = []
    if len(stack) == 1:
        commands.extend(stack)
    else:
        stack_line = [ord(x.tiles[0]) for x in stack]
        x, y, page = stack[0].x, stack[0].y, stack[0].page
        # print(len(stack_line), [hex(x) for x in stack_line])
        my_commands = tokenize(stack_line, single=True)
        for i in my_commands:
            i.x, i.y, i.page = x, (y + i.col) % 15, page + (y + i.col) // 15
            i.command = 'V' + i.command
            # print(i.col, i)
            commands.append(i)
    return commands


def commands_to_level(commands, door_data, pages):
    level_bits, all_bits = [], []
    current_page = 0
    last_len, last_repeat, last_linear = 0, [], []
    single_commands = sorted([c for c in commands if 'SINGLE' == c.command],
                key=lambda c: (c.x, c.page*15 + c.y))
    commands = [c for c in commands if 'SINGLE' != c.command]

    # print('\n'.join([str(x) for x in single_commands]))
    if len(single_commands):
        stack = [ single_commands[0] ]
        single_commands = single_commands[1:]
        for c in single_commands:
            last_obj = stack[-1] 
            y_pos = c.y + c.page * 15
            if y_pos == last_obj.y + last_obj.page * 15 + 1:
                stack.append(c)
            else:
                commands.extend(stack_manage(stack))
                stack = [c]
        if len(stack):
            commands.extend(stack_manage(stack))

    for c in sorted(commands, key=lambda x: (x.priority, x.page, x.tiles, x.command == 'RAW')):
        if c.page > pages:
            continue
        if len(level_bits) > 200:
            all_bits.append(level_bits)
            level_bits = []

        if current_page != c.page:
            # print('PAGING TO', c.page)
            level_bits.append((0xF0 + c.page))
            current_page = c.page

        if door_data[current_page] not in [b'\x00\x00', None]:
            level_bits.append(0xfd)
            level_bits.extend(door_data[current_page])
            door_data[current_page] = None

        # if c.command in ['CAPPED', 'VCAPPED']:
        #     c_byte = 0x4 if c.command == 'CAPPED' else 0x5
        #     rep_byte_set = [c.tiles[0], c.tiles[1], c.tiles[-1]]
        #     rep_byte = len(rep_byte_set) if last_linear != rep_byte_set else 0
        #     last_linear = rep_byte_set
        #     level_bits.extend([0b11100000 + c.h])
        #     level_bits.extend([(c_byte << 5) + rep_byte, (c.y << 4) + c.x])
        #                 # (c.h << 4) + len(c.tiles)-2])
        #     if rep_byte != 0:
        #         level_bits.extend([ord(x) for x in rep_byte_set])
        if c.command in ['LINEAR', 'VLINEAR', 'CAPPED', 'VCAPPED']:
            c_byte = 0x2 if c.command in ['LINEAR', 'CAPPED'] else 0x3
            rep_byte = len(c.tiles) if last_linear != c.tiles else 0
            last_linear = c.tiles
            level_bits.extend([(c_byte << 5) + rep_byte, (c.y << 4) + c.x])
            if rep_byte != 0:
                level_bits.extend([ord(x) for x in c.tiles])
        if c.command in ['REPEAT', 'VREPEAT', 'SINGLE', 'VSINGLE']:
            c_byte = 0x1 if c.command == 'VREPEAT' else 0x0
            rep_byte = len(c.tiles)
            if last_repeat == c.tiles[0] and last_len == len(c.tiles):
                rep_byte = 0
            last_repeat, last_len = c.tiles[0], len(c.tiles)
            level_bits.extend([(c_byte << 5) + rep_byte,
                        (c.y << 4) + c.x])
            if rep_byte != 0:
                level_bits.append(ord(c.tiles[0]))
        if c.command in ['RAW']:
            level_bits.extend([ord(x) for x in c.tiles])
    all_bits.append(level_bits)
    return all_bits # return level in 255 bit segments