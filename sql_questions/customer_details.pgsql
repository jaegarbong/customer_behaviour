--- Find each customer’s total spend, and average review rating. Return top 20 customers by total spend.

SELECT *
FROM shopping;

SELECT customer_id,
        SUM(purchase_amount_usd) as total_spend,        
        AVG(review_rating) as avg_review_rating
FROM shopping
GROUP BY customer_id 
order by total_spend DESC
LIMIT 20;
