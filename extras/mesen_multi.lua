--Scripts must be written in Lua (https://www.lua.org)
local json = require("json")
local io = require("io")

local player_obj = {} 
player_obj.__index = player_obj

CHAR_ORDER, CHAR_ORDER_SELECT = {0, 3, 1, 2}, {0, 2, 3, 1}
function player_obj:new (name)
  local me = {
    name = name,
    x = 0, y = 0,
    x_hi = 0, y_hi = 0,
    room = 0, character = 0, frame = 0
  }
  setmetatable(me, self)
  me.name = name
  return me
end

local frame_prg_loc = 0x3f417 
local frame_pos_table = {0,1,0,1,2,3,2,3}
local frame_pos_table_versed = {1,0,1,0,3,2,3,2}
local frame_off = {0,0,1,1,0,0,1,1}

function sprites_to_screen(p, x, y)
  local my_frame = p.frame&0x7F
  local my_dir = (p.frame&0x80) > 0
  for i = 0, 7, 1 do
    if my_dir then pos = frame_pos_table_versed[i+1]
    else pos = frame_pos_table[i+1] end
    local frame_spr = emu.read(frame_prg_loc+(my_frame*4)+pos, emu.memType.prg)
    if frame_spr > 0xf0 then goto cont end
    local frame_spr = frame_spr + frame_off[i+1] + 64 * CHAR_ORDER_SELECT[p.character+1]
    local fpx = i*8
    local frame_px_loc = {fpx%16, (fpx//16)*8}
    local frame_mem = (0x10*frame_spr)
    for row = 0, 7, 1 do
      local me_row = emu.read(frame_mem + row, emu.memType.chrRom)
      for px = 0, 7, 1 do
        local scr_px = px
        if not my_dir then scr_px = 7 - px end
        if (me_row & 2<<(px-1)) > 0 then 
          emu.drawPixel(x+frame_px_loc[1]+scr_px, y+frame_px_loc[2]+row, 0x000000, false, 1)
        end
      end
    end
    emu.drawString(x+frame_px_loc[1]-32, y+frame_px_loc[2], frame_spr, 0xFF0101, false, 1)
    ::cont::
  end
end

my_multi_state = {
  ["active"] = true,
  ["memory"] = {},
  ["players"] = {}
}
  
for i = 0, 3, 1 do
  l = #my_multi_state['players']
  my_multi_state['players'][l+1] = player_obj:new('Player' .. i)
end

local frame_cnt = -1

function stateToJson()
  --Get the emulation state
  local state = emu.getState()


  for i = 0, 3, 1 do
    local hWrite = io.open('player' .. i .. '.json', "rb")
    my_multi_state['players'][i+1] = json.decode(hWrite:read())
    hWrite.close()
  end

  --Draw some rectangles and print some text
  horiz = emu.read(0xec, 0, false) == 1
  my_room = emu.read(0x73F0, emu.memType.cpu, false)
  my_char = emu.read(0x008f, 0, false)
  cam_x =  emu.read(0xfd, emu.memType.cpu, false)
  cam_y =  emu.read(0xfc, emu.memType.cpu, false)
  cam_topleft =  emu.read(0xcf, emu.memType.cpu, false)
  cam_tile = cam_topleft >> 4
  cam_pg = cam_topleft & 0xF
  if horiz then
    cam_real_pos = ((cam_pg)*16 + cam_tile + 3)%160
  else
    cam_real_pos = ((cam_pg)*15 + cam_tile + 3)%150
  end

  emu.drawString(12, 12, "cam_x: " .. cam_x, 0xFFFFFF, 0xFF000000, 1)
  emu.drawString(12, 21, "cam_y: " .. cam_y, 0xFFFFFF, 0xFF000000, 1)
  emu.drawString(12, 30, "TOPLEFT: " .. cam_real_pos, 0xFFFFFF, 0xFF000000, 1)

  local my_player = player_obj:new('Player' .. my_char)
  my_player.x_hi = emu.read(0x0014, 0, false)
  my_player.y_hi = emu.read(0x001e, 0, false)
  my_player.x = emu.read(0x0028, 0, false)
  my_player.y = emu.read(0x0032, 0, false)
  my_player.room = my_room
  my_player.character = my_char
  my_player.frame = emu.read(0x00c7, 0, false) + (emu.read(0x9d, 0, false)*0x80)

  print(my_player)

  for index, p in ipairs(my_multi_state.players) do
    print(index)
    if p.room == my_room and p.name ~= my_player.name then
      local my_x = 0
      local my_y = 0
      if horiz then
        my_x = (p.x_hi*256 + p.x) - (cam_real_pos*16) - (cam_x%16)
        my_y = p.y
        sprites_to_screen(p, my_x, my_y)
        emu.drawString(my_x, my_y-8, p.name, 0xFFFFFF, 0x000000, true, 1)
      else
        my_x = p.x
        my_y = (p.y_hi*240 + p.y) - (cam_real_pos//15) - cam_y
        sprites_to_screen(p, my_x, my_y)
        emu.drawString(my_x, my_y-8, p.name, 0xFFFFFF, 0x000000, true, 1)
      end
    end
  end


  frame_cnt = frame_cnt + 1
  if frame_cnt%2 == 0 then
    local hWrite = io.open('player' .. my_player.character .. '.json', "wb")
    hWrite:write(json.encode(my_player))
    hWrite:close()
  end

end

--Register some code (printInfo function) that will be run at the end of each frame
emu.addEventCallback(stateToJson, emu.eventType.endFrame)

--Display a startup message
emu.displayMessage("Script", "Example Lua script loaded.")
