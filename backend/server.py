import os
import json
import sqlite3
import hashlib
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_DIR = "backend/data"
DB_PATH = os.path.join(DB_DIR, "commander_estate_new.db")
PORT = 8080

# Simple password hashing (SHA-256 for no dependencies)
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    is_new = not os.path.exists(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create tables
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT, block TEXT, unit_number TEXT NOT NULL, type TEXT, size TEXT, status TEXT DEFAULT 'vacant'
    );
    CREATE TABLE IF NOT EXISTS owners (
        id INTEGER PRIMARY KEY AUTOINCREMENT, property_id INTEGER, name TEXT NOT NULL, cnic TEXT, contact TEXT, ownership_start TEXT,
        FOREIGN KEY(property_id) REFERENCES properties(id)
    );
    CREATE TABLE IF NOT EXISTS rentals (
        id INTEGER PRIMARY KEY AUTOINCREMENT, property_id INTEGER, tenant_name TEXT NOT NULL, cnic TEXT, contact TEXT, lease_start TEXT, lease_end TEXT, rent_amount REAL, status TEXT DEFAULT 'active',
        FOREIGN KEY(property_id) REFERENCES properties(id)
    );
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT, property_id INTEGER, seller_name TEXT, buyer_name TEXT, buyer_contact TEXT, sale_price REAL, commission REAL, transaction_date TEXT, status TEXT DEFAULT 'pending',
        FOREIGN KEY(property_id) REFERENCES properties(id)
    );
    CREATE TABLE IF NOT EXISTS maintenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT, property_id INTEGER, reported_by TEXT, issue_description TEXT, date_reported TEXT, status TEXT DEFAULT 'open', cost REAL DEFAULT 0,
        FOREIGN KEY(property_id) REFERENCES properties(id)
    );
    """)
    
    if is_new:
        print("Seeding database...")
        c.executemany("INSERT INTO users (name, username, password_hash, role) VALUES (?, ?, ?, ?)", [
            ("Amaan", "admin", hash_pw("admin123"), "admin"),
            ("Bilal Agent", "agent1", hash_pw("agent123"), "agent"),
            ("Farhan Tech", "maint1", hash_pw("maint123"), "maintenance")
        ])
        c.executemany("INSERT INTO properties (block, unit_number, type, size, status) VALUES (?, ?, ?, ?, ?)", [
            ("A", "A-101", "house", "10 Marla", "rented"),
            ("B", "B-205", "shop", "500 sqft", "for_sale"),
            ("C", "C-310", "house", "5 Marla", "vacant")
        ])
        conn.commit()
        # Get property IDs
        c.execute("SELECT id FROM properties ORDER BY id ASC")
        p_ids = [row[0] for row in c.fetchall()]
        
        c.execute("INSERT INTO owners (property_id, name, cnic, contact, ownership_start) VALUES (?, ?, ?, ?, ?)", 
                  (p_ids[0], "Moiz Ur Rehman", "42101-1234567-1", "0300-1234567", "2022-01-15"))
        c.execute("INSERT INTO owners (property_id, name, cnic, contact, ownership_start) VALUES (?, ?, ?, ?, ?)", 
                  (p_ids[1], "Ahmed Khan", "42101-7654321-2", "0321-9876543", "2021-06-01"))
        c.execute("INSERT INTO owners (property_id, name, cnic, contact, ownership_start) VALUES (?, ?, ?, ?, ?)", 
                  (p_ids[2], "Sara Ali", "42101-1122334-3", "0333-4455667", "2023-03-10"))
        
        c.execute("INSERT INTO rentals (property_id, tenant_name, cnic, contact, lease_start, lease_end, rent_amount, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (p_ids[0], "Usman Tariq", "42101-9988776-4", "0345-1122334", "2025-01-01", "2026-12-31", 45000, "active"))
        
        c.execute("INSERT INTO sales (property_id, seller_name, buyer_name, buyer_contact, sale_price, commission, transaction_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (p_ids[1], "Ahmed Khan", "Zainab Fatima", "0311-2233445", 8500000, 170000, "2026-07-01", "pending"))
        
        c.execute("INSERT INTO maintenance (property_id, reported_by, issue_description, date_reported, status, cost) VALUES (?, ?, ?, ?, ?, ?)",
                  (p_ids[0], "Usman Tariq", "Water leakage in bathroom", "2026-07-10", "open", 0))
        
        conn.commit()
    conn.close()

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    return conn

class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="frontend", **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path.startswith('/api/'):
            self.handle_api_get(parsed_path.path)
        else:
            super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path.startswith('/api/'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body) if body else {}
            except:
                data = {}
            self.handle_api_post(parsed_path.path, data)
        else:
            self.send_error(404, "Not Found")

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def handle_api_get(self, path):
        conn = get_db()
        c = conn.cursor()
        
        if path == '/api/dashboard':
            c.execute("SELECT COUNT(*) as c FROM properties")
            total = c.fetchone()['c']
            c.execute("SELECT COUNT(*) as c FROM properties WHERE status='vacant'")
            vacant = c.fetchone()['c']
            c.execute("SELECT COUNT(*) as c FROM properties WHERE status='rented'")
            rented = c.fetchone()['c']
            c.execute("SELECT COUNT(*) as c FROM rentals WHERE status='active'")
            active_leases = c.fetchone()['c']
            c.execute("SELECT COUNT(*) as c FROM maintenance WHERE status='open'")
            open_m = c.fetchone()['c']
            self.send_json({
                "total_properties": total, "vacant": vacant, "rented": rented,
                "active_leases": active_leases, "open_maintenance": open_m
            })
        elif path == '/api/properties':
            c.execute("SELECT * FROM properties")
            self.send_json(c.fetchall())
        elif path == '/api/rentals':
            c.execute("SELECT rentals.*, properties.unit_number FROM rentals JOIN properties ON rentals.property_id = properties.id")
            self.send_json(c.fetchall())
        elif path == '/api/sales':
            c.execute("SELECT sales.*, properties.unit_number FROM sales JOIN properties ON sales.property_id = properties.id")
            self.send_json(c.fetchall())
        elif path == '/api/maintenance':
            c.execute("SELECT maintenance.*, properties.unit_number FROM maintenance JOIN properties ON maintenance.property_id = properties.id")
            self.send_json(c.fetchall())
        else:
            self.send_error(404, "Endpoint not found")
        conn.close()

    def handle_api_post(self, path, data):
        with open("debug.log", "a") as f:
            f.write(f"POST called: {path} with data: {data}\n")
        conn = get_db()
        c = conn.cursor()
        
        if path == '/api/login':
            username = data.get("username", "")
            password = data.get("password", "")
            hashed = hash_pw(password)
            with open("debug.log", "a") as f:
                f.write(f"Login attempt: {username}, {password}, {hashed}\n")
            c.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, hashed))
            user = c.fetchone()
            if user:
                self.send_json({"token": "dummy-token", "role": user['role'], "name": user['name']})
            else:
                self.send_json({"error": "Invalid username or password"}, 401)
        elif path == '/api/properties':
            c.execute("INSERT INTO properties (block, unit_number, type, size, status) VALUES (?, ?, ?, ?, ?)",
                      (data.get('block'), data.get('unit_number'), data.get('type'), data.get('size'), data.get('status', 'vacant')))
            conn.commit()
            self.send_json({"success": True})
        else:
            self.send_error(404, "Endpoint not found")
        conn.close()

if __name__ == "__main__":
    init_db()
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Starting zero-dependency server on http://localhost:{PORT}")
    httpd.serve_forever()
