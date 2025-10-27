-- Customer segmentation:
-- Classify each customer into spending tiers based on Purchase Amount (USD) —
-- Low (<50), Medium (50–100), High (>100) 
-- and compute count and average Review Rating for each tier.
-- (Tests: CASE WHEN, GROUP BY)

-- SELECT * from shopping;

WITH t_tier as 
(
SELECT *,
		CASE WHEN(s.purchase_amount_usd) < 50 THEN 'Low'
			WHEN(s.purchase_amount_usd) BETWEEN 50 AND 100 THEN 'Medium'
			WHEN(s.purchase_amount_usd) > 100 THEN 'High'			
		END  as tier				
FROM shopping s

)
SELECT t.tier,
		COUNT(*) AS customer_count,
		AVG(t.purchase_amount_usd) as avg_usd,
		AVG(t.review_rating) as avg_review
from t_tier as t
group by t.tier
ORDER BY 
    CASE tier 
        WHEN 'Low' THEN 1 
        WHEN 'Medium' THEN 2 
        WHEN 'High' THEN 3 
    END;
