QUERIES = dict(
    CREATE_TABLE="""
        CREATE TABLE IF NOT EXISTS ip (
        ip_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT NOT NULL UNIQUE,
        whois TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        update_at TEXT DEFAULT CURRENT_TIMESTAMP)
    """,
    GET_IP="""SELECT * FROM ip WHERE ip=?""",
    INSERT_IP="""INSERT INTO ip(ip, whois) VALUES(?,?)""",
    UPDATE_IP="""UPDATE ip SET whois = ?, update_at = ? WHERE ip=?"""
)
