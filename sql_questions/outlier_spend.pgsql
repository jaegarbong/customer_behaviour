-- 7. Outlier Spenders by Category
-- A customer is an outlier if their purchase exceeds the category’s (mean + 1×stddev). Return all such rows with computed z-score.
-- Concepts: statistical window functions, filtering


with stats as (
SELECT *,
        AVG(purchase_amount_usd) OVER(PARTITION BY category) as category_avg,
        stddev_pop(purchase_amount_usd) OVER(PARTITION BY category) as category_stddev
FROM shopping
)
SELECT customer_id, category, purchase_amount_usd, category_avg, category_stddev,
       (purchase_amount_usd - category_avg) / NULLIF(category_stddev, 0) as z_score
FROM stats
WHERE (purchase_amount_usd > category_avg + category_stddev)
ORDER by z_score DESC;