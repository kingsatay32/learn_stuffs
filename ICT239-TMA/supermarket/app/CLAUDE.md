# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Scope

The git repository root is `C:\Users\USER\myGit`, a personal learning workspace containing several unrelated folders (`Flask/`, `CSS/`, `staycation/`, etc.). This file covers only the app under `ICT239-TMA/supermarket/app/`.

That folder started life as a **copy of the Staycation app** (`staycation/app/`) and is being repurposed into a **supermarket / grocery-store app** for the ICT239 TMA. As of now the code is still almost entirely the Staycation hotel-booking app — the pivot has not happened yet. Treat the existing hotel `Package`/`Booking` code as the scaffold to adapt, not as the finished target. Commits in this repo are informal learning checkpoints ("Start learning HTML"); don't expect a clean history or CI.

### Target: supermarket app

The intended direction (see `data.py`) is a grocery store: product catalogue by category, replacing hotel packages; a shopping cart / order flow replacing hotel bookings. When building new features, prefer reshaping the existing MVC pieces (controller → model static helpers → template extending `base.html`) over introducing a new pattern. `data.py` holds the seed catalogue for this domain (see **Seeding data**).

## Project structure

Everything lives in `ICT239-TMA/supermarket/app/`. The layout is a classic Flask MVC split — the app object at the root, then `controllers/` (routes) → `models/` (data) → `templates/` (views), with `assets/` served as static files.

```
app/
├── __init__.py          ← builds the Flask app; exports `app`, `db`, `login_manager`
├── app.py               ← ENTRYPOINT (FLASK_APP): registers blueprints, Jinja filters,
│                          and the /upload, /changeAvatar, /chooseAvatar routes
├── app_noAJax.py        ← alternate entrypoint — non-AJAX avatar flow (teaching variant)
├── start.bat            ← the canonical run command on Windows (see "Running the app")
├── start.sh             ← the bash equivalent
├── requirements.txt     ← pinned deps (Flask 2.2.2, mongoengine, flask-login, flask-wtf)
├── README.md            ← stale upstream readme (the Medium auth-tutorial this was forked from)
├── data.py              ← supermarket seed data (categories + products); still UNWIRED
│
├── controllers/         ← one Flask Blueprint per file  (the "C")
│   ├── auth.py               → /register /login /logout + user_loader
│   ├── packageController.py  → /  /packages  /viewPackageDetail/<hotel_name>
│   ├── bookController.py     → /view /book /manageBooking /updateBooking /deleteBooking
│   │                            (blueprint is named "bookingController")
│   └── dashboard.py          → /trend_chart  (GET page, POST returns aggregated JSON)
│
├── models/              ← mongoengine Documents + static query helpers  (the "M")
│   ├── users.py             User    → Mongo collection `appUsers`
│   ├── package.py           Package → collection `staycation`
│   ├── book.py              Booking → collection `booking` (refs User + Package)
│   └── forms.py             WTForms: RegForm, BookForm
│
├── templates/           ← Jinja2, all extend base.html  (the "V")
│   ├── base.html            sidebar/nav shell; branches on current_user + admin email
│   ├── _render_field.html   macro for rendering a WTForms field
│   ├── packages.html · packageDetail.html · booking.html · userBookings.html
│   ├── login.html · register.html
│   ├── upload.html · changeAvatar.html · changeAvatar_noAJax.html
│   └── trend_chart.html
│
└── assets/              ← served at /static (app.static_folder = 'assets')
    ├── css/custom.css
    ├── js/               trend_chart.js (Chart.js), changeAvatar.js (jQuery AJAX)
    │                     + users.csv / staycation.csv / booking.csv  (upload samples)
    └── img/              avatars, favicon, page images
```

**Request flow:** `flask run` loads `app.py` → imports `app/__init__.py` for the app object → registers the four blueprints → a request hits a `controllers/*` view → the view calls `Model.someStaticMethod()` in `models/*` → renders a `templates/*` file that extends `base.html`.

## Running the app

The app is a Flask + MongoDB (mongoengine) server. It is **not** run with `python app.py` — `app.py` is the `FLASK_APP` entrypoint and relies on `PYTHONPATH` being set to the `app/` directory so that `controllers.*` and `models.*` resolve.

From `ICT239-TMA/supermarket/app/`:

```bat
:: Windows — same as start.bat
start.bat
```

```powershell
# PowerShell (Windows) — equivalent, done by hand
$env:FLASK_APP="app.py"; $env:PYTHONPATH="."; $env:FLASK_DEBUG="1"
flask run --host=0.0.0.0
```

```sh
# bash — equivalent to start.sh
export FLASK_APP=app.py; export PYTHONPATH=.; export FLASK_DEBUG=1
flask run --host=0.0.0.0
```

Prerequisites:
- A MongoDB server on `localhost`. The database name is `staycation` (hardcoded in `app/__init__.py`) — rename it there when the pivot to the supermarket domain happens. There are no migrations.
- `pip install -r requirements.txt` (pinned; Flask 2.2.2, Werkzeug 2.2.2, mongoengine 0.27, flask-mongoengine 1.0). A `venv/` is already present in `app/`.

There are no tests, linters, or build steps configured.

## Seeding data

There is no fixture script. Data is loaded through the running app: log in, then use the **Upload** page (`/upload`, admin only) to POST a CSV with a `datatype` of `Users`, `Package`, or `Booking`. Sample CSVs live in `app/assets/js/` (`users.csv`, `staycation.csv`, `booking.csv`). The parsing logic (column names, hashing, reference resolution) is inline in `app.py`'s `upload()` view.

`data.py` is a standalone Python seed-data module (not imported anywhere yet). It defines two module-level lists scraped from fairprice.com.sg: `categories` (15 supermarket category names) and `products` (~105 dicts with `name`, `category`, `special_price`, `usual_price`, `stock_qty`, `image_url`, `description`). This is the seed catalogue for the intended **supermarket** app — a different domain from the hotel `Package`/`Booking` models. A model, importer, and route still need to be wired to it.

## Architecture

**App object construction.** `app/__init__.py` is the `app` package. Its `create_app()` builds the `Flask` app, configures MongoEngine and Flask-Login, and assigns module-level `app`, `db`, `login_manager`. Everything else imports these with `from app import app, db, login_manager`. `app.py` is a separate file that imports those, registers blueprints, and defines a handful of routes directly (`/upload`, `/changeAvatar`, `/chooseAvatar`, `/base`) plus the `formatdate` / `formatmoney` Jinja filters.

**Blueprints** (`controllers/`), registered in `app.py`:
- `auth` (`auth.py`) — `/register`, `/login`, `/logout`, and the `login_manager.user_loader`.
- `packageController` (`packageController.py`) — `/` and `/packages` list, `/viewPackageDetail/<hotel_name>`.
- `bookingController` (`bookController.py`) — note the blueprint name is `bookingController`, not `bookController`; `url_for` calls use `bookingController.*`. Handles `/view`, `/book`, `/manageBooking`, `/updateBooking`, `/deleteBooking`.
- `dashboard` (`dashboard.py`) — `/trend_chart`; GET renders the page, POST returns JSON aggregated from all bookings for the Chart.js line chart driven by `assets/js/trend_chart.js`.

**Models** (`models/`) are mongoengine `db.Document` classes with hardcoded collection names that differ from the class names:
- `User` → collection `appUsers` (also a Flask-Login `UserMixin`).
- `Package` → collection `staycation`.
- `Booking` → collection `booking`; holds `ReferenceField`s to `User` and `Package`, and a denormalized `total_cost` computed by `calculate_total_cost()` (`duration * unit_cost`).

All data access goes through `@staticmethod` helpers on the model classes (`getUser`, `getPackage`, `getAllBookings`, `createBooking`, `updateBooking`, …); controllers never query `db` directly. `models/forms.py` has the WTForms classes (`RegForm`, `BookForm`).

**Templates & static.** `app.static_folder = 'assets'`, so `url_for('static', filename='css/custom.css')` resolves to `app/assets/css/custom.css`. All pages extend `templates/base.html`, which passes a `panel` string for the header. Bootstrap 4, jQuery, and Font Awesome are loaded from CDNs.

**Authorization is by hardcoded email.** `base.html` shows the admin nav (Dashboard, Upload) only when `current_user.email == "admin@abc.com"`; other authenticated users see Manage Booking / Change Avatar. There is no role field. Most view functions are gated only by `@login_required`, not by an admin check.

**AJAX vs non-AJAX variants exist as teaching material.** `app.py` + `templates/changeAvatar.html` use an AJAX `POST /chooseAvatar` (JSON). `app_noAJax.py` + `templates/changeAvatar_noAJax.html` are the slower `GET /chooseAvatar/<filename>` equivalent. Only one entrypoint is used at a time via `FLASK_APP`.

## Gotchas

- Imports assume the process CWD / `PYTHONPATH` is `app/`. Running from elsewhere breaks `from controllers...` / `from models...`.
- `formatdate` uses the Windows-only `%#d` strftime directive.
- `packageController.new_function_name` (`/new_endpoint`) references an undefined `string.txt` and will 500 — it is incomplete scratch code.
- Names still say "staycation" / "package" / "booking" throughout (collection names, the `staycation` DB, `hotel_name` route params, sample CSVs). When adapting to the supermarket domain, rename deliberately and update `url_for` targets, blueprint names, and template `extends` together.
- The Staycation original still lives at `staycation/app/` in this same repo — don't edit that copy when working on the supermarket app.
