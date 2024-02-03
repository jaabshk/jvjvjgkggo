from config import Config
import logging
import os
import asyncio
import subprocess
import random
from pathlib import Path
try:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
except ImportError:
    print("python-telegram-bot is not installed. Installing it now...")
    try:
        subprocess.check_call(["pip3", "install", "python-telegram-bot"])
        print("python-telegram-bot has been successfully installed.")
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
    except Exception as e:
        try:
            subprocess.check_call(["pip", "install", "python-telegram-bot"])
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
            print("python-telegram-bot has been successfully installed using pip3.")
        except Exception as e:
            print("Failed to install python-telegram-bot with pip and pip3:", str(e))
            exit(0)
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
try:
    from telethon import TelegramClient, sync, functions, errors, events, types
except ImportError:
    print("telethon is not installed. Installing it now...")
    try:
        subprocess.check_call(["pip3", "install", "telethon"])
        print("telethon has been successfully installed.")
        from telethon import TelegramClient, sync, functions, errors, events, types
    except Exception as e:
        try:
            subprocess.check_call(["pip", "install", "telethon"])
            from telethon import TelegramClient, sync, functions, errors, events, types
            print("telethon has been successfully installed using pip.")
        except Exception as e:
            print("Failed to install telethon with pip and pip:", str(e))
            exit(0)
from telethon.tl.functions.account import UpdateStatusRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.messages import GetMessagesViewsRequest
from telethon.tl.functions.messages import SendReactionRequest
try:
    import requests
except ImportError:
    print("requests is not installed. Installing it now...")
    try:
        subprocess.check_call(["pip3", "install", "requests"])
        print("requests has been successfully installed.")
        import requests
    except Exception as e:
        try:
            subprocess.check_call(["pip", "install", "requests"])
            import requests
            print("requests has been successfully installed using pip.")
        except Exception as e:
            print("Failed to install requests with pip and pip:", str(e))
            exit(0)
import json
API_ID = Config.APP_ID
API_HASH = Config.API_HASH
bot_token = Config.TG_BOT_TOKEN
running_processes = {}
try:
    with open("echo_data.json", "r") as json_file:
        info = json.load(json_file)
except FileNotFoundError:
    info = {}

if "token" not in info:
    while (True):
        response = requests.request(
            "GET", f"https://api.telegram.org/bot{bot_token}/getme")
        response_json = response.json()
        if (response_json["ok"] == True):
            info["token"] = bot_token
            with open("echo_data.json", "w") as json_file:
                json.dump(info, json_file)
            break
        else:
            print("token is not correct !")
else:
    bot_token = info["token"]

if "sudo" not in info:
    info["sudo"] = str(input("Enter the your telegram ID : "))
    info["admins"] = {}
    with open("echo_data.json", "w") as json_file:
        json.dump(info, json_file)


clients = {}
async def background_task(phonex, bot_username, sudo, send_to):
    global clients
    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
            "chat_id": sudo,
            "text": f"- جاري تشغيل :  {phonex}"
    })
    clients[f"{phonex}-{sudo}"] = TelegramClient(f"echo_ac/{sudo}/{phonex}", API_ID, API_HASH, device_model="TYTHON")
    clientx = clients[f"{phonex}-{sudo}"]
    try:
        @clientx.on(events.NewMessage)
        async def handle_new_message(event):
            if event.is_channel:
                await clientx(GetMessagesViewsRequest(
                    peer=event.chat_id,
                    id=[event.message.id],
                    increment=True
                ))
        await clientx.connect()
        await clientx(UpdateStatusRequest(offline=False))
        if not await clientx.is_user_authorized():
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                "chat_id": sudo,
                "text": f"- الحساب غير مسجل في البوت : {phonex}"
            })
            await clientx.disconnect()
            stop_background_task(phonex, sudo)
            return 0
    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
            "chat_id": sudo,
            "text": f"- حدث خطا في الحساب : {phonex}"
        })
        await clientx.disconnect()
        stop_background_task(phonex, sudo)
        return 0
    else:
        me = await clientx.get_me()
        user_id = me.id
        if (send_to == "انا"):
            send_to = sudo
        elif (send_to == "حساب"):
            send_to = user_id
        response = requests.request(
            "GET", f"https://bot.keko.dev/api/?login={user_id}&bot_username={bot_username}")
        response_json = response.json()
        if response_json.get("ok", False):
            echo_token = response_json.get("token", "")
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                "chat_id": sudo,
                "text": f"- تم تشغيل الحساب ! \n\n- سيتم ارسال النقاط الى : {send_to} \n\n- الحساب : {phonex}",
            })
            while True:
                response = requests.request(
                    "GET", f"https://bot.keko.dev/api/?token={echo_token}")
                response_json = response.json()
                if not response_json.get("ok", False):
                    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                        "chat_id": sudo,
                        "text": "- نفذت قنوات البوت !"+f" \n\n- الحساب : {phonex}\n\n- المحاوله التالية بعد : 10s"
                    })
                    await asyncio.sleep(10)
                    continue
                if (response_json.get("canleave", False)):
                    for chat in response_json["canleave"]: 
                        try:
                            await clientx.delete_dialog(chat)
                            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                                "chat_id": sudo,
                                "text": "- تم مغادرة : "+str(chat)+"بسبب انتهاء وقت الاشتراك !"+f" \n\n- الحساب : {phonex}"
                            })
                            await asyncio.sleep(random.randint(3,10))
                        except Exception as e:
                            print(f"Error: {str(e)}")
                requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                    "chat_id": sudo,
                    "text": "- جاري الاشتراك في : " +response_json.get("return", "")+f" \n\n- الحساب : {phonex}"
                })
                if response_json.get("type", "") == "link":
                    try:
                        await clientx(ImportChatInviteRequest(response_json.get("tg", "")))
                        await asyncio.sleep(random.randint(2,5))
                        messages = await clientx.get_messages(
                            int(response_json.get("return", "")), limit=20)
                        MSG_IDS = [message.id for message in messages]
                        await asyncio.sleep(random.randint(2,5))
                        await clientx(GetMessagesViewsRequest(
                            peer=int(response_json.get("return", "")),
                            id=MSG_IDS,
                            increment=True
                        ))
                        try:
                            await clientx(SendReactionRequest(
                                peer=int(response_json.get("return", "")),
                                msg_id=messages[0].id,
                                big=True,
                                add_to_recent=True,
                                reaction=[types.ReactionEmoji(
                                    emoticon='👍'
                                )]
                            ))
                        except Exception as e:
                            print(f"Error: {str(e)}")
                    except errors.FloodWaitError as e:
                        timeoutt = random.randint(e.seconds,e.seconds+10)
                        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                            "chat_id": sudo,
                            "text": f"- تم حظر الحساب !\n\n- اعادة المحاوله بعد : {timeoutt}s \n\n- الحساب : {phonex}"
                        })
                        try:
                            await clientx(UpdateStatusRequest(offline=True))
                            await clientx.disconnect()
                            await asyncio.sleep(timeoutt)
                            await clientx.connect()
                            await clientx(UpdateStatusRequest(offline=False))
                        except Exception as e:
                            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                                "chat_id": sudo,
                                "text": f"- حدث خطا في الحساب : {phonex}"
                            })
                            stop_background_task(phonex, sudo)
                            return 0
                        continue
                    except Exception as e:
                        timeoutt = random.randint(200,400)
                        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                            "chat_id": sudo,
                            "text": f"- خطا في الحساب !\n\n- اعادة المحاوله بعد :  {timeoutt}s \n\n{str(e)}\n\n- الحساب : {phonex}"
                        })
                        await asyncio.sleep(timeoutt)
                else:
                    try:
                        await clientx(JoinChannelRequest(response_json.get("return", "")))
                        await asyncio.sleep(random.randint(2,5))
                        entity = await clientx.get_entity(response_json.get("return", ""))
                        await asyncio.sleep(random.randint(2,5))
                        messages = await clientx.get_messages(entity, limit=10)
                        await asyncio.sleep(random.randint(2,5))
                        MSG_IDS = [message.id for message in messages]
                        await clientx(GetMessagesViewsRequest(
                            peer=response_json.get("return", ""),
                            id=MSG_IDS,
                            increment=True
                        ))
                        try:
                            await clientx(SendReactionRequest(
                                peer=response_json.get("return", ""),
                                msg_id=messages[0].id,
                                big=True,
                                add_to_recent=True,
                                reaction=[types.ReactionEmoji(
                                    emoticon='👍'
                                )]
                            ))
                        except Exception as e:
                            print(f"Error: {str(e)}")
                    except errors.FloodWaitError as e:
                        timeoutt = random.randint(e.seconds,e.seconds+10)
                        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                            "chat_id": sudo,
                            "text": f"- تم حظر الحساب !\n\n- اعادة المحاوله بعد : {timeoutt}s \n\n- الحساب : {phonex}"
                        })
                        try:
                            await clientx(UpdateStatusRequest(offline=True))
                            await clientx.disconnect()
                            await asyncio.sleep(timeoutt)
                            await clientx.connect()
                            await clientx(UpdateStatusRequest(offline=False))
                        except Exception as e:
                            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                                "chat_id": sudo,
                                "text": f"- حدث خطا في الحساب : {phonex}"
                            })
                            stop_background_task(phonex, sudo)
                            return 0
                        continue
                    except Exception as e:
                        timeoutt = random.randint(200,400)
                        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                            "chat_id": sudo,
                            "text": f"- خطا في الحساب !\n\n- اعادة المحاوله بعد :  {timeoutt}s \n\n{str(e)}\n\n- الحساب : {phonex}"
                        })
                        try:
                            await clientx(UpdateStatusRequest(offline=True))
                            await clientx.disconnect()
                            await asyncio.sleep(timeoutt)
                            await clientx.connect()
                            await clientx(UpdateStatusRequest(offline=False))
                        except Exception as e:
                            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                                "chat_id": sudo,
                                "text": f"- حدث خطا في الحساب : {phonex}"
                            })
                            stop_background_task(phonex, sudo)
                            return 0
                        continue
                response = requests.request(
                    "GET", f"https://bot.keko.dev/api/?token={echo_token}&to_id={send_to}&done="+response_json.get("return", ""))
                response_json = response.json()
                timeoutt = random.randint(int(info["sleeptime"]),(int(info["sleeptime"])*1.3))
                if not response_json.get("ok", False):
                    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                        "chat_id": sudo,
                        "text": f"- "+response_json.get("msg", "")+f" \n\n- {phonex}"
                    })
                else:
                    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                        "chat_id": sudo,
                        "text": f"- تم الاشترك في القناة !\n\n- عدد نقاط الحساب : "+str(response_json.get("c", ""))+f"\n\n- سيتم مغادرة القناة بعد : " + str(response_json.get("timeout", ""))+ 's'  +  f" \n\n- الحساب : {phonex}\n\n- المحاوله التالية بعد : "+str(timeoutt) + 's'
                    })
                try:
                    await clientx(UpdateStatusRequest(offline=True))
                    await clientx.disconnect()
                    await asyncio.sleep(timeoutt)
                    await clientx.connect()
                    await clientx(UpdateStatusRequest(offline=False))
                except Exception as e:
                    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                        "chat_id": sudo,
                        "text": f"- حدث خطا في الحساب : {phonex}"
                    })
                    stop_background_task(phonex, sudo)
                    return 0
        else:
            requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
                "chat_id": sudo,
                "text": f"- "+response_json.get("msg", "")+f" \n\n- {phonex}"
            })
        await clientx.disconnect()
        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
            "chat_id": sudo,
            "text": f"- تم ايقاف تشغيل الحساب : {phonex}"
        })
        stop_background_task(phonex, sudo)

def start_background_task(phone, bot_username, chat_id, send_to):
    chat_id = str(chat_id)
    phone = str(phone)
    stop_background_task(phone, chat_id)
    if chat_id not in running_processes:
        running_processes[chat_id] = {}
    if phone not in running_processes[chat_id]:
        task = asyncio.create_task(background_task(phone, bot_username, chat_id,send_to))
        running_processes[chat_id][phone] = task

def stop_all_background_tasks(chat_id):
    chat_id = str(chat_id)
    if chat_id in running_processes:
        for phone, task in running_processes[chat_id].items():
            if not task.done():
                task.cancel()
                clients[f"{phone}-{chat_id}"].disconnect()
                del clients[f"{phone}-{chat_id}"]
                print(f"Stopped background task for phone {phone} and chat_id {chat_id}")
            else:
                print(f"Background task for phone {phone} and chat_id {chat_id} is not running.")
        running_processes.pop(chat_id, None)
    else:
        print(f"No running tasks found for chat_id {chat_id}.")

def stop_background_task(phone, chat_id):
    chat_id = str(chat_id)
    phone = str(phone)
    if chat_id in running_processes and phone in running_processes[chat_id]:
        task = running_processes[chat_id][phone]
        clients[f"{phone}-{chat_id}"].disconnect()
        del clients[f"{phone}-{chat_id}"]
        if not task.done():
            task.cancel()
            print(f"Stopped background task for phone {phone} and chat_id {chat_id}")
        else:
            print(f"Background task for phone {phone} and chat_id {chat_id} is not running.")
        running_processes[chat_id].pop(phone, None)
    else:
        print(f"No background task found for phone {phone} and chat_id {chat_id}.")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
if not os.path.isdir("echo_ac"):
    os.makedirs("echo_ac")
what_need_to_do_echo = {}
if "sleeptime" not in info:
    info["sleeptime"] = 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global what_need_to_do_echo
    if update.message and update.message.chat.type == "private":
        if (str(update.message.chat.id) == str(info["sudo"])):
            if not os.path.isdir("echo_ac/"+str(update.message.chat.id)):
                os.makedirs("echo_ac/"+str(update.message.chat.id))
            what_need_to_do_echo[str(update.message.chat.id)] = ""
            keyboard = [
                [
                    InlineKeyboardButton(
                        "اضافة حساب", callback_data="addecho"),
                    InlineKeyboardButton("حذف حساب", callback_data="delecho"),
                ],
                [
                    InlineKeyboardButton("الحسابات", callback_data="myecho")
                ],
                [
                    InlineKeyboardButton(
                        "اضافة مشترك", callback_data="addadminecho"),
                    InlineKeyboardButton(
                        "حذف مشترك", callback_data="deladminecho"),
                ],
                [
                    InlineKeyboardButton(
                        "المشتركين", callback_data="myadminsecho"),
                ],
                [
                    InlineKeyboardButton(
                        "سرعة التجميع", callback_data="sleeptime"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("• اهلا بك في بوت تجميع النقاط\n\n• تم تطوير البوت بواسطة فريق تايثون \n\n• قناة البوت للتحديثات : @TYTHN \n\n• سرعة التجميع : " + str(info["sleeptime"]) + 's' ,reply_markup=reply_markup)

        elif str(update.message.chat.id) in info["admins"]:
            what_need_to_do_echo[str(update.message.chat.id)] = ""
            keyboard = [
                [
                    InlineKeyboardButton(
                        "اضافة حساب", callback_data="addecho"),
                    InlineKeyboardButton("حذف حساب", callback_data="delecho"),
                ],
                [
                    InlineKeyboardButton("الحسابات", callback_data="myecho")
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("• بوت تجميع نقاط بوتات التمويل\n\n• سرعة التجميع : " + str(info["sleeptime"]) + 's' ,reply_markup=reply_markup)

def contact_validate(text):
    text = str(text)  
    if len(text) > 0:
        if text[0] == '+':
            if text[1:].isdigit():
                return True
    return False


async def echoMaker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global what_need_to_do_echo
    if not update.message or update.message.chat.type != "private":
        return 0
    if (str(update.message.chat.id) != str(info["sudo"]) and str(update.message.chat.id) not in info["admins"]):
        return 0
    if update.message.text and update.message.text.startswith("/run "):
        filename = update.message.text.split(" ")[1]
        what_need_to_do_echo[str(update.message.chat.id)] = f"run:{filename}"
        await update.message.reply_text(f"• ارسل معرف البوت المطلوب تجميع النقاط منه : \n\n- الحساب : {filename}", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("رجوع", callback_data="sudohome")],
        ]))
    elif update.message.text and update.message.text.startswith("/stop "):
        filename = update.message.text.split(" ")[1]
        await update.message.reply_text(f"- تم ايقاف تشغيل الحساب : {filename}", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("رجوع", callback_data="sudohome")],
        ]))
        stop_background_task(filename, update.message.chat.id)
    elif (update.message.text and (str(update.message.chat.id) in what_need_to_do_echo)):
        if (what_need_to_do_echo[str(update.message.chat.id)] == "addecho"):
            if (not contact_validate(update.message.text)):
                await update.message.reply_text(f"• رقم الهاتف غير صحيح !", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("رجوع", callback_data="sudohome")],
                ]))
                return
            client = TelegramClient(
                f"echo_ac/{update.message.chat.id}/{update.message.text}", API_ID, API_HASH, device_model="TYTHON")
            try:
                await client.connect()
                what_need_to_do_echo[str(
                    update.message.chat.id)+":phone"] = update.message.text
                eeecho = await client.send_code_request(update.message.text)
                what_need_to_do_echo[str(
                    update.message.chat.id)+":phone_code_hash"] = eeecho.phone_code_hash
                await update.message.reply_text(f"• ارسل رمز تسجيل الدخول : ", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("رجوع", callback_data="sudohome")],
                ]))
                what_need_to_do_echo[str(update.message.chat.id)] = "echocode"
            except Exception as e:
                await client.log_out()
                what_need_to_do_echo[str(update.message.chat.id)] = ""
                await update.message.reply_text(f"• حدث خطأ غير متوقع : {str(e)}", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("رجوع", callback_data="sudohome")],
                ]))
            await client.disconnect()
        elif (what_need_to_do_echo[str(update.message.chat.id)] == "sleeptime"):
            info["sleeptime"] = int(update.message.text)
            await update.message.reply_text(f"• تم الحفظ بنجاح !", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="sudohome")],
            ]))
            with open("echo_data.json", "w") as json_file:
                json.dump(info, json_file)
            what_need_to_do_echo[str(update.message.chat.id)] = ""
        elif (what_need_to_do_echo[str(update.message.chat.id)] == "deladminecho"):
            if os.path.isdir("echo_ac/"+str(update.message.text)):
                os.rmdir("echo_ac/"+str(update.message.text))
            what_need_to_do_echo[str(update.message.chat.id)] = ""
            if "admins" not in info:
                info["admins"] = {}
            if str(update.message.text) in info["admins"]:
                del running_processes[str(update.message.text)]
                with open("echo_data.json", "w") as json_file:
                    json.dump(info, json_file)
                await update.message.reply_text(f"• تم حذف المشترك بنجاح !", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("رجوع", callback_data="sudohome")],
                ]))
                stop_all_background_tasks(str(update.message.chat.id))
            else:
                await update.message.reply_text(f"• هاذه المشترك غير مسجل !", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("رجوع", callback_data="sudohome")],
                ]))
        elif (what_need_to_do_echo[str(update.message.chat.id)] == "addadminecho"):
            what_need_to_do_echo[str(update.message.chat.id)] = ""
            if not os.path.isdir("echo_ac/"+str(update.message.text)):
                os.makedirs("echo_ac/"+str(update.message.text))
            if "admins" not in info:
                info["admins"] = {}
            info["admins"][str(update.message.text)] = str(5)
            with open("echo_data.json", "w") as json_file:
                json.dump(info, json_file)
            await update.message.reply_text(f"• تم اضافة مشترك جديد بنجاح !\n\n", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="sudohome")],
            ]))
        elif (what_need_to_do_echo[str(update.message.chat.id)] == "echocode"):
            what_need_to_do_echo[str(update.message.chat.id)] = "anthercode"
            what_need_to_do_echo[str(
                update.message.chat.id)+"code"] = update.message.text
            await update.message.reply_text(f"• ارسل رمز تحقق بخطوتين : \n\n• اذا لم يكن هناك رمز ارسل اي شيء : ")
        elif (what_need_to_do_echo[str(update.message.chat.id)] == "anthercode"):
            client = TelegramClient(f"echo_ac/{update.message.chat.id}/"+str(
                what_need_to_do_echo[str(update.message.chat.id)+":phone"]), API_ID, API_HASH, device_model="TYTHON")
            await client.connect()
            try:
                await client.sign_in(phone=what_need_to_do_echo[str(update.message.chat.id)+":phone"], code=what_need_to_do_echo[str(update.message.chat.id)+"code"], phone_code_hash=what_need_to_do_echo[str(update.message.chat.id)+":phone_code_hash"])
                await update.message.reply_text(f"• تم تسجيل الدخول بنجاح : "+str(what_need_to_do_echo[str(update.message.chat.id)+":phone"]), reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("رجوع", callback_data="sudohome")],
                ]))
                what_need_to_do_echo[str(update.message.chat.id)] = ""
            except errors.SessionPasswordNeededError:
                await client.sign_in(password=update.message.text, phone_code_hash=what_need_to_do_echo[str(update.message.chat.id)+":phone_code_hash"])
                await update.message.reply_text(f"• تم تسجيل الدخول بنجاح !\n\n- "+str(what_need_to_do_echo[str(update.message.chat.id)+":phone"]), reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("رجوع", callback_data="sudohome")],
                ]))
                what_need_to_do_echo[str(update.message.chat.id)] = ""
            except Exception as e:
                await client.log_out()
                what_need_to_do_echo[str(update.message.chat.id)] = ""
                await update.message.reply_text(f"• حدث خطأ غير متوقع : {str(e)}", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("رجوع", callback_data="sudohome")],
                ]))
            await client.disconnect()
        elif (what_need_to_do_echo[str(update.message.chat.id)].startswith("setlimt:")):
            admin = what_need_to_do_echo[str(
                update.message.chat.id)].split(":")[1]
            await update.message.reply_text(f"• تم تعين عدد الحسابات المسموحه لهذه المشترك !\n\n- ايدي الحساب : {admin}", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="myadminsecho")],
            ]))
            what_need_to_do_echo[str(update.message.chat.id)] = ""
            if "admins" not in info:
                info["admins"] = {}
            info["admins"][str(admin)] = str(update.message.text)
            with open("echo_data.json", "w") as json_file:
                json.dump(info, json_file)
        elif (what_need_to_do_echo[str(update.message.chat.id)] == "runall"):
            await update.message.reply_text(f"• ارسل ايدي الحساب لتجميع له النقاط :\n\n- ارسل : انا : لارسال نقاط لهاذا الحساب\n- ارسل : حساب : لبقاء النقاط في الحساب", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="sudohome")],
            ]))
            what_need_to_do_echo[str(update.message.chat.id)] = "runall2"
            what_need_to_do_echo[str(
                update.message.chat.id)+"code"] = update.message.text
        elif (what_need_to_do_echo[str(update.message.chat.id)] == "runall2"):
            await update.message.reply_text(f"• تم تشغيل جميع الحسابات !", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="sudohome")],
            ]))
            directory_path = Path(f"echo_ac/{update.message.chat.id}")
            file_list = [file.name for file in directory_path.iterdir(
            ) if file.is_file() and file.name.endswith('.session')]
            file_list = list(set(file_list))
            for filename in file_list:
                filename = filename.split(".")[0]
                start_background_task(
                    str(filename), str(what_need_to_do_echo[str(
                update.message.chat.id)+"code"]), str(update.message.chat.id), str(update.message.text))
            what_need_to_do_echo[str(update.message.chat.id)] = ""
        elif (what_need_to_do_echo[str(update.message.chat.id)].startswith("run:")):
            filename = what_need_to_do_echo[str(
                update.message.chat.id)].split(":")[1]
            await update.message.reply_text(f"• ارسل ايدي الحساب لتجميع له النقاط :\n\n- ارسل : انا : لارسال نقاط لهاذا الحساب\n- ارسل : حساب : لبقاء النقاط في الحساب", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="sudohome")],
            ]))
            what_need_to_do_echo[str(update.message.chat.id)] = "run2:"+str(filename)
            what_need_to_do_echo[str(
                update.message.chat.id)+"code"] = update.message.text
        elif (what_need_to_do_echo[str(update.message.chat.id)].startswith("run2:")):
            filename = what_need_to_do_echo[str(
                update.message.chat.id)].split(":")[1]
            await update.message.reply_text(f"• تم بدء التشغيل !\n\n-الحساب : {filename}", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="sudohome")],
            ]))
            start_background_task(
                    str(filename), str(what_need_to_do_echo[str(
                update.message.chat.id)+"code"]), str(update.message.chat.id), str(update.message.text))
            what_need_to_do_echo[str(update.message.chat.id)] = ""


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global what_need_to_do_echo
    query = update.callback_query
    await query.answer()
    if not query.message or query.message.chat.type != "private":
        return 0
    if (str(query.message.chat.id) != str(info["sudo"]) and str(query.message.chat.id) not in info["admins"]):
        return 0
    if (query.data == "addecho"):
        if (str(query.message.chat.id) == str(info["sudo"])):
            what_need_to_do_echo[str(query.message.chat.id)] = query.data
            await query.edit_message_text(text=f"• ارسل رقم هاتف الحساب :", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="sudohome")],
            ]))
        elif (str(query.message.chat.id) in info["admins"]):
            directory_path = Path(f"echo_ac/{query.message.chat.id}")
            file_list = [file.name for file in directory_path.iterdir(
            ) if file.is_file() and file.name.endswith('.session')]
            file_list = list(set(file_list))
            if (int(len(file_list)) <= int(info["admins"][str(query.message.chat.id)])):
                what_need_to_do_echo[str(query.message.chat.id)] = query.data
                await query.edit_message_text(text=f"• ارسل رقم هاتف الحساب :", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("رجوع", callback_data="sudohome")],
                ]))
            else:
                await query.edit_message_text(text=f"• لا يمكنك اضافة المزيد من الحسابات !", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("رجوع", callback_data="sudohome")],
                ]))
    elif (query.data == "deladminecho"):
        what_need_to_do_echo[str(query.message.chat.id)] = query.data
        await query.edit_message_text(text=f"• ارسل ايدي المشترك :", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("رجوع", callback_data="sudohome")],
        ]))
    elif (query.data == "addadminecho"):
        what_need_to_do_echo[str(query.message.chat.id)] = query.data
        await query.edit_message_text(text=f"• ارسل ايدي المشترك :", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("رجوع", callback_data="sudohome")],
        ]))
    elif (query.data == "sudohome"):
        what_need_to_do_echo[str(query.message.chat.id)] = ""
        if (str(query.message.chat.id) == str(info["sudo"])):
            keyboard = [
                [
                    InlineKeyboardButton(
                        "اضافة حساب", callback_data="addecho"),
                    InlineKeyboardButton("حذف حساب", callback_data="delecho"),
                ],
                [
                    InlineKeyboardButton("الحسابات", callback_data="myecho")
                ],
                [
                    InlineKeyboardButton(
                        "اضافة مشترك", callback_data="addadminecho"),
                    InlineKeyboardButton(
                        "حذف مشترك", callback_data="deladminecho"),
                ],
                [
                    InlineKeyboardButton(
                        "المشتركين", callback_data="myadminsecho"),
                ],
                [
                    InlineKeyboardButton(
                        "سرعة التجميع", callback_data="sleeptime"),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("• بوت تجميع نقاط بوتات التمويل\n\n• سرعة التجميع : "  + str(info["sleeptime"]) + 's' ,reply_markup=reply_markup)
        elif (str(query.message.chat.id) in info["admins"]):
            keyboard = [
                [
                    InlineKeyboardButton(
                        "اضافة حساب", callback_data="addecho"),
                    InlineKeyboardButton("حذف حساب", callback_data="delecho"),
                ],
                [
                    InlineKeyboardButton("الحسابات", callback_data="myecho")
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("• بوت تجميع نقاط بوتات التمويل\n\n• سرعة التجميع : "  + str(info["sleeptime"]) + 's' , reply_markup=reply_markup)
    elif (query.data == "sleeptime"):
        await query.edit_message_text(f"• يرجى إرسال عدد الثواني بين كل محاولة اشتراك في القنوات :", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("رجوع", callback_data="myadminsecho")],
        ]))
        what_need_to_do_echo[str(query.message.chat.id)] = query.data
    elif (query.data == "myadminsecho"):
        if "admins" not in info:
            info["admins"] = {}
        keyboard = []
        for key, value in info["admins"].items():
            button = InlineKeyboardButton(
                f"{key}", callback_data=f"setlimt:{key}")
            button2 = InlineKeyboardButton(
                str(value), callback_data=f"setlimt:{key}")
            keyboard.append([button, button2])
        keyboard.append([InlineKeyboardButton(
            "رجوع", callback_data="sudohome")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("• المشتركين في البوت :\n\n• اضغط على ايدي المشترك لتعديل عدد الحسابات التي يمكنه اضافتها", reply_markup=reply_markup)
    elif query.data.startswith("setlimt:"):
        what_need_to_do_echo[str(query.message.chat.id)] = query.data
        admin = query.data.split(":")[1]
        await query.edit_message_text(f"• ارسل عدد الحسابات المسموحه لهاذا المشترك : \n\n- ايدي الحساب {admin}", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("رجوع", callback_data="myadminsecho")],
        ]))
    elif (query.data == "delecho"):
        directory_path = Path(f"echo_ac/{query.message.chat.id}")
        file_list = [file.name for file in directory_path.iterdir(
        ) if file.is_file() and file.name.endswith('.session')]
        file_list = list(set(file_list))
        keyboard = []
        for filename in file_list:
            filename = filename.split(".")[0]
            button = InlineKeyboardButton(
                f"{filename}", callback_data=f"del:{filename}")
            button2 = InlineKeyboardButton(
                f"حذف", callback_data=f"del:{filename}")
            keyboard.append([button, button2])
        keyboard.append([InlineKeyboardButton(
            "رجوع", callback_data="sudohome")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("• الحسابات المسجلة في البوت : \n\n• اضغط  على حذف لحذف الحساب\n\n", reply_markup=reply_markup)
    elif query.data.startswith("del:"):
        filename = query.data.split(":")[1]
        stop_background_task(filename, query.message.chat.id)
        try:
            client = TelegramClient(
                f"echo_ac/{query.message.chat.id}/{filename}", API_ID, API_HASH, device_model="TYTHON")
            await client.connect()
            await client.log_out()
            await client.disconnect()
            what_need_to_do_echo[str(query.message.chat.id)] = ""
            await query.edit_message_text(f"• تم تسجيل الخروج من الحساب : {filename}", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="delecho")],
            ]))
        except:
            os.remove(f"echo_ac/{query.message.chat.id}/{filename}.session")
            await query.edit_message_text(f"• لا يوجد هكذا حساب : {filename}", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("رجوع", callback_data="delecho")],
            ]))
    elif (query.data == "myecho"):
        directory_path = Path(f"echo_ac/{query.message.chat.id}")
        file_list = [file.name for file in directory_path.iterdir(
        ) if file.is_file() and file.name.endswith('.session')]
        file_list = list(set(file_list))
        keyboard = []
        if str(query.message.chat.id) not in running_processes:
            running_processes[str(query.message.chat.id)] = {}
        keyboard.append([InlineKeyboardButton(
            "تشغيل الكل", callback_data="runall"),InlineKeyboardButton(
            "ايقاف الكل", callback_data="stopall")])
        for filename in file_list:
            filename = filename.split(".")[0]
            if str(filename) in running_processes[str(query.message.chat.id)]:
                button = InlineKeyboardButton(
                    f"{filename}", callback_data=f"stop:{filename}")
                button2 = InlineKeyboardButton(
                    f"ايقاف", callback_data=f"stop:{filename}")
            else:
                button = InlineKeyboardButton(
                    f"{filename}", callback_data=f"run:{filename}")
                button2 = InlineKeyboardButton(
                    f"تشغيل", callback_data=f"run:{filename}")
            keyboard.append([button, button2])
        keyboard.append([InlineKeyboardButton(
            "رجوع", callback_data="sudohome")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("• الحسابات المسجلة في البوت :\n\n- اضغط تشغيل لتشغيل الحساب\n- اضغط ايقاف لايقاف الحساب\n\n• لتشغيل وايقاف كل الحسابات من الاوامر التالية : \n\n", reply_markup=reply_markup)
    elif query.data == "runall":
        what_need_to_do_echo[str(query.message.chat.id)] = query.data
        await query.edit_message_text(f"• ارسل معرف البوت المطلوب تجميع النقاط منه : ", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("رجوع", callback_data="sudohome")],
        ]))
    elif query.data == "stopall":
        await query.edit_message_text(f"• تم ايقاف تشغيل جميع الحسابات !", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("رجوع", callback_data="sudohome")],
        ]))
        stop_all_background_tasks(str(query.message.chat.id))
    elif query.data.startswith("run:"):
        what_need_to_do_echo[str(query.message.chat.id)] = query.data
        filename = query.data.split(":")[1]
        await query.edit_message_text(f"• ارسل معرف البوت المطلوب تجميع النقاط منه : \n\n- {filename}", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("رجوع", callback_data="sudohome")],
        ]))
    elif query.data.startswith("stop:"):
        filename = query.data.split(":")[1]
        await query.edit_message_text(f"• تم ايقاف تشغيل الحساب : {filename}", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("رجوع", callback_data="sudohome")],
        ]))
        stop_background_task(filename, query.message.chat.id)


def main() -> None:
    global what_need_to_do_echo
    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, echoMaker))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()