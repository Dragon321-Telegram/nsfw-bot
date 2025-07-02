# -*- coding: utf-8 -*-
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions, Message
from pyrogram.enums import ChatMemberStatus
import re, os, json

API_ID = 23054181
API_HASH = "e681f6e19614282bd41b94321d395047"
BOT_TOKEN = "7973348977:AAGZ4y-cDwYno41ZCb1omwXYKs_g-vMV6JU"

app = Client("NSFW_Protector", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
warn_count = {}

def load_bad_words():
    path = os.path.join("badwords.txt")
    if not os.path.exists(path): return []
    with open(path, "r", encoding="utf-8") as f:
        return list(set([line.strip().lower() for line in f if line.strip()]))

BAD_WORDS = load_bad_words()

def load_custom_nsfw():
    path = os.path.join("nsfw_custom.json")
    if not os.path.exists(path):
        return {"texts": [], "file_ids": [], "sticker_ids": [], "sticker_sets": []}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for key in ["texts", "file_ids", "sticker_ids", "sticker_sets"]:
            if key not in data:
                data[key] = []
        return data

def save_custom_nsfw(data):
    with open(os.path.join("nsfw_custom.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

NSFW_CUSTOM = load_custom_nsfw()

def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    return text.lower()

def is_nsfw_sticker(msg: Message):
    try:
        if msg.sticker:
            name = msg.sticker.set_name or ""
            emoji = msg.sticker.emoji or ""
            if any(x in name.lower() for x in ["nsfw", "xxx", "sex", "18", "nude", "h0rny"]):
                return True
            if any(e in emoji for e in ["🍆", "💦", "😈", "👅", "🍑", "🫦", "👙"]):
                return True
    except:
        return False
    return False

async def handle_violation(msg: Message):
    uid = msg.from_user.id
    uname = msg.from_user.mention
    warn_count.setdefault(uid, 0)
    warn_count[uid] += 1
    try:
        await app.send_message(msg.chat.id, f"{uname}\n🚫 NSFW content deleted.\nʙᴏᴛ ʙʏ ᴅʀᴀɢᴏɴ ❤️‍🔥")
    except: pass

    if warn_count[uid] >= 3:
        try:
            await msg.chat.restrict_member(uid, permissions=ChatPermissions(can_send_messages=False))
            await app.send_message(msg.chat.id, "𝙄𝙨𝙨 𝙗𝙠𝙡 𝙠𝙤 𝙗𝙤𝙡𝙣𝙚 𝙠𝙖 𝙢𝙤𝙠𝙖𝙖 𝙙𝙚𝙫𝙚. ✅")
        except:
            await app.send_message(msg.chat.id, "❌ I couldn't mute them. Maybe they're admin or I need rights.")

@app.on_message(filters.command("add") & filters.reply & filters.group)
async def add_nsfw(_, msg: Message):
    if not msg.reply_to_message: return
    target = msg.reply_to_message
    text = target.text or target.caption or ""
    if text:
        if text.lower() not in NSFW_CUSTOM["texts"]:
            NSFW_CUSTOM["texts"].append(text.lower())
    elif target.sticker:
        fid = target.sticker.file_unique_id
        if fid not in NSFW_CUSTOM["sticker_ids"]:
            NSFW_CUSTOM["sticker_ids"].append(fid)
        if target.sticker.set_name:
            if target.sticker.set_name not in NSFW_CUSTOM["sticker_sets"]:
                NSFW_CUSTOM["sticker_sets"].append(target.sticker.set_name)
    elif target.photo or target.video or target.animation:
        fid = target.media.file_unique_id
        if fid not in NSFW_CUSTOM["file_ids"]:
            NSFW_CUSTOM["file_ids"].append(fid)

    save_custom_nsfw(NSFW_CUSTOM)
    await msg.reply("✅ This content has been added to NSFW filter.")

@app.on_message(filters.command("remove") & filters.reply & filters.group)
async def remove_nsfw(_, msg: Message):
    if not msg.reply_to_message: return
    target = msg.reply_to_message
    text = target.text or target.caption or ""
    if text and text.lower() in NSFW_CUSTOM["texts"]:
        NSFW_CUSTOM["texts"].remove(text.lower())
    elif target.sticker:
        fid = target.sticker.file_unique_id
        if fid in NSFW_CUSTOM["sticker_ids"]:
            NSFW_CUSTOM["sticker_ids"].remove(fid)
        if target.sticker.set_name and target.sticker.set_name in NSFW_CUSTOM["sticker_sets"]:
            NSFW_CUSTOM["sticker_sets"].remove(target.sticker.set_name)
    elif target.photo or target.video or target.animation:
        fid = target.media.file_unique_id
        if fid in NSFW_CUSTOM["file_ids"]:
            NSFW_CUSTOM["file_ids"].remove(fid)

    save_custom_nsfw(NSFW_CUSTOM)
    await msg.reply("❎ Removed from NSFW filter.")

@app.on_message(filters.command("unmute") & filters.group)
async def unmute_user(_, msg: Message):
    if not msg.reply_to_message: return await msg.reply("Reply to the muted user to unmute.")
    admin = await app.get_chat_member(msg.chat.id, msg.from_user.id)
    if admin.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        return await msg.reply("Only admins can unmute users!")

    user_id = msg.reply_to_message.from_user.id
    try:
        await msg.chat.restrict_member(user_id, permissions=ChatPermissions(can_send_messages=True))
        warn_count[user_id] = 0
        await msg.reply("𝙄𝙨𝙨 𝙗𝙠𝙡 𝙠𝙤 𝙗𝙤𝙡𝙣𝙚 𝙠𝙖 𝙢𝙤𝙠𝙖𝙖 𝙙𝙚𝙫𝙚. ✅")
    except:
        await msg.reply("I couldn’t unmute this user. Do I have rights?")

@app.on_message(filters.group)
async def all_message_check(_, msg: Message):
    if not msg.from_user: return
    uid = msg.from_user.id
    content = msg.text or msg.caption or ""
    clean = clean_text(content)

    if any(word in clean for word in BAD_WORDS) or content.lower() in NSFW_CUSTOM["texts"]:
        try: await msg.delete()
        except: pass
        await handle_violation(msg)
        return

    fid = None
    if msg.sticker:
        fid = msg.sticker.file_unique_id
        set_name = msg.sticker.set_name or ""
        if is_nsfw_sticker(msg) or fid in NSFW_CUSTOM["sticker_ids"] or set_name in NSFW_CUSTOM["sticker_sets"]:
            try: await msg.delete()
            except: pass
            await handle_violation(msg)
            return
    elif msg.photo or msg.video or msg.animation:
        fid = msg.media.file_unique_id
        if fid in NSFW_CUSTOM["file_ids"]:
            try: await msg.delete()
            except: pass
            await handle_violation(msg)
            return

print("🤖 NSFW Filter Bot running... Powered by DRAGON ❤️‍🔥")
app.run()