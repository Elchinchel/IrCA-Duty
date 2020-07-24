from .utils import msg_op
from . import dlp
from animstarter import start_player
import time
from typing import List, Any

animation_names = ('бан', 'цем', 'поддержка', 'помощь', 'под',
'мол', 'дорога', 'дрг', 'секс', 'бб', 'брак', 'удар', 'полиция', 'пнуть',
'свидание', 'вселенная', 'привет', 'пока', 'письмо', 'смерть', 'на',
'пожалуйста', 'накормить', 'пошел', 'бух', 'поцеловать', 'выстрел',
'зарплата', 'зп', 'бомба', 'таймер', 'ф', 'f', 'ъуъ', 'луна')

@dlp.register(*animation_names)
def animations(nd):
    nd[5] = nd.msg['command']
    
    
    if nd[5] == 'ф' or nd[5] == 'f':
        pics = ['🌕🌗🌑🌑🌑🌑🌑🌓🌕','🌕🌗🌑🌑🌑🌑🌑🌕🌕','🌕🌗🌑🌓🌕🌕🌕🌕🌕',
        '🌕🌗🌑🌓🌕🌕🌕🌕🌕','🌕🌗🌑🌑🌑🌑🌓🌕🌕','🌕🌗🌑🌑🌑🌑🌕🌕🌕',
        '🌕🌗🌑🌓🌕🌕🌕🌕🌕','🌕🌗🌑🌓🌕🌕🌕🌕🌕','🌕🌗🌑🌓🌕🌕🌕🌕🌕']
        start_player(nd[3], nd[1], nd.db.access_token, pics, 1, False)
        return "ok"


    if nd[5] == 'луна':
        pics = ['🌑🌒🌓🌔🌕🌖🌗🌘']
        start_player(nd[3], nd[1], nd.db.access_token, pics, 1, False)
        return "ok"


    if nd[5] == 'ъуъ':
        pics = [
        '🌘🌑🌕🌕🌘🌑🌒🌕🌕🌕',
        '🌑🌕🌕🌘🌑🌑🌑🌓🌕🌕','🌘🌔🌖🌑👁🌑👁🌓🌗🌒','🌖🌓🌗🌑🌑🌑🌑🌔🌕🌑',
        '🌕🌗🌑🌑🌑🌑🌒🌕🌘🌒','🌕🌕🌘🌑🌑🌑🌑🌑🌒🌕','🌕🌕🌘🌑🌑🌑🌔🌕🌕🌕',
        '🌕🌕🌘🌔🌘🌑🌕🌕🌕🌕','🌕🌖🌒🌕🌗🌒🌕🌕🌕🌕','🌕🌗🌓🌕🌗🌓🌕🌕🌕🌕']
        start_player(nd[3], nd[1], nd.db.access_token, pics, 1, False)
        return "ok"

    pic = 0

    if nd[5] == 'бан':
        pic = ["😒    😈","😒⚠    😈","😒 ⚠   😈","😒  ⚠  😈","😒   ⚠ 😈","😏 👿"]


    if nd[5] == 'цем':
        pic = ['😚 ❤ ᅠᅠᅠᅠᅠ 😔 ','😚 ᅠ ❤ ᅠᅠᅠᅠ 😔 ','😚 ᅠᅠ ❤ ᅠᅠᅠ 😔 ','😚 ᅠᅠᅠ ❤ ᅠᅠ 😔 ',
        '😚 ᅠᅠᅠᅠ ❤ ᅠ 😔 ','😚 ᅠᅠᅠᅠᅠᅠ ❤ 😔 ','😚 ᅠᅠᅠᅠᅠᅠ ☺ ','😊 ☺ ']


    if nd[5] in {'поддержка', 'помощь', 'под'}:
        pic = ["😉     😔 ","😉👍    😔 ","😉 👍   😔 ",
        "😉  👍  😔 ","😉   👍 😔 ","😉    👍😨 ","😉👍😊"]


    if nd[5] == 'мол':
        pic = ["😍     😔 ","😍 ❤   😔 ","😍  ❤  😔 ","😍   ❤ 😳 ","😍    ❤😍 ","😘🤗",]


    if nd[5] == 'дорога' or nd[5] == 'дрг':
        pic = ["🛤\n🛤\n🛤\n🛤\n🛤","🚆\n🛤\n🛤\n🛤\n🛤","🛤\n🚆\n🛤\n🛤\n🛤",
        "🛤\n🛤\n🚆\n🛤\n🛤","🛤\n🛤\n🛤\n🚆\n🛤","🛤\n🛤\n🛤\n🛤\n🚆","🛤\n🛤\n🛤\n🛤\n🛤"]


    if nd[5] == 'бб':
        pic = ["😔      😆","😢      😆","😕      😂",
        "🙂👉   😮","🙂👉🔥😣","😂     😵"]


    if nd[5] == 'секс':
        pic = ["😶     😶","😍     😍","😍👉   👌😍","😍 👉 👌 😍",
        "😍  👉👌 😍","😍 👉 👌 😍","🤤     🤤"]


    if nd[5] == 'брак':
        pic = ["🙋   🏃","💁💕  🚶","🙎  🎁🙇","🙎🎁  🙇","🙆💍 🎁🙇",
        " 💕💏💕","💕 💑 💕","👫   ⛪","👫  ⛪","👫 ⛪","👫💒"]


    if nd[5] == 'удар':
        pic = ["😔     🤣","😤     😂","😡🤜    🤣",
        "😡 🤜   😂","😡  🤜  🤣","😡   🤜 🤣","😡    🤜😣","😌     😵"]


    if nd[5] == 'полиция':
        pic = ["     🚓","    🚓","   🚓","  🚓"," 🚓","🚓",]


    if nd[5] == 'пнуть':
        pic = ["😑👟     🤔","😑 👟    🤔","😑  👟   🤔","😑   👟  🤔","😑    👟 🤔","😏     👟🤕"]


    if nd[5] == 'свидание':
        pic = ["💃    🕺"," 💃  🕺 ","  💃🕺  ","  👫 🌇","   👫🌇","   💑🌇","   💏🌇"]


    if nd[5] == 'вселенная':
        pic = ["🌑✨✨🌏✨✨✨","✨🌑✨🌍✨✨✨","✨✨🌑🌎✨✨✨",
        "✨✨✨🌏🌕✨✨","✨✨✨🌍✨🌕✨","✨✨✨🌎✨✨🌕"]


    if nd[5] == 'привет':
        pic = ["😄🖐","😄👋","😄🖐","😄👋","😄🖐","😄👋"]


    if nd[5] == 'пока':
        pic = ["😁🖐 ","😐👋 ","😕🖐 ","😔👋 ","😔✋ ","😔👋 ","😔✋"]


    if nd[5] == 'письмо':
        pic = ["😊💬         😔","😊  💬       😔","😊    💬     😔",
        "😊      💬   😔","😊         💬😔","😊         😃"]


    if nd[5] == 'смерть':
        pic = ["🙁     😎","😤     😎","😡🔪    😎",
        "😡 🔪   😯","😡  🔪  😧","😡   🔪 😧","😡    🔪😩","😁     😵"]


    if nd[5] == 'на':
        if nd.msg['args']:
            if nd.msg['args'][0] == 'попей':
                pic = ["🙂      🙂","😦      🙂","😯      🙂","😗💦     🙂","😗 💦    🙂",
                "😗  💦   🤔","😗   💦  😳","😁    💦 😦","😂     💦😪","😈      😵"]


    if nd[5] == 'пожалуйста':
        pic = ["🤓     🤔","🤓    🚶","🤓   🚶","🤓  😦","🤓 🚶","🤓🤔","🗣😏","🤝"]


    if nd[5] == 'накормить':
        pic = ["🤔     😒","🤔🍔    😒","😊 🍔   😒","😊  🍔  😲","😊   🍔 😲","😁    🍔🤤","😌🍔😋"]


    if nd[5] == 'пошел':
        if nd.msg['args']:
            if nd.msg['args'][0] == 'нахуй':
                pic = ["😔      🤣","😡    🤣","😡 🖕    🤣","😏     😢","🤣     😭"]


    if nd[5] == 'бух':
        pic = ["😋    🍾", "😄   🍾","😁  🍾","🤤 🍾","🤢","🤮"]


    if nd[5] == 'поцеловать':
        pic = ["😺     🙄","😺    🙄","😺   🙄","😺  🙄","😺 🙄","😺🙄","😽😍"]



    if nd[5] == 'выстрел':
        pic = ["😏 😣","😂 🔫😡","😨 • 🔫😡","😵💥 🔫😡"]



    if nd[5] == 'зарплата' or nd[5] == 'зп':
        pic = ["😔     🙋‍♂", "😔     💁‍♂💵","😔    💵💁‍♂","😔   💵💁‍♂",
        "😔  💵💁‍♂","😔 💵💁‍♂", "😔💵💁‍♂", "😔💵🙋‍♂", "😦💵","😁💵" ]



    if nd[5] == 'бомба':
        pic = ['😠        😝','😡        😝','😡👉💣     😝','😡 👉💣   😝','😡  👉💣   😝',
        '😡   👉💣  😝','😡    👉💣 😝','😡     👉💣😝','😌     👉💣💀']



    if nd[5] == 'таймер':
        pic = ['🔟','9️⃣','8️⃣','7️⃣','6️⃣','5️⃣','4️⃣','3️⃣','2️⃣','1️⃣','✅ Время вышло ✅',]


    if pic:
        start_player(nd[3], nd[1], nd.db.access_token, pic, 1, True)

    return "ok"