-- Compute average and median Purchase Amount (USD) by Category and Gender.

SELECT * from shopping;

SELECT category, gender,
		ROUND(AVG(purchase_amount_usd),2),
		PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY purchase_amount_usd) as median_amt
		
FROM shopping
GROUP BY category, gender;