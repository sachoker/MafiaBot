import telebot
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, \
    CallbackQuery
from Room import Room

bot = telebot.TeleBot('5199607748:AAHolJJentSfLi0uMP04kIbBHxh8r06Vh-8')
rooms = []


def extract_room_id(text):
    return text.split()[1] if len(text.split()) > 1 else None


@bot.message_handler(commands=['start'])
def choose_role(message: Message):
    room_id = extract_room_id(message.text)

    if room_id:
        for i in rooms:
            if i.id == room_id:
                markup = InlineKeyboardMarkup()
                outbtn = InlineKeyboardButton('Выйти', callback_data=f'out_{room_id}')
                markup.add(outbtn)
                i.add_user(message.chat.id, message.from_user.username)
                bot.send_message(message.chat.id, f'Здравствуйте, вы добавлены в комнату', reply_markup=markup)
    else:
        createbtn = InlineKeyboardButton('Создать комнату', callback_data='create')
        markup = InlineKeyboardMarkup().add(createbtn)
        bot.send_message(message.chat.id, 'Здравствуйте, вы зашли как администратор', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def call_handler(call: CallbackQuery):
    ids = call.message.chat.id
    bot.answer_callback_query(call.id)
    match call.data.split('_')[0]:
        case 'create':
            room = Room(ids, bot)
            rooms.append(room)
            delbtn = InlineKeyboardButton('Удалить комнату', callback_data=f'delete_{room.id}')
            startbtn = InlineKeyboardButton('Раздать карты', callback_data=f'start_{room.id}')
            markup = InlineKeyboardMarkup().add(delbtn, startbtn)
            bot.send_message(ids, f'Комната создана!\nСсылка на комнату:\n{room.get_link()}',
                             reply_markup=markup)
        case 'start':
            idr = call.data.split('_')[1]
            for i in rooms:
                if i.id == idr:
                    i.begin_distribution(ids, call)
                    break
        case 'delete':
            idr = call.data.split('_')[1]
            for i in rooms:
                if i.id == idr:
                    rooms.remove(i)
                    break
            bot.send_message(ids, f'Комната удалена')
        case 'out':
            idr = call.data.split('_')[1]
            for i in rooms:
                if i.id == idr:
                    i.del_user(ids)


bot.infinity_polling()
