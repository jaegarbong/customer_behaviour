-- ### 6. High-Value Customers by Relative Rank
-- Rank all customers by `Purchase Amount (USD)` descending. Return the top 5% (percentile-based) of spenders, showing their `Customer ID`, `Location`, and `Category`.  
-- **Concepts:** window ranking, percentile filtering

WITH perc_rnk AS (
  SELECT
      customer_id,      
      purchase_amount_usd,
      PERCENT_RANK() OVER (ORDER BY purchase_amount_usd DESC) AS pct_rank
  FROM shopping
)
SELECT
    customer_id,    
    purchase_amount_usd,
    pct_rank
FROM perc_rnk
WHERE pct_rank >= 0.95
ORDER BY purchase_amount_usd DESC;

---Alternate using ROW NUMBER---
WITH ranked AS (
  SELECT
      customer_id,
      purchase_amount_usd,
      ROW_NUMBER() OVER (ORDER BY purchase_amount_usd DESC) AS rn
  FROM shopping
),
total AS (SELECT COUNT(*) AS n FROM shopping)
SELECT r.*
FROM ranked r, total t
WHERE rn <= 0.05 * t.n
ORDER BY purchase_amount_usd DESC;