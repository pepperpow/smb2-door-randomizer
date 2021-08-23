while (true) do
    gui.text(10,50,"Running...");
    tbl = input.get()
    for i = 0, 9 do
        if i == memory.readbyte(0x535) then
            gui.text(20,60 + 10*i,memory.readbyte(0x51D + i*2))
            gui.text(40,60 + 10*i,memory.readbyte(0x51E + i*2)%16)
            gui.text(60,60 + 10*i,math.floor(memory.readbyte(0x51E + i*2)/16))
        end
        if i ~= memory.readbyte(0x535) then
            gui.text(10,60 + 10*i,memory.readbyte(0x51D + i*2))
            gui.text(30,60 + 10*i,memory.readbyte(0x51E + i*2)%16)
        end
    end
    if memory.readbyte(0x627) == 0 then
        if tbl['numpad0'] then
            i = memory.readbyte(0x535)
            memory.writebyte(0x4e7, memory.readbyte(0x51D + i*2))
            door_ptrs = 0x51d
            -- while door_ptrs < 0x51d + 20 do
            --     memory.writebyte(door_ptrs, 0x0)
            --     door_ptrs = door_ptrs + 1
            -- end
            memory.writebyte(0x4e8, math.floor(memory.readbyte(0x51E + i*2)/16))
            memory.writebyte(0x4e9, memory.readbyte(0x51E + i*2)%16)
            memory.writebyte(0x534, 0)
            memory.writebyte(0x4ea, 0)
            memory.writebyte(0x627, 1)
            emu.frameadvance();
            memory.writebyte(0x627, 0)
        end
    end
    emu.frameadvance();
end;