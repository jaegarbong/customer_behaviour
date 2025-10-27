
-- Category–Season Performance
-- Find top 3 `Category–Season` combinations by **average purchase amount**, only for combinations with ≥30 customers.  
-- **Concepts:** multi-column grouping, `HAVING`, `ORDER BY`, `LIMIT`

SELECT category, season,
		COUNT(customer_id) as n_cust,
		ROUND(AVG(purchase_amount_usd),3) as avg_usd
FROM shopping
group by category, season
HAVING COUNT(customer_id) >= 30
ORDER BY avg_usd DESC
LIMIT 3;
