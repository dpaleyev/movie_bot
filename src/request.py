import aiohttp
import requests
import asyncio
import os
from bs4 import BeautifulSoup

async def search(query: str):
    url = f"https://api.themoviedb.org/3/search/movie?query={query}&include_adult=true&language=ru-RU&page=1"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.environ['TMDB_TOKEN']}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            return data['results']


def get_pirate_link(movie_data: dict):
    title = movie_data['title']
    url = "https://www.google.com/search"
    params = {"q": f"kinopoisk {title}"}
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
    }
    soup = BeautifulSoup(
        requests.get(url, params=params, headers=headers).content, "html.parser"
    )
    for link in soup.select("a:has(h3)"):
        if "film" in link["href"]:
            return link["href"]

def get_view_link(movie_data: dict):
    needed_headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
    url = f"https://www.themoviedb.org/movie/{movie_data['id']}/watch"

    response = requests.get(url, headers = needed_headers )
    
    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find(id="ott_offers_window").find_all("a")

    resurces = ["Netflix", "Apple TV", "Disney"]
    added = set()

    result_links = []

    for href in results:
        if href.get("title") is None:
            continue
        for r in resurces:
            if r in href.get("title") and r not in added:
                added.add(r)
                result_links.append([r, href.get("href")])
    
    return result_links

async def fetch_movie(movie_id, session):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=ru-RU"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.environ['TMDB_TOKEN']}"
    }

    async with session.get(url, headers=headers) as response:
        data = await response.json()
        return data

async def fetch_movie_list(movie_list):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_movie(movie_id, session) for movie_id in movie_list]
        return await asyncio.gather(*tasks)