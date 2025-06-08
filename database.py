import inspect
import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "discord.db")


def create_users_per_guild_table():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "users_per_guild" (
            "user_id" INTEGER NOT NULL,
            "guild_id" INTEGER NOT NULL,
            "racism_count" INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY("user_id", "guild_id")
        )
    """)
    con.commit()
    con.close()


def increase_and_get_racism_count(user_id: int, guild_id: int) -> int:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        SELECT racism_count 
        FROM users_per_guild
        WHERE (user_id = ?) AND (guild_id = ?)
    """, (user_id, guild_id))
    racism_count = cur.fetchone()

    if not racism_count:
        cur.execute("""
            INSERT INTO users_per_guild (user_id, guild_id, racism_count)
            VALUES (?, ?, 1)
        """, (user_id, guild_id))
        con.commit()
        con.close()
        return 1

    racism_count = racism_count[0] + 1
    cur.execute("""
        UPDATE users_per_guild
        SET racism_count = ?
        WHERE (user_id = ?) AND (guild_id = ?)
    """, (racism_count, user_id, guild_id))
    con.commit()
    con.close()

    return racism_count


def create_racism_words_table():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "racism_words" (
            "word" TEXT NOT NULL,
            "guild_id" INTEGER NOT NULL,
            "added_by" INTEGER NOT NULL,
            "added_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY("word", "guild_id")
        )
    """)
    con.commit()
    con.close()


def get_racism_words(guild_id: int) -> list[str]:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        SELECT word
        FROM racism_words
        WHERE guild_id = ?
    """, (guild_id,))
    racism_words = [row[0] for row in cur.fetchall()]
    con.close()
    return racism_words


def add_racism_word(word: str, guild_id: int, added_by: int) -> bool:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    flag = True

    try:
        cur.execute("""
            INSERT INTO racism_words (word, guild_id, added_by)
            VALUES (?, ?, ?)
        """, (word, guild_id, added_by))
        con.commit()
    except sqlite3.IntegrityError:
        flag = False
    finally:
        con.close()
        return flag


def remove_racism_word(word: str, guild_id: int) -> bool:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        DELETE FROM racism_words
        WHERE (word = ?) AND (guild_id = ?)
    """, (word, guild_id))

    changes = cur.rowcount  # number of rows affected by the DELETE
    con.commit()
    con.close()

    return changes > 0


def init_database():
    module = sys.modules[__name__]
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("create_"):
            print(f"Initialising DB: Running {name}()")
            func()
