-- 8. Review Consistency
-- For each `Category`, calculate the difference between its max and min `Review Rating`. Which categories have the smallest variation?  


SELECT category,
        MAX(review_rating) as max_rev,
        MIN(review_rating) as min_rev,
       MAX(review_rating) - MIN(review_rating) AS review_variation
FROM shopping
GROUP BY category
ORDER BY review_variation ASC;