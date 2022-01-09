-- update the existing rows
UPDATE stock_prices p,stock_prices_stage s
SET p.`open_price` = s.`open_price`,
    p.`high_price` = s.`high_price`,
    p.`low_price` = s.`low_price`,
    p.`close_price` = s.`close_price`,
    p.`updated_at`=NOW()
WHERE p.`ticker` = s.`ticker`
  AND p.`as_of_date` = s.`as_of_date`;

-- insert the new rows
INSERT INTO stock_prices (ticker, as_of_date, open_price, high_price, low_price, close_price)
SELECT ticker, as_of_date, open_price, high_price, low_price, close_pric
FROM stock_prices_stage s
WHERE NOT EXISTS
    (SELECT 1 FROM stock prices p
     WHERE p.`ticker` = s.`ticker`
         AND p.`as_of_date` = s.`as_of_date`;
)

-- truncate the stage table
TRUNCATE TABLE stock_prices_stage;