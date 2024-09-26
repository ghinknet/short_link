import time
import random
import json

from quart import Quart, request, redirect

import aiomysql
import aiofiles

with open("config.json", "r") as fb:
    config = json.loads(fb.read())
    DB = config["DB"]
    KEYS = config["KEYS"]
    LISTEN = config["LISTEN"]
    DEBUG = config["DEBUG"]

app = Quart("Ghink Short Link Service")
db_pool = None

field_map = {
    'A': 0, 'a': 1, 'B': 2, 'b': 3,
    'C': 4, 'c': 5, 'D': 6, 'd': 7,
    '1': 8, 'E': 9, 'e': 10, 'F': 11,
    'f': 12, 'G': 13, 'g': 14, 'H': 15,
    'h': 16, '2': 17, 'I': 18, 'i': 19,
    'J': 20, 'j': 21, 'K': 22, 'k': 23,
    'L': 24, 'l': 25, '3': 26, 'M': 27,
    'm': 28, 'N': 29, 'n': 30, 'O': 31,
    'o': 32, 'P': 33, 'p': 34, '4': 35,
    'Q': 36, 'q': 37, 'R': 38, 'r': 39,
    'S': 40, 's': 41, 'T': 42, 't': 43,
    '5': 44, 'U': 45, 'u': 46, 'V': 47,
    'v': 48, 'W': 49, 'w': 50, 'X': 51,
    'x': 52, '6': 53, 'Y': 54, 'y': 55,
    'Z': 56, 'z': 57, '7': 58, '8': 59,
    '9': 60, '0': 61
}

async def init_db():
    global db_pool
    db_pool = await aiomysql.create_pool(
        host=DB["host"],
        user=DB["user"],
        password=DB["password"],
        db=DB["database"],
        autocommit=True
    )

@app.before_serving
async def startup():
    await init_db()

@app.after_serving
async def shutdown():
    db_pool.close()
    await db_pool.wait_closed()

@app.route("/", methods=["GET"])
async def index():
    return redirect("https://k76u22n4gd.apifox.cn")

@app.route("/<string:link_id>", methods=["GET"])
async def route(link_id: str):
    for char in link_id:
        if char not in field_map:
            return redirect("https://www.ghink.net")

    link_id_converted = sum(field_map[link_id[::-1][i]] * 62 ** i for i in range(len(link_id)))

    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('SELECT link, validity FROM links WHERE id=%s', (link_id_converted,))
            link = await cursor.fetchone()
    
    if link is None or link[0] is None:
        async with aiofiles.open("404.html", "r", encoding="utf-8") as fb:
            return await fb.read(), 404
    if link[1] is not None and link[1] < time.time():
        await remove_link(link_id_converted)
        async with aiofiles.open("404.html", "r", encoding="utf-8") as fb:
            return await fb.read(), 404
    return redirect(link[0])

@app.route("/", methods=["POST"])
async def add():
    form = await request.form  # Await the form to get the data
    key = form.get("key")  # Access the key
    link = form.get("link")  # Access the link
    validity = form.get("validity")  # Access the validity

    if not key or not link:
        return json.dumps({"ok": False, "message": "bad field(s)", "id": ""})

    if key not in KEYS:
        return json.dumps({"ok": False, "message": "forbidden", "id": ""})

    if validity:
        if validity.isdecimal() and int(validity) > time.time():
            validity = int(validity)
        else:
            return json.dumps({"ok": False, "message": "bad field(s)", "id": ""})
    else:
        validity = None

    while True:
        link_id_random = ''.join(random.sample(field_map.keys(), 6))
        link_id_converted = sum(field_map[link_id_random[::-1][i]] * 62 ** i for i in range(len(link_id_random)))

        async with db_pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT link FROM links WHERE id=%s', (link_id_converted,))
                link_selected = await cursor.fetchone()
                if link_selected is None:
                    break

    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT INTO `links` VALUES (%s, %s, %s)", (link_id_converted, link, validity))

    return json.dumps({"ok": True, "message": "successful", "id": link_id_random})

@app.route("/", methods=["PATCH"])
async def reload():
    global config, DB, KEYS, LISTEN, DEBUG

    with open("config.json", "r") as fb:
        config = json.loads(fb.read())
        DB = config["DB"]
        KEYS = config["KEYS"]
        LISTEN = config["LISTEN"]
        DEBUG = config["DEBUG"]

    return json.dumps({"ok": True, "message": "successful"})

async def remove_link(id):
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute('DELETE FROM links WHERE id=%s', (id,))

if __name__ == "__main__":
    app.run(host=LISTEN[0], port=LISTEN[1], debug=DEBUG)
