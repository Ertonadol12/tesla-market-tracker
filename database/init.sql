-- Tesla Market Tracker Database Schema

-- Listings table
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source VARCHAR(50),
    brand VARCHAR(50),
    model VARCHAR(100),
    year INTEGER,
    trim VARCHAR(100),
    price INTEGER,
    mileage INTEGER,
    exterior_color VARCHAR(50),
    interior_color VARCHAR(50),
    options TEXT,
    location_city VARCHAR(100),
    location_state VARCHAR(2),
    listing_url VARCHAR(500),
    listing_date DATE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    price_per_mile FLOAT
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_brand ON listings(brand);
CREATE INDEX IF NOT EXISTS idx_model ON listings(model);
CREATE INDEX IF NOT EXISTS idx_year ON listings(year);
CREATE INDEX IF NOT EXISTS idx_price ON listings(price);
CREATE INDEX IF NOT EXISTS idx_mileage ON listings(mileage);
CREATE INDEX IF NOT EXISTS idx_scraped_at ON listings(scraped_at);

-- Daily snapshots table
CREATE TABLE IF NOT EXISTS daily_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand VARCHAR(50),
    model VARCHAR(100),
    year INTEGER,
    avg_price FLOAT,
    min_price INTEGER,
    max_price INTEGER,
    avg_mileage FLOAT,
    listing_count INTEGER,
    snapshot_date DATE UNIQUE
);