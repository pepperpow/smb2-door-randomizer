-- Script to rip full level data from the original game
-- Automatically runs
local json = require("json")
local io = require("io")

function bytes_to_array(mem, len)
    arr = {}
    for i = 0, len-1, 1 do
        arr[#arr+1] = memory.readbyte(mem + i)
    end
    return arr
end

function write_to_file()
    local my_level_num = memory.readbyte(0x531) * 10 + memory.readbyte(0x532)
    if my_level_num < 200 then
        local my_thing = {
            ["my_level_num"] = my_level_num,
            ["my_level_world_num"] = memory.readbyte(0x635),
            ["my_header"] = bytes_to_array(0x7800, 0x4),
            ["my_ptrs"] = bytes_to_array(0x51d, 0x534 - 0x51d),
            ["my_enemies"] = bytes_to_array(0x7b00, 0x100),
            ["my_level"] = bytes_to_array(0x6000, 0x960)
        }
        emu.print(my_level_num)

        local my_dir = "grabbed_levels/"
        local my_file_name = my_level_num .. ".json"
        local full_name = my_dir .. my_file_name

        local hWrite = io.open(full_name, "wb")
        hWrite:write(json.encode(my_thing))
        hWrite:close()

        --Load the table

        emu.pause()
        my_level_num = my_level_num + 1
        if my_level_num < 200 then
            memory.writebyte(0x531, math.floor(my_level_num / 10) )
            local door_ptrs = 0x51d
            while door_ptrs < 0x51d + 20 do
                memory.writebyte(door_ptrs, 0x0)
                door_ptrs = door_ptrs + 1
            end
            memory.writebyte(0x532, my_level_num % 10 )
            memory.writebyte(0x534, 0 )
            memory.writebyte(0x635, math.floor(my_level_num / 30) )
            memory.setregister('pc', 0xe43b)
        end

        if my_level_num < 200 then
            emu.unpause()
        end
    end
end


while (true) do
    gui.text(50,50,"Running...");
    local tbl = input.get()
    if memory.readbyte(0x627) == 0 then
        if tbl['0'] then
            write_to_file()
            local i = 120
            -- while input.get()['numpad0'] do
            while true do 
                emu.frameadvance();
                i = i - 1
                if i == 0 then
                    i = 120
                    write_to_file()
                end
            end
        end
    end
    emu.frameadvance();
end;