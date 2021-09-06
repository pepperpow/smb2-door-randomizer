from binascii import crc32

PRG0="47ba60fad332fdea5ae44b7979fe1ee78de1d316ee027fea2ad5fe3c0d86f25a"
PRG1="6ca47e9da206914730895e45fef4f7393e59772c1c80e9b9befc1a01d7ecf724"

smb2_crcs = [0x7D3F6F3D, 0xE0CA425C] 
smb2_crcs2 = [0x8AA4ACE0, 0x17518181]


def try_to_patch_this_rom_okay(rom, force=False):
    crc = crc32(rom)
    if crc in smb2_crcs or force:
        with open('patch_data/smb2-patch.ips', 'r+b') as f:
            my_patched_rom = patch_ips(rom, f.read())
            return my_patched_rom
    if crc in smb2_crcs2:
        with open('patch_data/smb2-patch-reva.ips', 'r+b') as f:
            my_patched_rom = patch_ips(rom, f.read())
            return my_patched_rom
    return None

def patch_ips (original, patch_data):
    # 
    # Rudimentary IPS patching function
    # 

    # Check magic word "PATCH"
    patched_rom = original

    print("Patching...")
    if patch_data[:5] != b'PATCH':
        print('no magic patch')
        print(patch_data[:5])
        return None
    patch_data = patch_data[5:]
    pos = 0
    while len(patch_data) > 0:
        #  Check magic word "EOF"
        pos = patch_data[:3]
        if pos == b'EOF':
            print("Patch Success")
            return patched_rom
        patch_data = patch_data[3:]
        pos = int.from_bytes(pos, 'big')
        n, patch_data = patch_data[:2], patch_data[2:]
        n = int.from_bytes(n, 'big')
        if n == 0:
            n, patch_data = patch_data[:2], patch_data[2:]
            n = int.from_bytes(n, 'big')
            if pos + n >= len(patched_rom):
                patched_rom = patched_rom + bytearray([0]*(pos - len(patched_rom) + n))
            byt = patch_data[0]
            for i in range(n):
                patched_rom[pos + i] = byt
            patch_data = patch_data[1:]
        else:
            if pos + n >= len(patched_rom):
                patched_rom = patched_rom + bytearray([0]*(pos - len(patched_rom) + n))
            # // RLE Normal
            patched_rom[pos:pos + n] = patch_data[:n]
            patch_data = patch_data[n:]
    print("Patch Terminated Unusually")
    return patched_rom


def getMemoryLocationsFromLst(my_list, bank_num=0):
    my_mem_locs = {
        'prg-{}-{}'.format(x,x+1): 0x2000*x for x in range(0,32,2)
    }
    last_address = 0
    offset = 0
    for entry in my_list.split('\n'):
        mem_address = entry[0:5]
        try:
            mem_address = int('0x{}'.format(mem_address), 16)
        except ValueError:
            continue
        if mem_address < 0x8000 or ':' not in entry:
            continue 
        if mem_address - 0x8000 < last_address:
            offset += 0x4000
        new_entry = entry[5:entry.find(':')].strip()
        my_mem_locs[new_entry] = mem_address - 0x8000 + offset
        if my_mem_locs[new_entry] > 0x1C000:
            my_mem_locs[new_entry] += 0x20000
        last_address = mem_address - 0x8000
    return my_mem_locs
    
def getASMDefsFromLst(my_list):
    my_asm_defs = {}
    for entry in my_list.split('\n'):
        entry = entry.split(';')[0]
        if '=' in entry:
            new_entry = entry[5:].strip()
            name, val = tuple(new_entry.split('=', 1))
            my_asm_defs[name.strip()] = val.strip()
    return my_asm_defs