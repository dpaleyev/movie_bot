from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext

import src.database as db
from src.request import fetch_movie_list

from handlers.movie import movie_callback, get_pagination_keyboard

router = Router()

@router.message(Command('start'))
async def start(message: Message):
    await message.answer('Привет, я бот для поиска фильмов. Введи название фильма, который хочешь найти.')

@router.message(Command('history'))
async def history(message: Message):
    history = db.get_queries(message.from_user.id)
    if history:
        await message.answer("📖 Последние 20 запросов:\n"+'\n'.join(reversed(history[:20])))
    else:
        await message.answer('📖 История пуста')
        
@router.message(Command('stat'))
async def stat(message: Message):
    stat = db.get_show_stat(message.from_user.id)
    if stat:
        await message.answer("📈 Статистика просмотров:\n"+'\n'.join([f'{title}: {count}' for title, count in sorted(stat, key=lambda x: -x[1])]))
    else:
        await message.answer('📈 Статистика пуста')

@router.message(Command('saved'))
async def watch_list(message: Message, state: FSMContext):
    if len(message.text.split()) == 2: 
        friend = message.text.split()[1]
        watch_list = db.get_mutual_watch_list(message.from_user.id, friend[1:])
        print(watch_list)
    else:
        watch_list = db.get_watch_list(message.from_user.id)

    if not watch_list:
        await message.answer('🗂 Список пуст')
        return
    
    fetch_data = await fetch_movie_list(watch_list[:10])
    print(fetch_data)

    fetch_data_ext = fetch_data + [None for _ in range(len(watch_list) - len(fetch_data))]
    
    user_data = await state.get_data()

    movie_dict = user_data.get('movies', {})
    movie_dict[message.message_id + 1] = fetch_data_ext
    page_dict = user_data.get('pages', {})
    page_dict[message.message_id + 1] = 0
    watch_dict = user_data.get('watch', {})
    watch_dict[message.message_id + 1] = watch_list
    await state.update_data(movies=movie_dict)
    await state.update_data(pages=page_dict)
    await state.update_data(watch=watch_dict)

    image, description = movie_callback(fetch_data[0])
    await message.answer_photo(
        image,
        caption=description,
        reply_markup=get_pagination_keyboard(1, len(fetch_data), fetch_data[0]['id'], message.from_user.id, pref = "sv")
    )

@router.callback_query(F.data.startswith('sv_'))
async def watch_list_pagination(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    movies = data['movies'][callback.message.message_id]
    page = data['pages'][callback.message.message_id]
    watch_list = data['watch'][callback.message.message_id]
    if callback.data == 'sv_prev' and page > 0:
        page -= 1
    elif callback.data == 'sv_next' and page < len(watch_list) - 1:
        page += 1
    pages = data['pages']
    pages[callback.message.message_id] = page

    print(movies)
    if movies[page] is None:
        fetch_data = await fetch_movie_list(watch_list[page:page+10])
        movies[page:page + len(fetch_data)] = fetch_data
    
    movies_cont = data['movies']
    movies_cont[callback.message.message_id] = movies

    if 0 <= page < len(movies):
        image, description = movie_callback(movies[page])

        file = InputMediaPhoto(media=image, caption=description)
        
        await callback.message.edit_media(
            file,
            reply_markup=get_pagination_keyboard(page + 1, len(movies), movies[page]['id'], callback.from_user.id, pref = "sv")
        )
        await state.update_data(page=pages)
        await state.update_data(movies=movies_cont)

        await callback.answer()