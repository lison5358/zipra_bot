import logging

# Logging purposes
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logging.info("Importing Modules....")

import pyrogram, asyncio, traceback, re
from utils import *
from funcs import *
from callback import *
from utils import clean_service
from multiprocessing import cpu_count

# Some variables
owner = [1923158017, 1506906677]
bot = pyrogram.Client("mybot", workers=cpu_count() * 4)
bot.start()
me = bot.get_me()
user_command = {
    'start': start_handler, 'ping': ping_handler, 'pong': ping_handler,
    'dbg': json_handler, 'kickme': kbm_handler, 'indomie': indomie_handler,
    'bots': bots_handler, 'test': test, 'notes': notes_handler, 'tags': notes_handler,
    'assembly': code_runner, 'ats': code_runner, 'bash': code_runner, 'c': code_runner, 
    'clojure': code_runner, 'cobol': code_runner, 'coffeescript': code_runner, 'cpp': code_runner, 
    'crystal': code_runner, 'csharp': code_runner, 'd': code_runner, 'elixir': code_runner, 
    'elm': code_runner, 'erlang': code_runner, 'fsharp': code_runner, 'go': code_runner, 'groovy': code_runner, 
    'haskell': code_runner, 'idris': code_runner, 'java': code_runner, 'javascript': code_runner, 
    'julia': code_runner, 'kotlin': code_runner, 'lua': code_runner, 'mercury': code_runner, 
    'nim': code_runner, 'nix': code_runner, 'ocaml': code_runner, 'perl': code_runner, 'php': code_runner, 
    'python': code_runner, 'raku': code_runner, 'ruby': code_runner, 'rust': code_runner, 'scala': code_runner, 
    'swift': code_runner, 'typescript': code_runner, 'copy': copy_handler, 'ocr': ocr_handler
}
admin_command = {
    'del': del_handler, 'pin': pins_handler, 'unpin': pins_handler,
    'mute': kbm_handler,  'getpp': getpp_handler,
    'kick': kbm_handler, 'tag': notes_handler, 'untag': notes_handler
}
creator_command = {
     'cleanservice': clean_service
}
owner_command = {
     'apakek': ocr_handler, 'status': status_handler, 'exec': exec_handler, 'info': info_handler
}
callbacks = {
    'indomie': indomie_callback, 'kick': kick_callback, 'kickgajadi': kick_callback
}

# Callback handlers
@bot.on_callback_query()
async def callback_query_handler(bot, msg: pyrogram.types.CallbackQuery):
    try:
        # print(f'{msg.from_user.username} mengklik tombol di {msg.message.chat.title}, id message: {msg.message.message_id}')
        parser = commands.Parser(me.username, msg.data)
        # print(msg.data)
        command = await parser.get_command()
        args = await parser.get_options(command)
        if command in callbacks:
            return await callbacks[command].main(msg, command, args)
    except Exception as e:
        return await bot.send_message(owner, str(e))


# Service message handlers
@bot.on_message(pyrogram.filters.service)
async def service_filter(_, msg: pyrogram.types.Message):
    if msg.new_chat_members != None:
        if msg.new_chat_members[0].is_self:
            return await msg.reply(f"Halo, perkenalkan namaku {(await msg._client.get_me()).first_name}. Saya sedang dalam pengembangan oleh @ridhwan_aziz. Semoga bot ini bisa berkembang agar bisa mengatur grup ini!\n\nTerima kasih sudah menggunakan zipra!")
        GREETING_MESSAGE = f"Hai {msg.new_chat_members[0].first_name}! Selamat datang di grup {msg.chat.title}"
        INVITED_BY = msg.from_user.first_name if msg.from_user else msg.sender_chat.title
        ADDON = f"\n\nKamu dimasukkan oleh: {INVITED_BY}" if msg.new_chat_members[0].id != msg.from_user.id else ""
        await msg.reply(GREETING_MESSAGE+ADDON, True)
    return await services.main(msg)

# Message handler including edited message
@bot.on_message()
async def message_handlers(bot, msg: pyrogram.types.Message):
    try:
        # Teks pesan
        if msg.text != None:
            text = msg.text
        elif msg.caption != None:
            text = msg.caption
        elif msg.sticker != None:
            text = msg.sticker.emoji if msg.sticker.emoji != None else None
        else:
            text = None

        if msg.chat.type == 'channel':
            return

        # User id
        if msg.from_user != None:
            userid = msg.from_user.id
        else:
            userid = None
        parser = commands.Parser(me.username, text)
        command = await parser.get_command()
        args = await parser.get_options(command)
        if command in user_command:
            return await user_command[command].main(msg, command, args)
        
        if msg.chat.type == 'private':
            return None
        ca = await check_admin.main(msg)
        if command in admin_command:
            if ca == 'administrator' or ca == 'creator':
                return await admin_command[command].main(msg, command, args)
            else:
                return await msg.reply("Kamu harus menjadi admin atau creator grup ini!")
        elif command in creator_command:
            if ca == 'creator':
                return await creator_command[command].main(msg, command, args)
            else:
                return await msg.reply("Kamu harus menjadi creator grup ini!")
        elif command in owner_command:
            if userid in owner:
                return await owner_command[command].main(msg, command, args)
        else:
            pass

        # For Tag handler
        if text == None:
            return
        pattern = re.compile(r'#(\w+)')
        result = pattern.search(text)
        if result != None:
            db = databases.Database('databases/notes.db', 'notes')
            fetched = await db.get_data(['chat_id', 'name'], [str(msg.chat.id), result[1]])
            if fetched != []:
                return await msg.reply(fetched[0][2], True)
            
    except pyrogram.errors.FloodWait as e:
        await asyncio.sleep(e.x)
    except pyrogram.errors.ChatAdminRequired as e:
        return await msg.reply("Aku perlu menjadi admin untuk melakukan itu :)", True)
    except pyrogram.errors.ChatWriteForbidden:
        pass
    except UnicodeDecodeError:
        pass
    except:
        await msg.reply("Terjadi kesalahan", True)
        await bot.send_message(owner, f"Terjadi kesalahan. <a href=\"https://t.me/c/{str(msg.chat.id).split('-100')[1]}/{msg.message_id}\">TKJ</a>")
        return await bot.send_message(owner, traceback.format_exc(), parse_mode=None)
    

try:
    pyrogram.idle()
except KeyboardInterrupt:
    pass
bot.stop()
