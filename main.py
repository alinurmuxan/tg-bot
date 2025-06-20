import telebot
import json
import time
import random

bot = telebot.TeleBot("8048575381:AAGwGWnkXmORreShYOROy4HpLC9qj4SKQUs")

LOG_CHAT_ID = -4775652491  # Тек логтар сақталатын топтың ID

permissions_file = "permissions.json"
helpers_file = "helpers.json"
last_ask_file = "ask.json"

# Тек рұқсат етілгендер ғана командаларды қолдана алсын
def only_allowed(func):
    def wrapper(msg):
        username = f"@{msg.from_user.username}"
        perms = load_json(permissions_file)
        if username not in perms:
            return  # ❌ Жауап бермейді
        return func(msg)
    return wrapper

# JSON функциялар
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        # /givehelper
@bot.message_handler(commands=['givehelper'])
@only_allowed
def give_helper(msg):
    try:
        _, username, nick = msg.text.split()
        perms = load_json(permissions_file)
        helpers = load_json(helpers_file)

        perms[username] = {"role": "helper", "nick": nick}
        helpers[nick] = {
            "role": "Хелпер",
            "vk": "",
            "days": 0,
            "warns": "0/2",
            "strikes": 0,
            "points": 0,
            "afk": 0,
            "asks": 0
        }

        save_json(permissions_file, perms)
        save_json(helpers_file, helpers)
        bot.reply_to(msg, f"✅ {username} теперь helper с ником {nick}")
    except:
        bot.reply_to(msg, "❗ Пример: /givehelper @user Nick_Name")
      
@bot.message_handler(commands=['getid'])
def get_id(msg):
    bot.reply_to(msg, f"🆔 Chat ID: `{msg.chat.id}`", parse_mode="Markdown")

# /giveadmin
@bot.message_handler(commands=['giveadmin'])
@only_allowed
def give_admin(msg):
    try:
        _, username, nick = msg.text.split()
        perms = load_json(permissions_file)
        helpers = load_json(helpers_file)

        perms[username] = {"role": "admin", "nick": nick}
        helpers[nick] = {
            "role": "Старший Хелпер",
            "vk": "",
            "days": 0,
            "warns": "0/2",
            "strikes": 0,
            "points": 0,
            "afk": 0,
            "asks": 0
        }

        save_json(permissions_file, perms)
        save_json(helpers_file, helpers)
        bot.reply_to(msg, f"✅ {username} теперь admin с ником {nick}")
    except:
        bot.reply_to(msg, "❗ Пример: /giveadmin @user Nick_Name")

# /remove
@bot.message_handler(commands=['remove'])
@only_allowed
def remove_person(msg):
    try:
        _, target = msg.text.split()
        perms = load_json(permissions_file)
        helpers = load_json(helpers_file)

        # Удаление по username
        if target in perms:
            nick = perms[target]["nick"]
            perms.pop(target, None)
            helpers.pop(nick, None)
            text = f"❌ {target} снят и его статистика удалена"
        # Удаление по нику
        elif target in helpers:
            for u in list(perms):
                if perms[u]["nick"] == target:
                    perms.pop(u, None)
            helpers.pop(target, None)
            text = f"❌ {target} снят и удалён"
        else:
            text = "❗ Пользователь не найден."

        save_json(permissions_file, perms)
        save_json(helpers_file, helpers)
        bot.reply_to(msg, text)

    except Exception as e:
        bot.reply_to(msg, f"⚠ Ошибка: {e}")

# /form
@bot.message_handler(commands=['form'])
@only_allowed
def form_helper(msg):
    try:
        parts = msg.text.split()
        if len(parts) < 4:
            return bot.reply_to(msg, "❗ Пример: /form Nick_Name Роль VK")

        nick = parts[1]
        vk = parts[-1]
        role = ' '.join(parts[2:-1])  # Қалған бөліктер роль болады

        helpers = load_json(helpers_file)
        helpers[nick] = {
            "role": role,
            "vk": vk,
            "days": 0,
            "warns": "0/2",
            "strikes": 0,
            "points": 0,
            "afk": 0,
            "asks": 0
        }
        save_json(helpers_file, helpers)
        bot.reply_to(msg, f"✅ {nick} добавлен в helperlist с ролью: {role} и VK: {vk}")
    except:
        bot.reply_to(msg, "❗ Пример: /form Nick_Name Роль VK")
        # /edit
@bot.message_handler(commands=['edit'])
@only_allowed
def edit_stat(msg):
    try:
        args = msg.text.split(maxsplit=3)
        if len(args) != 4:
            return bot.reply_to(msg, "❗ Пример: /edit Nick_Name параметр значение")

        nick, param, value = args[1], args[2], args[3]
        username = f"@{msg.from_user.username}"
        perms = load_json(permissions_file)

        if username not in perms or perms[username]['role'] != 'admin':
            return bot.reply_to(msg, "🚫 Только админы могут изменять данные.")

        helpers = load_json(helpers_file)
        if nick not in helpers:
            return bot.reply_to(msg, f"❌ Хелпер {nick} не найден.")

        if param not in helpers[nick]:
            return bot.reply_to(msg, f"❗ Неверный параметр.")

        if param in ['days', 'strikes', 'points', 'afk', 'asks']:
            value = int(value)

        helpers[nick][param] = value
        save_json(helpers_file, helpers)
        bot.reply_to(msg, f"✅ У {nick} параметр {param} обновлён на {value}")
    except Exception as e:
        bot.reply_to(msg, f"⚠ Ошибка: {e}")

# /search
@bot.message_handler(commands=['search'])
@only_allowed
def search_info(msg):
    args = msg.text.split()
    username = f"@{msg.from_user.username}"
    perms = load_json(permissions_file)
    helpers = load_json(helpers_file)

    if username not in perms:
        return

    role = perms[username]['role']
    mynick = perms[username]['nick']
    nick = mynick if len(args) == 1 else args[1]

    if nick not in helpers:
        return bot.reply_to(msg, f"❌ Nick {nick} не найден.")
    if len(args) > 1 and role != "admin":
        return bot.reply_to(msg, "❌ Только админы могут смотреть чужие данные.")

    h = helpers[nick]
    text = (
        f"👤 NickName: {nick}\n"
        f"🏢 Должность: {h['role']}\n"
        f"📅 Дней в должности: {h['days']}\n"
        f"⚠️ Предупреждения: {h['warns']}\n"
        f"❗️ Выговоры: {h['strikes']}\n"
        f"⭐️ Баллы: {h['points']}\n"
        f"💤 Неактивы: {h['afk']}\n"
        f"⁉️ Сделано асков: {h.get('asks', 0)}"
    )
    bot.reply_to(msg, text)

# /helperlist
@bot.message_handler(commands=['helperlist'])
@only_allowed
def helper_list(msg):
    helpers = load_json(helpers_file)
    if not helpers:
        return bot.reply_to(msg, "❌ Список пуст.")

    def get_priority(data):
        first = data["role"].strip().upper()[0]
        return {
            "Г": 0,
            "З": 1,
            "С": 2,
            "Х": 3
        }.get(first, 4)

    sorted_helpers = sorted(helpers.items(), key=lambda x: get_priority(x[1]))

    text = "📜 <b>Список хелперов:</b>\n\n"
    for nick, data in sorted_helpers:
        role = data['role']
        vk = data['vk'].strip()

        # Если ссылка пустая — ставим прочерк
        if vk == "":
            link = "—"
        else:
            link = f'<a href="{vk}">VK</a>'

        text += f"👤 <b>{nick}</b>\n🏢 {role}\n🔗 {link}\n\n"

    bot.send_message(msg.chat.id, text, parse_mode="HTML", disable_web_page_preview=True)

# /myaccess
@bot.message_handler(commands=['myaccess'])
@only_allowed
def my_access(msg):
    username = f"@{msg.from_user.username}"
    perms = load_json(permissions_file)
    if username in perms:
        bot.reply_to(msg, f"🔑 Ваш доступ: {perms[username]['role']}")
    else:
        bot.reply_to(msg, "❗ У вас нет доступа.")

import json
import random
import time
import difflib  # для сравнения текстов

last_ask_file = "ask.json"  # уже используем для таймера

# Загружаем вопросы
with open("ask.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# Для сохранения времени ответа
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Команда /ask
@bot.message_handler(commands=['ask'])
@only_allowed
def ask_question(msg):
    username = f"@{msg.from_user.username}"
    perms = load_json("permissions.json")

    if username not in perms:
        return bot.reply_to(msg, "❌ У вас нет доступа.")

    last = load_json(last_ask_file)
    now = time.time()

    if username in last and now - last[username] < 3600:
        mins = int((3600 - (now - last[username])) // 60)
        return bot.reply_to(msg, f"⏳ Подожди ещё {mins} мин перед следующим вопросом.")

    q = random.choice(list(questions))
    correct = questions[q]
    last[username] = now
    save_json(last_ask_file, last)

    bot.send_message(msg.chat.id, f"{q}\n\n💬 Напиши ответ сюда:")

    # Ожидаем ответ
    @bot.message_handler(func=lambda m: m.chat.id == msg.chat.id and m.from_user.username == msg.from_user.username)
    def check_answer(answer_msg):
        user_ans = answer_msg.text.lower().strip()
        correct_ans = correct.lower().strip()

        similarity = difflib.SequenceMatcher(None, user_ans, correct_ans).ratio()

        if similarity >= 0.6:
            bot.reply_to(answer_msg, "✅ Правильно!")
        else:
            bot.reply_to(answer_msg, f"❌ Неправильно.\nПравильный ответ: {correct}")
            # /start, /help, /scores
@bot.message_handler(commands=['start', 'help', 'scores'])
@only_allowed
def base_cmds(msg):
    username = f"@{msg.from_user.username}"
    perms = load_json(permissions_file)
    role = perms[username]['role'] if username in perms else None

    if msg.text == '/start':
        return bot.reply_to(msg, "👋 Привет! Я бот помощник проекта Black Russia.")

    if msg.text == '/help':
        if role == 'admin':
            help_text = (
                "🛠 Команды для админов:\n"
                "/givehelper @username Nick_Name — дать доступ хелпера\n"
                "/giveadmin @username Nick_Name — дать доступ админа\n"
                "/remove @username или Nick_Name — удалить доступ и статистику\n"
                "/form Nick_Name Роль VK — добавить в helperlist\n"
                "/edit Nick_Name параметр значение — изменить статистику\n"
                "/search Nick_Name — посмотреть чужую статистику\n"
                "/helperlist — список всех хелперов\n"
                "/ask — задать случайный вопрос хелперу\n"
                "/myaccess — узнать свой доступ\n"
                "/scores — счёт (в разработке)"
            )
        elif role == 'helper':
            help_text = (
                "🛠 Команды для хелперов:\n"
                "/search — посмотреть свою статистику\n"
                "/ask — получить вопрос\n"
                "/helperlist — список хелперов\n"
                "/myaccess — узнать свой доступ"
            )
        else:
            help_text = "❗ У вас нет доступа к использованию команд."

        bot.reply_to(msg, help_text)

    elif msg.text == '/scores':
        bot.reply_to(msg, "🏆 Подсчёт баллов пока в разработке.")

# 🔁 Пересылка личных сообщений админу
import re  # регулярка кириллица үшін

ADMIN_ID = 6197668362  # Сенің Telegram ID

@bot.message_handler(func=lambda msg: True, content_types=['text'])
def monitor_all(msg):
    username = f"@{msg.from_user.username}"
    perms = load_json(permissions_file)
    text = msg.text.strip()

    # Только личка
    if msg.chat.type != "private":
        return

    # Роль пользователя
    role = perms[username]["role"] if username in perms else None

    # 1. Сообщения без прав (неизвестные пользователи)
    if username not in perms:
        if re.search(r'[А-Яа-яЁё]', text):  # если кириллица
            bot.send_message(ADMIN_ID, f"👤 Неизвестный: {username}\n✉️ Написал (кириллица):\n{text}")
        elif not text.startswith("/"):
            bot.send_message(ADMIN_ID, f"👤 Неизвестный: {username}\n✉️ Написал:\n{text}")
        return

    # 2. Хелпер/админ — пишет некоманду
    if not text.startswith("/"):
        bot.send_message(ADMIN_ID, f"👤 {role.upper()} {username}\n✉️ Написал:\n{text}")
        return

    # 3. Пишет команду, которая ему не доступна
    if text.startswith("/giveadmin") or text.startswith("/edit") or text.startswith("/remove"):
        if role != "admin":
            bot.send_message(ADMIN_ID, f"🚫 Команда недоступна!\n👤 {username} пытался: {text}")
            return

    # 4. Проверка на русские слова
    if re.search(r'[А-Яа-яЁё]', text):
        bot.send_message(ADMIN_ID, f"🇷🇺 Русский текст от {username}:\n{text}")
        

# /addask командасы
@bot.message_handler(commands=['addask'])
@only_allowed
def add_ask(msg):
    username = f"@{msg.from_user.username}"
    perms = load_json("permissions.json")

    # Тек админ ғана қоса алады
    if username not in perms or perms[username]["role"] != "admin":
        return bot.reply_to(msg, "❌ Тек админдерге ғана рұқсат.")

    if "::" not in msg.text:
        return bot.reply_to(msg, "❗ Формат: /addask Вопрос :: Ответ")

    try:
        parts = msg.text.replace("/addask", "", 1).strip().split("::")
        question = parts[0].strip()
        answer = parts[1].strip()

        questions = load_json("ask.json")
        questions[question] = answer
        save_json("ask.json", questions)

        bot.reply_to(msg, "✅ Сұрақ сәтті қосылды!")
    except Exception as e:
        bot.reply_to(msg, f"⚠️ Қате: {e}")
       
@bot.message_handler(func=lambda msg: True, content_types=['text'])
def monitor_all(msg):
    if msg.chat.type != "private":
        return

    username = f"@{msg.from_user.username}"
    text = msg.text.strip()
    perms = load_json(permissions_file)
    role = perms[username]["role"] if username in perms else "❌ NO ACCESS"

    # 1. Егер бұл белгілі команда болса — басқа хендлер өңдейді
    if text.startswith("/") and any(text.startswith(cmd) for cmd in KNOWN_COMMANDS):
        return

    # 2. Егер рұқсатсыз адам болса
    if username not in perms:
        if re.search(r'[А-Яа-яЁё]', text):  # Кириллица бар ма
            bot.send_message(LOG_CHAT_ID, f"👤 Неизвестный: {username}\n✉️ Написал (кириллица):\n{text}")
        elif not text.startswith("/"):
            bot.send_message(LOG_CHAT_ID, f"👤 Неизвестный: {username}\n✉️ Написал:\n{text}")
        return

    # 3. Егер бұл рұқсатты адам жазса, және некоманда болса — логқа
    if not text.startswith("/"):
        bot.send_message(LOG_CHAT_ID, f"📩 {role} {username}\n{text}")
    else:
        # Белгісіз команда болса, логқа
        bot.send_message(LOG_CHAT_ID, f"⚙️ {role} {username} жазды команду:\n{text}")

    # 4. Егер тыйым салынған команданы қолданса — жеке админге
    if text.startswith("/giveadmin") or text.startswith("/edit") or text.startswith("/remove"):
        if role != "admin":
            bot.send_message(ADMIN_ID, f"🚫 Команда недоступна!\n👤 {username} пытался: {text}")
            
@bot.message_handler(commands=['helperlist'])
@only_allowed
def show_helperlist(msg):
    helpers = load_json(helpers_file)
    
    hierarchy = {
        "Главный Следящий за Агентами Поддержки": "👑 Руководство",
        "Заместитель Главного Следящего за Агентами Поддержки": "💎 Заместители",
        "Следящий за Хелперами": "🛡️ Кураторы",
        "Хелпер": "👤 Хелперы"
    }

    sections = {
        "👑 Руководство": [],
        "💎 Заместители": [],
        "🛡️ Кураторы": [],
        "👤 Хелперы": []
    }

    for username, data in helpers.items():
        role = data.get("role", "Хелпер")
        vk = data.get("vk", "—")
        added = False

        for key, section in hierarchy.items():
            if key.lower() in role.lower():
                sections[section].append(f"{hierarchy[key].split()[0]} {username} | {role} | [VK]({vk})")
                added = True
                break
        
        if not added:
            sections["👤 Хелперы"].append(f"👤 {username} | {role} | [VK]({vk})")

    response = ""
    total = 0
    for section_title, people in sections.items():
        if people:
            response += f"\n<b>{section_title}</b>\n"
            for i, person in enumerate(people, start=1):
                response += f"{i}. {person}\n"
                total += 1

    response += f"\n📊 <b>Всего:</b> {total} человек"

    bot.send_message(msg.chat.id, response.strip(), parse_mode="HTML", disable_web_page_preview=True)
        
        # Запуск
print("✅ Бот запущен!")
bot.infinity_polling()
