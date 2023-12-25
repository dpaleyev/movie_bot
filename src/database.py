import sqlite3

conn = sqlite3.connect('database.db')

def setup():
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS "queries" (
                "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                "user_id"	INTEGER NOT NULL,
                "query"	TEXT NOT NULL,
                "date"	TEXT NOT NULL
                )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS "show_stat" (
                "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                "user_id"	INTEGER NOT NULL,
                "title"	TEST NOT NULL,
                "date"	TEXT NOT NULL
                )""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS "watch_list" (
                "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                "user_id"	INTEGER NOT NULL,
                "user_name"	TEXT NOT NULL,
                "movie_id"	TEXT NOT NULL,
                "date"	TEXT NOT NULL
                )""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS "files" (
                "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                "file_id"	TEXT NOT NULL,
                "title"	TEXT NOT NULL
                )""")
    
    conn.commit()

def add_query(user_id, query, date):
    cur = conn.cursor()
    cur.execute(f"""INSERT INTO queries (user_id, query, date) VALUES ({user_id}, '{query}', '{date}')""")
    conn.commit()

def get_queries(user_id):
    cur = conn.cursor()
    cur.execute(f"""SELECT query FROM queries WHERE user_id = {user_id} ORDER BY date""")
    return [i[0] for i in cur.fetchall()]

def add_show_stat(user_id, title, date):
    cur = conn.cursor()
    cur.execute(f"""INSERT INTO show_stat (user_id, title, date) VALUES ({user_id}, '{title}', '{date}')""")
    conn.commit()

def get_show_stat(user_id):
    cur = conn.cursor()
    cur.execute(f"""SELECT title, COUNT(*) FROM show_stat WHERE user_id = {user_id} GROUP BY title""")
    return cur.fetchall()

def add_to_watch_list(user_id, user_name, movie_id, date):
    cur = conn.cursor()
    cur.execute(f"""INSERT INTO watch_list (user_id, user_name, movie_id, date) VALUES ({user_id}, '{user_name}', '{movie_id}', '{date}')""")
    conn.commit()

def remove_from_watch_list(user_id, movie_id):
    cur = conn.cursor()
    cur.execute(f"""DELETE FROM watch_list WHERE user_id = {user_id} AND movie_id = '{movie_id}'""")
    conn.commit()

def is_in_watch_list(user_id, movie_id):
    cur = conn.cursor()
    cur.execute(f"""SELECT movie_id FROM watch_list WHERE user_id = {user_id} AND movie_id = '{movie_id}'""")
    return cur.fetchone() is not None

def get_watch_list(user_id):
    cur = conn.cursor()
    cur.execute(f"""SELECT movie_id FROM watch_list WHERE user_id = {user_id}""")
    return [i[0] for i in cur.fetchall()]

def get_mutual_watch_list(user_id, friend_user_name):
    cur = conn.cursor()
    cur.execute(f"""SELECT movie_id FROM watch_list WHERE user_id = {user_id} AND movie_id IN (SELECT movie_id FROM watch_list WHERE user_name = '{friend_user_name}')""")
    return [i[0] for i in cur.fetchall()]

def add_file(file_id, title):
    cur = conn.cursor()
    cur.execute(f"""INSERT INTO files (file_id, title) VALUES ('{file_id}', '{title}')""")
    conn.commit()

def get_file(file_id):
    cur = conn.cursor()
    cur.execute(f"""SELECT title FROM files WHERE file_id = '{file_id}'""")
    return cur.fetchone()[0] if cur.fetchone() else ""
