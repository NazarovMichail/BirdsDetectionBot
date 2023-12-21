from config import TOKEN
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from keyboards import kbrd_menu, inline_dove, inline_bluetit, inline_thrush, inline_sparrow, inline_woodpecker, inline_cardinal
from aiogram.contrib.fsm_storage.memory import MemoryStorage


from roboflow import Roboflow
rf = Roboflow(api_key="jyxqZLcJ27mR9wFxBpUJ")
project = rf.workspace().project("birds-detection-fld02")
model = project.version(2).model

bot = Bot(TOKEN)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)

PROJECT_INFO = """
Бот разработан для детекции птиц по фото.
_____________________________________
📸 1. Загрузите фотографию с изображением птиц 
🦅 2. Бот определит птиц на фотографии 
📚 3. Чтобы узнать о птице подробнее 
   нажмите на кнопку "Узнать о ..." 
_____________________________________

В проекте принимали участие:
🤝 <b>Иванов А.А</b>, 
🤝 <b>Петров. П.П</b>,
🤝 <b>Сидоров. П.П</b>...

"""


START_TEXT = """
<b>Загрузите фотографию птиц 🐦‍⬛️</b>
"""


class InputState(StatesGroup):  
# Класс для считывания текущего состояния
    input_state = State()


async def bot_startup(dispatcher):
    print('Bot is running ...')


async def bot_shutup(dispatcher):
    # При выходе пишется сообщение
    print('Bot has gone ...')


# Вывод информации
@dispatcher.message_handler(Text(equals='О проекте'))
async def proj_info(message: types.Message):
    await message.answer(text=f' {PROJECT_INFO} ',
                        parse_mode= "HTML")
    await message.answer(text=f' {CREATORS} ',
                        parse_mode= "HTML")
    await message.delete()

# Вывод клавиатуры меню
@dispatcher.message_handler(commands=['start'])
async def get_keyboard(message: types.Message):
    await message.answer(text=START_TEXT, parse_mode='HTML', reply_markup=kbrd_menu)
    await bot.send_animation(chat_id=message.from_user.id, animation=open('presentation.gif', 'rb'))
    await message.delete()


@dispatcher.message_handler(content_types=['photo'])
async def get_photo(message: types.Message):   
    await message.photo[-1].download('model/file.jpg')
    prediction = model.predict('model/file.jpg', confidence=40, overlap=30).json()
    print(prediction)
    model.predict("model/file.jpg", confidence=40, overlap=30).save("model/prediction.jpg")
    await message.delete()
    await bot.send_photo(chat_id=message.from_user.id, photo=open('model/prediction.jpg', 'rb'))
    class_list = []
    try:
        if prediction['predictions'] == []:
                await message.answer(text="""На изображении нет птиц 🤷... Ведь так? 🫣""")
        for pred in prediction['predictions']:
            if pred['class'] not in class_list:
                if pred['class'] == "pigeon":
                    await bot.send_photo(chat_id=message.from_user.id, photo=open('img/pigeon.jpg', 'rb'), caption='Голубь', reply_markup=inline_dove)
                    class_list.append(pred['class'])
                if pred['class'] == "tit":
                    await bot.send_photo(chat_id=message.from_user.id, photo=open('img/titmouse.jpg', 'rb'), caption='Синица', reply_markup=inline_bluetit)
                    class_list.append(pred['class'])

                if pred['class'] == "thrush":
                    await bot.send_photo(chat_id=message.from_user.id, photo=open('img/thrush.jpg', 'rb'), caption='Дрозд', reply_markup=inline_thrush,)
                    class_list.append(pred['class'])

                if pred['class'] == "sparrow":
                    await bot.send_photo(chat_id=message.from_user.id, photo=open('img/sparrow.jpg', 'rb'), caption='Воробей', reply_markup=inline_sparrow)
                    class_list.append(pred['class'])
                    
                if pred['class'] == "woodpecker":
                    await bot.send_photo(chat_id=message.from_user.id, photo=open('img/woodpckr.jpg', 'rb'), caption='Дятел', reply_markup=inline_woodpecker)
                    class_list.append(pred['class'])

                if pred['class'] == "cardinal":
                    await bot.send_photo(chat_id=message.from_user.id, photo=open('img/cardinal.jpg', 'rb'), caption='Красный кардинал', reply_markup=inline_cardinal)
                    class_list.append(pred['class'])
            
                
    except IndexError:
        await message.answer(text="""На изображении нет птиц 🤷... Ведь так? 🫣""")


if __name__ == '__main__':
    executor.start_polling(dispatcher=dispatcher,
                        on_startup=bot_startup,
                        skip_updates=True,
                        on_shutdown=bot_shutup)