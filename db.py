import sqlite3

DB = "bot.db"


def conn():
    return sqlite3.connect(DB)


def init_db():
    c = conn()
    cur = c.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        telegram_id INTEGER PRIMARY KEY,
        name TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS shifts(
        day TEXT,
        telegram_id INTEGER,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT,
        requester_id INTEGER,
        requester_name TEXT,
        role TEXT,
        status TEXT,
        accepted_by INTEGER
    )
    """)

    c.commit()
    c.close()


def set_user(uid, name, role):
    c = conn()
    cur = c.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO users VALUES(?,?,?)",
        (uid, name, role),
    )
    c.commit()
    c.close()


def add_request(day, uid, name, role):
    c = conn()
    cur = c.cursor()

    cur.execute(
        """
        INSERT INTO requests(
            day, requester_id, requester_name, role,
            status, accepted_by
        )
        VALUES(?,?,?,?,?,?)
        """,
        (day, uid, name, role, "pending", None),
    )

    req_id = cur.lastrowid
    c.commit()
    c.close()
    return req_id


def accept_request(req_id, accepter_id):
    c = conn()
    cur = c.cursor()

    cur.execute(
        """
        UPDATE requests
        SET status='accepted',
            accepted_by=?
        WHERE id=?
        """,
        (accepter_id, req_id),
    )

    c.commit()
    c.close()


def get_pending(req_id):
    c = conn()
    cur = c.cursor()

    cur.execute("""
        SELECT day, requester_name, role, status
        FROM requests
        WHERE id=?
    """, (req_id,))

    row = cur.fetchone()
    c.close()
    return row


def get_schedule():
    c = conn()
    cur = c.cursor()

    cur.execute("""
        SELECT day, telegram_id, role
        FROM shifts
        ORDER BY day
    """)

    rows = cur.fetchall()
    c.close()
    return rows
