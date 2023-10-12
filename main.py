import time, random, json, threading
import pymysql
from flask import Flask, request, redirect

with open("config.json", "r") as fb:
    config = json.loads(fb.read())
    DB = config["DB"]
    KEYS = config["KEYS"]
    LISTEN = config["LISTEN"]
    DEBUG = config["DEBUG"]

app = Flask("Ghink Short Link Service")
db = pymysql.connect(
    host=DB["host"],
    user=DB["user"],
    password=DB["password"],
    database=DB["database"]
)

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
    '9': 60, '0': 61}


@app.route("/", methods=["GET"])
def index():
    with open("index.html", "r", encoding="utf-8") as fb:
        return fb.read()


@app.route("/<string:link_id>", methods=["GET"])
def route(link_id: str):
    global db
    for char in link_id:
        if char not in tuple(field_map.keys()):
            return redirect("https://www.ghink.net")
    link_id_converted = 0
    for i in range(len(link_id)):
        link_id_converted += field_map[link_id[::-1][i]] * 62 ** i

    try:
        db.ping()
    except pymysql.err.InterfaceError:
        db = pymysql.connect(
            host=DB["host"],
            user=DB["user"],
            password=DB["password"],
            database=DB["database"]
        )

    cursor = db.cursor()
    cursor.execute('SELECT link, validity FROM links WHERE id=%s', link_id_converted)
    db.commit()
    link = cursor.fetchone()
    if link is None or link[0] is None:
        with open("404.html", "r", encoding="utf-8") as fb:
            return fb.read(), 404
    if link[1] is not None and link[1] < time.time():
        remove_thread = threading.Thread(target=remove_link, args=(link_id_converted,))
        remove_thread.start()
        with open("404.html", "r", encoding="utf-8") as fb:
            return fb.read(), 404
    return redirect(link[0])


@app.route("/", methods=["POST"])
def add():
    global db
    key = request.form.get("key")
    link = request.form.get("link")
    validity = request.form.get("validity")
    # Judge whether fields are empty
    if key == "" or link == "":
        return json.dumps({"ok": False, "message": "bad field(s)", "id": ""})
    # No access
    if key not in KEYS:
        return json.dumps({"ok": False, "message": "forbidden", "id": ""})
    # Check validity
    if validity:
        if validity.isdecimal() and int(validity) > time.time():
            validity = int(validity)
        else:
            return json.dumps({"ok": False, "message": "bad field(s)", "id": ""})
    else:
        validity = None

    # Random
    while True:
        link_id_random = ''.join(random.sample(tuple(field_map.keys()), 6))
        link_id_converted = 0
        for i in range(len(link_id_random)):
            link_id_converted += field_map[link_id_random[::-1][i]] * 62 ** i
        # Get Cursor
        try:
            db.ping()
        except pymysql.err.InterfaceError:
            db = pymysql.connect(
                host=DB["host"],
                user=DB["user"],
                password=DB["password"],
                database=DB["database"]
            )
        cursor = db.cursor()
        cursor.execute('SELECT link FROM links WHERE id=%s', link_id_converted)
        db.commit()
        link_selected = cursor.fetchone()
        if link_selected is None:
            break
    # Insert
    cursor.execute("INSERT INTO `links` VALUES (%s, %s, %s)", [link_id_converted, link, validity])
    db.commit()

    return json.dumps({"ok": True, "message": "successful", "id": link_id_random})


@app.route("/", methods=["PATCH"])
def reload():
    global config, DB, KEYS, LISTEN, DEBUG

    with open("config.json", "r") as fb:
        config = json.loads(fb.read())
        DB = config["DB"]
        KEYS = config["KEYS"]
        LISTEN = config["LISTEN"]
        DEBUG = config["DEBUG"]

    return json.dumps({"ok": True, "message": "successful"})


def remove_link(id):
    global db
    # Get Cursor
    try:
        db.ping()
    except pymysql.err.InterfaceError:
        db = pymysql.connect(
            host=DB["host"],
            user=DB["user"],
            password=DB["password"],
            database=DB["database"]
        )
    cursor = db.cursor()
    cursor.execute('DELETE FROM links WHERE id=%s', id)
    db.commit()


if __name__ == "__main__":
    app.run(LISTEN[0], LISTEN[1], DEBUG)
    db.close()
