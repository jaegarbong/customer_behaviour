# SQL Practice Questions for Data Science Interviews

This set of 10 SQL problems is designed for **intermediate to advanced** data science interview preparation.  
Dataset: `shopping` (columns include Customer ID, Gender, Age, Category, Purchase Amount (USD), Review Rating, etc.)

---

## 🟢 Moderate Difficulty

### 1. Customer Segmentation
Classify each customer into spending tiers based on `Purchase Amount (USD)` —  
**Low (<50)**, **Medium (50–100)**, **High (>100)** — and compute the count and average `Review Rating` for each tier.  
**Concepts:** `CASE WHEN`, `GROUP BY`

```sql

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
    END

```

---

### 2. Category–Season Performance
Find top 3 `Category–Season` combinations by **average purchase amount**, only for combinations with ≥30 customers.  
**Concepts:** multi-column grouping, `HAVING`, `ORDER BY`, `LIMIT`

```sql
SELECT category, season,
		COUNT(customer_id) as n_cust,
		ROUND(AVG(purchase_amount_usd),3) as avg_usd
FROM shopping
group by category, season
HAVING COUNT(customer_id) >= 30
ORDER BY avg_usd DESC
LIMIT 3;
```

---

### 3. Discount & Promo Overlap
Calculate how many transactions used both `Discount Applied = 'Yes'` and `Promo Code Used = 'Yes'`, and what % they represent of total transactions.  
**Concepts:** conditional aggregation, percentage calculation

```sql
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

```

---

### 4. Shipping Preference by Gender
For each `Gender`, find the most common `Shipping Type`. Return one row per gender.  
**Concepts:** finding mode via `RANK()` or `ROW_NUMBER()`


```sql
-- ### 4. Shipping Preference by Gender
-- For each `Gender`, find the most common `Shipping Type`. Return one row per gender.  
-- **Concepts:** finding mode via `RANK()` or `ROW_NUMBER()`

with gs as (
SELECT gender,
		shipping_type,
		count(*) as n_count
from shopping
GROUP BY gender, shipping_type
ORDER BY 1
),

t_rank as
(

SELECT 	gender, 
		shipping_type,
		RANK() OVER(PARTITION BY gender ORDER BY n_count DESC) as rnk
from gs
)
SELECT * from t_rank where rnk=1;

--- Answer 2 (postgres specific) ----
-- “From all rows that share the same value of gender, keep only the first one according to the ORDER BY clause.”

SELECT DISTINCT ON (gender)
       gender, shipping_type, n_count
FROM (
  SELECT gender, shipping_type, COUNT(*) AS n_count
  FROM shopping
  GROUP BY gender, shipping_type
) t
ORDER BY gender, n_count DESC;
```
---

### 5. Previous Purchases vs. Frequency
Compute average `Previous Purchases` for each `Frequency of Purchases` group and rank them in descending order.  
**Concepts:** `GROUP BY`, window ranking

```sql
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
```
---

## 🔴 Hard Difficulty

### 6. High-Value Customers by Relative Rank
Rank all customers by `Purchase Amount (USD)` descending. Return the top 5% (percentile-based) of spenders, showing their `Customer ID`, `Location`, and `Category`.  
**Concepts:** window ranking, percentile filtering


```sql
--Using PERCENT_RANK
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
```
---

### 7. Outlier Spenders by Category
A customer is an outlier if their purchase exceeds the category’s `(mean + 2×stddev)`. Return all such rows with computed z-score.  
**Concepts:** statistical window functions, filtering

```sql
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
```
---

### 8. Review Consistency
For each `Category`, calculate the difference between its max and min `Review Rating`. Which categories have the smallest variation?  
**Concepts:** aggregation, min–max range

```sql
SELECT category,
        MAX(review_rating) as max_rev,
        MIN(review_rating) as min_rev,
       MAX(review_rating) - MIN(review_rating) AS review_variation
FROM shopping
GROUP BY category
ORDER BY review_variation ASC;
```
---
**Recommended Environment:** DuckDB or PostgreSQL  
**Goal:** Practice beyond basic aggregation — focus on ranking, filtering, and analytical SQL patterns.