-- BisLK Case 2: same eight entities from the submitted ER model.
-- Additional sourcing metadata documents public rating snapshots and photo licenses.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  phone TEXT,
  district TEXT,
  joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS businesses (
  business_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  address TEXT NOT NULL,
  district TEXT NOT NULL,
  phone TEXT,
  email TEXT,
  website TEXT,
  latitude REAL CHECK (latitude BETWEEN -90 AND 90),
  longitude REAL CHECK (longitude BETWEEN -180 AND 180),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- Public review aggregates are metadata; they are NOT entries in reviews.
  public_rating REAL CHECK(public_rating IS NULL OR (public_rating >= 0 AND public_rating <= 5)),
  public_review_count INTEGER CHECK(public_review_count IS NULL OR public_review_count >= 0),
  public_source_name TEXT,
  public_source_url TEXT,
  public_review_summary TEXT,
  public_checked_on TEXT,
  address_source_url TEXT
);

CREATE TABLE IF NOT EXISTS categories (
  category_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  description TEXT
);

-- Actual BisLK user reviews, not imported third-party text.
CREATE TABLE IF NOT EXISTS reviews (
  review_id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  business_id INTEGER NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
  rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
  comment TEXT,
  reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS business_categories (
  business_id INTEGER NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
  category_id INTEGER NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
  PRIMARY KEY (business_id, category_id)
);

-- file_path may be a verified, openly licensed remote photo URL or local upload path.
CREATE TABLE IF NOT EXISTS business_images (
  image_id INTEGER PRIMARY KEY AUTOINCREMENT,
  business_id INTEGER NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
  file_path TEXT NOT NULL,
  caption TEXT,
  uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  image_author TEXT,
  image_license TEXT,
  license_url TEXT,
  source_url TEXT,
  image_origin TEXT NOT NULL DEFAULT 'local_upload' CHECK(image_origin IN ('wikimedia_commons','local_upload'))
);

CREATE TABLE IF NOT EXISTS category_attributes (
  attribute_id INTEGER PRIMARY KEY AUTOINCREMENT,
  category_id INTEGER NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
  attribute_name TEXT NOT NULL,
  data_type TEXT NOT NULL CHECK (data_type IN ('text', 'number', 'boolean')),
  UNIQUE(category_id, attribute_name)
);

CREATE TABLE IF NOT EXISTS business_attribute_values (
  business_id INTEGER NOT NULL REFERENCES businesses(business_id) ON DELETE CASCADE,
  attribute_id INTEGER NOT NULL REFERENCES category_attributes(attribute_id) ON DELETE CASCADE,
  value TEXT NOT NULL,
  PRIMARY KEY (business_id, attribute_id)
);

CREATE INDEX IF NOT EXISTS idx_businesses_district ON businesses(district);
CREATE INDEX IF NOT EXISTS idx_businesses_rating ON businesses(public_rating);
CREATE INDEX IF NOT EXISTS idx_reviews_business ON reviews(business_id);
CREATE INDEX IF NOT EXISTS idx_bc_category ON business_categories(category_id);
CREATE INDEX IF NOT EXISTS idx_images_business ON business_images(business_id);
