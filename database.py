import sqlite3
import os
  
DB_PATH = '../dataset/cognitive_load.db'
  
def init_db():
    '''Create all tables if they do not exist'''
    os.makedirs('../dataset', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Sessions table — one row per student session
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id            TEXT PRIMARY KEY,
        student_id    TEXT,
        date          TEXT,
        difficulty    TEXT,
        nasa_tlx_score REAL,
        load_class    TEXT
    )''')

    # Quiz responses — one row per question answered
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_responses (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id      TEXT,
        question_id     INTEGER,
        response_time   REAL,
        is_correct      INTEGER,
        confidence      INTEGER,
        timestamp       INTEGER
    )''')

    # CV signals from Member 1
    c.execute('''CREATE TABLE IF NOT EXISTS cv_signals (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id  TEXT,
        timestamp   INTEGER,
        blink_rate  REAL,
        gaze        TEXT,
        expression  TEXT
    )''')

    # Behaviour signals from Member 2
    c.execute('''CREATE TABLE IF NOT EXISTS behaviour_signals (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id       TEXT,
        timestamp        INTEGER,
        wpm              REAL,
        backspace_rate   REAL,
        scroll_reversals REAL,
        mouse_idle       REAL
    )''')

    conn.commit()
    conn.close()
    print('Database ready at', DB_PATH)


def save_session(session_id, student_id, difficulty):
    conn = sqlite3.connect(DB_PATH)
    import datetime
    conn.execute(
        'INSERT INTO sessions VALUES (?,?,?,?,?,?)',
        (session_id, student_id, str(datetime.date.today()), difficulty, None, None)
    )
    conn.commit(); conn.close()


def save_quiz_response(session_id, question_id, response_time, is_correct, confidence):
    import time
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'INSERT INTO quiz_responses VALUES (NULL,?,?,?,?,?,?)',
        (session_id, question_id, response_time, int(is_correct), confidence, int(time.time()))
    )
    conn.commit(); conn.close()


def save_nasa_tlx(session_id, scores):
    '''
    scores = dict with keys: mental, physical, temporal,
            performance, effort, frustration (each 0-20)
    '''
    nasa_score = sum(scores.values()) / len(scores) * 5  # scale to 0-100

    if nasa_score <= 33:   load_class = 'LOW'
    elif nasa_score <= 66: load_class = 'MEDIUM'
    else:                  load_class = 'OVERLOADED'

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'UPDATE sessions SET nasa_tlx_score=?, load_class=? WHERE id=?',
        (nasa_score, load_class, session_id)
    )
    conn.commit(); conn.close()
    return nasa_score, load_class


if __name__ == '__main__':
    init_db()
