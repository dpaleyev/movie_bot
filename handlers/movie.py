from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, URLInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

import src.database as db
from src.request import search, get_pirate_link, get_view_link
from src.views import get_pagination_keyboard, movie_callback


router = Router()

@router.message(F.text)
async def get_movie(message: Message, state: FSMContext):
    fetch_data = await search(message.text)

    if not fetch_data:
        await message.answer('🔍 Ничего не найдено')
        return
    print(fetch_data)

    user_data = await state.get_data()
    movie_dict = user_data.get('movies', {})
    movie_dict[message.message_id + 1] = fetch_data
    page_dict = user_data.get('pages', {})
    page_dict[message.message_id + 1] = 0
    await state.update_data(movies=movie_dict)
    await state.update_data(pages=page_dict)

    image, description = movie_callback(fetch_data[0])
    await message.answer_photo(
        image,
        caption=description,
        reply_markup=get_pagination_keyboard(1, len(fetch_data), fetch_data[0]['id'], message.from_user.id)
    )
    db.add_query(message.from_user.id, message.text, message.date)
    db.add_show_stat(message.from_user.id, fetch_data[0]['title'] + f" ({fetch_data[0]['release_date'].split('-')[0]})", message.date)


@router.callback_query(F.data.startswith('pag_'))
async def pagination(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    movies = data['movies'][callback.message.message_id]
    page = data['pages'][callback.message.message_id]
    if callback.data == 'pag_prev':
        page -= 1
    elif callback.data == 'pag_next':
        page += 1
    pages = data['pages']
    pages[callback.message.message_id] = page

    if 0 <= page < len(movies):
        image, description = movie_callback(movies[page])

        file = InputMediaPhoto(media=image, caption=description)
        
        await callback.message.edit_media(
            file,
            reply_markup=get_pagination_keyboard(page + 1, len(movies), movies[page]['id'], callback.from_user.id)
        )
        await state.update_data(page=pages)
        await callback.answer()
        db.add_show_stat(callback.from_user.id, movies[page]['title'] + f" ({movies[page]['release_date'].split('-')[0]})", callback.message.date)

@router.callback_query(F.data == 'watch')
async def watch(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    movies = data['movies'][callback.message.message_id]
    page = data['pages'][callback.message.message_id]
    
    movie_title = movies[page]['title']

    pirate_link = get_pirate_link(movies[page])
    view_links = get_view_link(movies[page])

    keyboard = InlineKeyboardBuilder()
    for link in view_links:
        keyboard.add(InlineKeyboardButton(text="📺 " + link[0], url=link[1]))
    keyboard.add(InlineKeyboardButton(text="🏴‍☠️ Йо-хо-хо", url=pirate_link.replace("ru", "gg")))
    keyboard.add(InlineKeyboardButton(text="🏴‍☠️ Йо-хо-хо (VPN)", url=pirate_link.replace("kinopoisk", "freekinopoisk")))
    keyboard.adjust(1)
    
    
    await callback.message.answer(f"🍿 Mожно посмотреть здесь:", reply_markup=keyboard.as_markup())

@router.callback_query(F.data.startswith('save'))
async def save(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    movies = data['movies'][callback.message.message_id]
    page = data['pages'][callback.message.message_id]
    
    db.add_to_watch_list(callback.from_user.id, callback.from_user.username, movies[page]['id'], callback.message.date)

    image, description = movie_callback(movies[page])

    file = InputMediaPhoto(media=image, caption=description)
        
    await callback.message.edit_media(
        file,
        reply_markup=get_pagination_keyboard(page + 1, len(movies), movies[page]['id'], callback.from_user.id)
    )

@router.callback_query(F.data.startswith('remove'))
async def remove(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    movies = data['movies'][callback.message.message_id]
    page = data['pages'][callback.message.message_id]
    
    db.remove_from_watch_list(callback.from_user.id, movies[page]['id'])

    image, description = movie_callback(movies[page])

    file = InputMediaPhoto(media=image, caption=description)
        
    await callback.message.edit_media(
        file,
        reply_markup=get_pagination_keyboard(page + 1, len(movies), movies[page]['id'], callback.from_user.id)
    )
