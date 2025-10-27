-- ### 5. Previous Purchases vs. Frequency
-- Compute average `Previous Purchases` for each `Frequency of Purchases` group and rank them in descending order.  
-- **Concepts:** `GROUP BY`, window ranking

WITH freq_purch as 
(
SELECT 	frequency_of_purchases,
		COUNT(customer_id) as n_cust,
		ROUND(AVG(previous_purchases),3) as avg_last_purch	
from shopping
GROUP BY frequency_of_purchases
)

SELECT 	*, 
		RANK() OVER(ORDER BY avg_last_purch DESC) as rnk
from freq_purch
