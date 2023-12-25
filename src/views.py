from aiogram.types import InlineKeyboardButton, URLInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

import src.database as db


def get_pagination_keyboard(page: int, total_pages: int, movie_id: int, user_id: int, pref: str = 'pag'):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.row(InlineKeyboardButton(text='🍿 Смотреть', callback_data="watch"))
    if (db.is_in_watch_list(user_id, movie_id)):
        kb_builder.row(InlineKeyboardButton(text='🗂 Удалить из сохраненных', callback_data=f"remove"))
    else:
        kb_builder.row(InlineKeyboardButton(text='🗂 Добавить в сохраненные', callback_data=f"save"))
    kb_builder.row(
        InlineKeyboardButton(text='<<', callback_data=f"{pref}_prev"),
        InlineKeyboardButton(text=f'{page}/{total_pages}', callback_data="tr_curr"),
        InlineKeyboardButton(text='>>', callback_data=f"{pref}_next"),
    )
    return kb_builder.as_markup()

def movie_callback(movie_data: dict):
    print(movie_data)
    if movie_data['poster_path'] is None:
        image_from_url = URLInputFile("https://motivatevalmorgan.com/wp-content/uploads/2016/06/default-movie-1-3.jpg")
    else:
        image_from_url = URLInputFile(f"https://image.tmdb.org/t/p/w600_and_h900_bestv2/{movie_data['poster_path']}")

    if len(movie_data['overview']) > 1024:
        movie_data['overview'] = movie_data['overview'][:movie_data['overview'].rfind('.')]
    else:
        description = f"🎬 {movie_data['title']} ({movie_data['original_title']}) \n\
📅 {movie_data['release_date']} \n\
⭐️ {movie_data['vote_average']} \n\
📝 {movie_data['overview']}"

    return image_from_url, description
