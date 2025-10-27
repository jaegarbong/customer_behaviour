-- ### 3. Discount & Promo Overlap
-- Calculate how many transactions used both `Discount Applied = 'Yes'` and `Promo Code Used = 'Yes'`, and what % they represent of total transactions.  
-- **Concepts:** conditional aggregation, percentage calculation

SELECT discount_applied, promo_code_used,
		COUNT(*)
FROM shopping
WHERE discount_applied = TRUE AND promo_code_used = TRUE
GROUP by discount_applied, promo_code_used;


WITH overlap AS (
    SELECT COUNT(*) AS both_true
    FROM shopping
    WHERE discount_applied = TRUE 
      AND promo_code_used = TRUE
),
total AS (
    SELECT COUNT(*) AS total_rows
    FROM shopping
)
SELECT 
    o.both_true,
    t.total_rows,
    ROUND(100.0 * o.both_true / t.total_rows, 2) AS percent_overlap
FROM overlap o, total t;
