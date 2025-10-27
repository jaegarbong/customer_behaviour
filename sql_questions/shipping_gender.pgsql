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
