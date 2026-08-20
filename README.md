# Commander City Estate Management System

## What this is
Local web app for managing rental, buy/sell, and maintenance records for Commander City properties. Multi-user with login roles (admin, agent, maintenance).

## How to run (on the office computer)

1. Install Python 3.10+ if not already installed.
2. Open terminal in this folder and install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Seed the database (only needed once, or after wiping data):
   ```
   cd backend
   python3 seed.py
   ```
4. Start the server:
   ```
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```
5. On the host machine, open browser to: http://localhost:8000
6. On other office computers/phones (same WiFi), find the host machine's local IP
   (Windows: `ipconfig`, Mac/Linux: `ifconfig`) and open: http://<host-ip>:8000

## Demo logins
- admin / admin123 (full access)
- agent1 / agent123 (rental + sales)
- maint1 / maint123 (maintenance only)

**Change these passwords before real use** — edit backend/seed.py, wipe data/commander_estate.db, re-run seed.py.

## Importing your real Excel data
Once you send the Excel file, I'll write an import script to load your actual
properties, owners, tenants, and sales history into this same database — no
manual re-entry needed.

## What's built
- Property records (house/shop, block, unit, size, status)
- Owners linked to each property
- Rentals — tenant info, lease terms, rent amount
- Buy/Sell — buyer, seller, price, commission, status
- Maintenance — issue log, status, cost
- Dashboard — quick counts across everything
- Full property lookup — search one house, see everything linked to it
- Role-based login (admin / agent / maintenance)

## What's not built yet (next phases)
- Document upload (deeds, NOCs, agreements) — schema exists, UI doesn't yet
- Connection to your existing rent billing Python pipeline
- Editing/deleting existing records (currently add-only)
- Search/filter bar on the properties list
