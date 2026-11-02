"""Database layer. Parameterized SQL, ACID transactions and foreign-key constraints."""
from __future__ import annotations

import hashlib
import os
import sqlite3
from pathlib import Path
from uuid import uuid4

import pandas as pd

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / 'bislk.db'
SCHEMA_PATH = ROOT / 'schema.sql'
IMAGE_DIR = ROOT / 'images'


def connect_db():
    con = sqlite3.connect(DB_PATH, timeout=15)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys = ON')
    return con


def init_db():
    with connect_db() as con:
        con.executescript(SCHEMA_PATH.read_text(encoding='utf-8'))


def query(sql, params=()):
    with connect_db() as con:
        return pd.read_sql_query(sql, con, params=params)


def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 200_000)
    return f'pbkdf2_sha256$200000${salt.hex()}${digest.hex()}'


def add_user(name, email, password, phone='', district=''):
    if not name.strip() or '@' not in email or len(password) < 8:
        raise ValueError('Enter a name, valid email and password with at least 8 characters.')
    with connect_db() as con:
        cur = con.execute('INSERT INTO users(full_name,email,password_hash,phone,district) VALUES(?,?,?,?,?)',
                          (name.strip(), email.strip().lower(), hash_password(password), phone.strip() or None, district.strip() or None))
        return cur.lastrowid


def add_business(name, description, address, district, category_ids, phone='', email='', website='', latitude=None, longitude=None):
    if not name.strip() or not address.strip() or not category_ids:
        raise ValueError('Business name, real address and at least one category are required.')
    if (latitude is None) != (longitude is None):
        raise ValueError('Supply both coordinates, or leave both empty.')
    if latitude is not None and not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError('Invalid latitude / longitude.')
    with connect_db() as con:
        cur = con.execute('''INSERT INTO businesses
            (name,description,address,district,phone,email,website,latitude,longitude)
            VALUES (?,?,?,?,?,?,?,?,?)''',
            (name.strip(), description.strip() or None, address.strip(), district,
             phone.strip() or None, email.strip() or None, website.strip() or None, latitude, longitude))
        bid = cur.lastrowid
        con.executemany('INSERT INTO business_categories(business_id,category_id) VALUES (?,?)',
                        [(bid, int(cid)) for cid in category_ids])
        return bid


def add_review(user_id, business_id, rating, comment):
    with connect_db() as con:
        cur = con.execute('INSERT INTO reviews(user_id,business_id,rating,comment) VALUES(?,?,?,?)',
                          (int(user_id), int(business_id), int(rating), comment.strip() or None))
        return cur.lastrowid


def add_photo_bytes(business_id, filename, contents, license_label, author):
    """Store an uploaded image and image provenance. Only caller-approved uploads."""
    ext = Path(filename).suffix.lower()
    if ext not in ('.jpg', '.jpeg', '.png', '.webp'):
        raise ValueError('Only JPG, PNG, or WebP files are allowed.')
    if not contents or len(contents) > 8 * 1024 * 1024:
        raise ValueError('Upload must be 1 byte to 8 MB.')
    from PIL import Image
    from io import BytesIO
    try:
        im = Image.open(BytesIO(contents))
        im.verify()
    except Exception as exc:
        raise ValueError('The uploaded file is not a readable image.') from exc
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f'{uuid4().hex}{ext}'
    saved = IMAGE_DIR / stored_name
    saved.write_bytes(contents)
    try:
        with connect_db() as con:
            cur = con.execute('''INSERT INTO business_images
                (business_id,file_path,caption,image_author,image_license,image_origin)
                VALUES(?,?,?,?,?,'local_upload')''',
                (business_id, f'images/{stored_name}', filename, author.strip(), license_label.strip()))
            return cur.lastrowid
    except Exception:
        saved.unlink(missing_ok=True)
        raise


# Report 1: *sourced public platform rating snapshot*; not the internal reviews table.
REPORT_TOP_RATED = '''
SELECT b.name AS business, b.district, b.public_rating AS public_rating_out_of_5,
       b.public_review_count, b.public_source_name AS platform,
       b.public_source_url AS review_source
FROM businesses b
WHERE b.public_rating IS NOT NULL
  AND (b.public_review_count >= ? OR (? = 0 AND b.public_review_count IS NULL))
ORDER BY b.public_rating DESC, COALESCE(b.public_review_count, 0) DESC, b.name
'''

# Report 2: counts by district x category from a 3-table JOIN.
REPORT_DISTRICT_CATEGORY = '''
SELECT b.district, c.name AS category, COUNT(DISTINCT b.business_id) AS businesses
FROM businesses b
JOIN business_categories bc ON b.business_id = bc.business_id
JOIN categories c ON bc.category_id = c.category_id
GROUP BY b.district, c.category_id, c.name
ORDER BY b.district, businesses DESC, c.name
'''

# Additional report: ratings submitted into this very app (not seeded/impersonated).
REPORT_USER_REVIEWS = '''
SELECT b.name AS business, b.district, COUNT(r.review_id) AS local_reviews,
       ROUND(AVG(r.rating), 2) AS local_average
FROM reviews r
JOIN businesses b ON b.business_id = r.business_id
GROUP BY b.business_id
ORDER BY local_average DESC, local_reviews DESC
'''
