from Cryptodome.Cipher import AES
import sqlite3
import os

def dir_exists(direc):
    return os.path.exists(direc) and os.path.isdir(direc)

def file_exists(file):
    return os.path.exists(file) and os.path.isfile(file)

class QuarantineSystem:
    def __init__(self):
        self.db_path = "./config/quarantine"
        self.q_dir = "./config/quarantine_files"

        if not dir_exists("./config"):
            os.mkdir("./config")

        if not dir_exists(self.q_dir):
            os.mkdir(self.q_dir)

        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS quarantine(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT,
                    datapath TEXT,
                    threat TEXT,
                    type TEXT,
                    key TEXT,
                    nonce TEXT,
                    source TEXT
                )
            """)
            con.commit()

    def get_records(self):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT id, path, threat, source FROM quarantine")
            result = cur.fetchall()
            records = []
            for i in result:
                records.append({
                    "id": i[0],
                    "file": i[1],
                    "threat": i[2],
                    "source": i[3]
                })
            return records

    def add_path(self, path, threatname, source="unknown"):
        with open(path, "rb") as f:
            file_content = f.read()

        source = getattr(source, "name", "unknown") if not isinstance(source, str) else source

        __key = os.urandom(16)
        __cipher = AES.new(__key, AES.MODE_CTR)
        rnd = os.urandom(64).hex()
        datapath = os.path.join(self.q_dir, f"{rnd}.quarantine")

        with open(datapath, "wb") as f:
            f.write(__cipher.encrypt(file_content))

        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO quarantine(path, datapath, threat, type, key, nonce, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                path,
                datapath,
                threatname,
                "file",
                __key.hex(),
                __cipher.nonce.hex(),
                source
            ))
            con.commit()

        os.remove(path)

    def restore_id(self, id_):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM quarantine WHERE id = ?", (id_,))
            rows = cur.fetchall()
            if not rows:
                return -1

            for i in rows:
                key = bytes.fromhex(i[5])
                nonce = bytes.fromhex(i[6])
                __cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
                with open(i[2], 'rb') as f:
                    ciphdata = f.read()
                with open(i[1], 'wb') as f:
                    f.write(__cipher.decrypt(ciphdata))
                os.remove(i[2])

            cur.execute("DELETE FROM quarantine WHERE id = ?", (id_,))
            con.commit()

    def remove_id(self, id_):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM quarantine WHERE id = ?", (id_,))
            rows = cur.fetchall()
            if not rows:
                return -1

            for i in rows:
                if file_exists(i[2]):
                    os.remove(i[2])

            cur.execute("DELETE FROM quarantine WHERE id = ?", (id_,))
            con.commit()
