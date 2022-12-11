BEGIN TRANSACTION;
CREATE TABLE courses(id INTEGER PRIMARY KEY, coin_name VARCHAR(10), 
        coin_buy_price FLOAT(15) DEFAULT 0.00, coin_sell_price FLOAT(15) DEFAULT 0.00);
INSERT INTO "courses" VALUES(1,'BTC',0.0,0.0);
INSERT INTO "courses" VALUES(2,'USDT',0.0,0.0);
CREATE TABLE offers(offer_id INTEGER PRIMARY KEY, user_id INTEGER, datetime INTEGER, 
        operation VARCHAR(5), coin INTEGER, quantity DECIMAL(15), price DECIMAL(15), total DECIMAL(15), 
        is_completed VARCHAR(5));
CREATE TABLE supports(support_id INTEGER PRIMARY KEY, user_id INTEGER, text VARCHAR(4000), 
            is_completed VARCHAR(5));
CREATE TABLE users(id INTEGER PRIMARY KEY, user_id INTEGER, nickname VARCHAR(50), 
        name VARCHAR(50), phone VARCHAR(20), reg_date INTEGER);
COMMIT;
