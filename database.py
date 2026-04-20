"""
database.py — База данных Джарвиса.
  • SQLite  — по умолчанию (без зависимостей, работает везде)
  • PostgreSQL — если задан DATABASE_URL

Все настройки берутся из config.py.
"""
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

from config import DATABASE_URL, SQLITE_PATH, SESSION_DAYS, ADMIN_USERNAME

_DB_URL = DATABASE_URL
USE_PG  = bool(_DB_URL)

if USE_PG:
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        raise ImportError(
            "psycopg2 не установлен.\n"
            "Установи: pip install psycopg2-binary\n"
            "Или убери DATABASE_URL чтобы использовать SQLite."
        )

# ──────────────────────────────────────────────────────────────
#  Соединения
# ──────────────────────────────────────────────────────────────

def _pg_conn():
    return psycopg2.connect(_DB_URL, sslmode="require")

def _sq_conn():
    conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # лучше для concurrent reads
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def get_conn():
    return _pg_conn() if USE_PG else _sq_conn()

def _ph(sql: str) -> str:
    """Заменяет %s на ? для SQLite."""
    return sql if USE_PG else sql.replace("%s", "?")

def _rows(cur) -> list:
    return [dict(r) for r in cur.fetchall()]

def _one(cur) -> Optional[dict]:
    row = cur.fetchone()
    return dict(row) if row else None

# ──────────────────────────────────────────────────────────────
#  Схема БД
# ──────────────────────────────────────────────────────────────

_SCHEMA_SQ = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt          TEXT NOT NULL,
    is_admin      INTEGER DEFAULT 0,
    created_at    TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS sessions (
    token      TEXT PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
    expires_at TEXT NOT NULL,
    is_guest   INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role       TEXT NOT NULL,
    content    TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

_SCHEMA_PG = """
CREATE TABLE IF NOT EXISTS users (
    id           SERIAL PRIMARY KEY,
    username     VARCHAR(120) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt         TEXT NOT NULL,
    is_admin     BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS sessions (
    token      CHAR(128) PRIMARY KEY,
    user_id    INT REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ NOT NULL,
    is_guest   BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS messages (
    id         SERIAL PRIMARY KEY,
    user_id    INT REFERENCES users(id) ON DELETE CASCADE,
    role       VARCHAR(16) NOT NULL,
    content    TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

def _ensure_schema():
    try:
        conn = get_conn()
        if USE_PG:
            with conn.cursor() as cur:
                for stmt in _SCHEMA_PG.strip().split(";"):
                    if stmt.strip():
                        cur.execute(stmt)
            conn.commit()
        else:
            conn.executescript(_SCHEMA_SQ)
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Ошибка инициализации схемы: {e}")

_ensure_schema()

# ──────────────────────────────────────────────────────────────
#  Пароли
# ──────────────────────────────────────────────────────────────

def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((salt + password).encode()).hexdigest()

# ──────────────────────────────────────────────────────────────
#  Пользователи
# ──────────────────────────────────────────────────────────────

def register_user(username: str, password: str) -> tuple[bool, str]:
    uname = username.strip().lower()
    if uname == ADMIN_USERNAME:
        return False, "reserved"
    salt    = secrets.token_hex(32)
    pw_hash = hash_password(password, salt)
    try:
        conn = get_conn()
        conn.execute(
            _ph("INSERT INTO users (username, password_hash, salt, is_admin) VALUES (%s,%s,%s,%s)"),
            (uname, pw_hash, salt, 0),
        )
        conn.commit()
        conn.close()
        return True, "ok"
    except Exception as e:
        err = str(e).lower()
        if "unique" in err:
            return False, "exists"
        return False, str(e)

def register_admin(username: str, password: str) -> tuple[bool, str]:
    uname   = username.strip().lower()
    salt    = secrets.token_hex(32)
    pw_hash = hash_password(password, salt)
    try:
        conn = get_conn()
        if USE_PG:
            with conn.cursor() as cur:
                cur.execute(
                    _ph(
                        "INSERT INTO users (username,password_hash,salt,is_admin) VALUES (%s,%s,%s,TRUE)"
                        " ON CONFLICT (username) DO UPDATE SET password_hash=%s,salt=%s,is_admin=TRUE"
                    ),
                    (uname, pw_hash, salt, pw_hash, salt),
                )
            conn.commit()
        else:
            row = conn.execute(_ph("SELECT id FROM users WHERE username=%s"), (uname,)).fetchone()
            if row:
                conn.execute(
                    _ph("UPDATE users SET password_hash=%s,salt=%s,is_admin=1 WHERE username=%s"),
                    (pw_hash, salt, uname),
                )
            else:
                conn.execute(
                    _ph("INSERT INTO users (username,password_hash,salt,is_admin) VALUES (%s,%s,%s,1)"),
                    (uname, pw_hash, salt),
                )
            conn.commit()
        conn.close()
        return True, "ok"
    except Exception as e:
        return False, str(e)

def login_user(username: str, password: str) -> tuple[bool, Optional[int], bool]:
    try:
        conn = get_conn()
        if USE_PG:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    _ph("SELECT id,password_hash,salt,is_admin FROM users WHERE username=%s"),
                    (username.strip().lower(),),
                )
                row = _one(cur)
        else:
            cur = conn.execute(
                _ph("SELECT id,password_hash,salt,is_admin FROM users WHERE username=%s"),
                (username.strip().lower(),),
            )
            row = _one(cur)
        conn.close()
        if not row:
            return False, None, False
        if hash_password(password, row["salt"]) == row["password_hash"]:
            return True, row["id"], bool(row["is_admin"])
        return False, None, False
    except Exception:
        return False, None, False

def get_all_users() -> list:
    try:
        conn = get_conn()
        if USE_PG:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT id,username,is_admin,created_at FROM users ORDER BY created_at DESC LIMIT 100"
                )
                rows = _rows(cur)
        else:
            cur  = conn.execute(
                "SELECT id,username,is_admin,created_at FROM users ORDER BY created_at DESC LIMIT 100"
            )
            rows = _rows(cur)
        conn.close()
        return rows
    except Exception:
        return []

def set_admin_flag(user_id: int, flag: bool):
    try:
        conn = get_conn()
        val  = flag if USE_PG else int(flag)
        conn.execute(_ph("UPDATE users SET is_admin=%s WHERE id=%s"), (val, user_id))
        conn.commit()
        conn.close()
    except Exception:
        pass

# ──────────────────────────────────────────────────────────────
#  Сессии
# ──────────────────────────────────────────────────────────────

def create_session(user_id: int, is_guest: bool = False) -> str:
    token   = secrets.token_hex(64)
    expires = (datetime.utcnow() + timedelta(days=SESSION_DAYS)).isoformat()
    try:
        conn = get_conn()
        if not is_guest:
            conn.execute(
                _ph("DELETE FROM sessions WHERE user_id=%s AND is_guest=%s"),
                (user_id, False if USE_PG else 0),
            )
        conn.execute(
            _ph("INSERT INTO sessions (token,user_id,expires_at,is_guest) VALUES (%s,%s,%s,%s)"),
            (token, user_id, expires, False if USE_PG else 0),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass
    return token

def validate_session(token: str) -> tuple[Optional[int], Optional[str], Optional[bool]]:
    if not token:
        return None, None, None
    now = datetime.utcnow().isoformat()
    try:
        conn = get_conn()
        if USE_PG:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """SELECT u.id,u.username,u.is_admin
                       FROM sessions s JOIN users u ON u.id=s.user_id
                       WHERE s.token=%s AND s.expires_at>NOW() AND s.is_guest=FALSE""",
                    (token,),
                )
                row = _one(cur)
        else:
            cur = conn.execute(
                _ph("""SELECT u.id,u.username,u.is_admin
                       FROM sessions s JOIN users u ON u.id=s.user_id
                       WHERE s.token=%s AND s.expires_at>%s AND s.is_guest=0"""),
                (token, now),
            )
            row = _one(cur)
        conn.close()
        if row:
            return row["id"], row["username"], bool(row["is_admin"])
        return None, None, None
    except Exception:
        return None, None, None

def delete_session(token: str):
    try:
        conn = get_conn()
        conn.execute(_ph("DELETE FROM sessions WHERE token=%s"), (token,))
        conn.commit()
        conn.close()
    except Exception:
        pass

def cleanup_expired_sessions():
    now = datetime.utcnow().isoformat()
    try:
        conn = get_conn()
        if USE_PG:
            conn.execute("DELETE FROM sessions WHERE expires_at < NOW() - INTERVAL '1 day'")
        else:
            conn.execute(_ph("DELETE FROM sessions WHERE expires_at<%s"), (now,))
        conn.commit()
        conn.close()
    except Exception:
        pass

# ──────────────────────────────────────────────────────────────
#  Сообщения
# ──────────────────────────────────────────────────────────────

def load_messages(user_id: int) -> list:
    try:
        conn = get_conn()
        if USE_PG:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    _ph("SELECT role,content FROM messages WHERE user_id=%s ORDER BY created_at"),
                    (user_id,),
                )
                rows = _rows(cur)
        else:
            cur  = conn.execute(
                _ph("SELECT role,content FROM messages WHERE user_id=%s ORDER BY created_at"),
                (user_id,),
            )
            rows = _rows(cur)
        conn.close()
        return [{"role": r["role"], "content": r["content"]} for r in rows]
    except Exception:
        return []

def save_message(user_id: int, role: str, content: str):
    try:
        conn = get_conn()
        conn.execute(
            _ph("INSERT INTO messages (user_id,role,content) VALUES (%s,%s,%s)"),
            (user_id, role, content),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def clear_history(user_id: int):
    try:
        conn = get_conn()
        conn.execute(_ph("DELETE FROM messages WHERE user_id=%s"), (user_id,))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_admin_stats() -> dict:
    now = datetime.utcnow().isoformat()
    try:
        conn = get_conn()
        if USE_PG:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT COUNT(*) AS c FROM messages")
                msgs = _one(cur)["c"]
                cur.execute("SELECT COUNT(*) AS c FROM users")
                users = _one(cur)["c"]
                cur.execute(
                    "SELECT COUNT(*) AS c FROM sessions WHERE expires_at>NOW() AND is_guest=FALSE"
                )
                active = _one(cur)["c"]
        else:
            msgs   = dict(conn.execute("SELECT COUNT(*) AS c FROM messages").fetchone())["c"]
            users  = dict(conn.execute("SELECT COUNT(*) AS c FROM users").fetchone())["c"]
            active = dict(conn.execute(
                _ph("SELECT COUNT(*) AS c FROM sessions WHERE expires_at>%s AND is_guest=0"),
                (now,),
            ).fetchone())["c"]
        conn.close()
        return {"messages": msgs, "users": users, "active_sessions": active}
    except Exception:
        return {"messages": 0, "users": 0, "active_sessions": 0}
