-- FMP Index Data Table
CREATE TABLE IF NOT EXISTS fmp_index_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price DECIMAL(15, 2),
    change DECIMAL(15, 2),
    volume BIGINT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weather Data Table
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    location_name VARCHAR(100),
    region VARCHAR(100),
    country VARCHAR(100),
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    location_time TIMESTAMP,
    temperature_c DECIMAL(5, 2),    
    wind_kph DECIMAL(5, 2),
    wind_direction VARCHAR(10),
    humidity INTEGER,
    feels_like_c DECIMAL(5, 2),
    uv_index DECIMAL(5, 2),
    last_updated TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CoinMarket Bitcoin Data Table
CREATE TABLE IF NOT EXISTS coinmarket_bitcoin_data (
    id SERIAL PRIMARY KEY,
    price_usd DECIMAL(15, 2),
    percent_change_1h DECIMAL(5, 2),
    percent_change_24h DECIMAL(5, 2),
    last_updated TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Last Sync Table
CREATE TABLE IF NOT EXISTS last_sync (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_fmp_symbol ON fmp_index_data(symbol);
CREATE INDEX IF NOT EXISTS idx_fmp_timestamp ON fmp_index_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_timestamp ON weather_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_coinmarket_timestamp ON coinmarket_bitcoin_data(timestamp); 