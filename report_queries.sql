-- REPORT 1: Verified public-rating leaderboard. Snapshot fields copied with citations.
-- Public ratings do NOT come from BisLK's reviews table.
SELECT name AS business, district, public_rating, public_review_count,
       public_source_name AS platform, public_source_url
FROM businesses
WHERE public_rating IS NOT NULL
ORDER BY public_rating DESC, COALESCE(public_review_count,0) DESC;

-- REPORT 2: Registered businesses grouped by district and category.
SELECT b.district, c.name AS category, COUNT(DISTINCT b.business_id) AS business_count
FROM businesses b
JOIN business_categories bc ON bc.business_id=b.business_id
JOIN categories c ON c.category_id=bc.category_id
GROUP BY b.district,c.category_id
ORDER BY b.district, business_count DESC, c.name;

-- EXTRA: First-party reviews entered through BisLK's Add review form.
SELECT b.name, COUNT(*) AS user_reviews, ROUND(AVG(r.rating),2) AS internal_average
FROM reviews r
JOIN businesses b ON b.business_id=r.business_id
GROUP BY b.business_id;

-- Proof of physical photo records and their licensing metadata:
SELECT b.name, i.image_id, i.file_path, i.image_author, i.image_license, i.source_url
FROM business_images i
JOIN businesses b ON b.business_id=i.business_id
ORDER BY b.name;
