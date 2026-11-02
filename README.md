# BisLK — Real-Location Business Directory DBMS Mini Project

An updated version of the BisLK Case 2 student database project built with **Python + SQLite + Streamlit**. Based on the student's **eight-entity ER model**; *only* new provenance columns were added to two tables. This is a classroom prototype, not a production directory.

## What's inside

- **15 actual businesses:** 5 around Kandy, 5 around Kurunegala, and 5 around Moratuwa.
- Genuine, cited **street/location addresses**; no "Example Road" or invented house numbers.
- **15 attributed published ratings** and paraphrased review themes; public ratings are external provider snapshots as of 2026-11-02, not fictitious individual BisLK reviews.
- **5 real, openly licensed business photographs** from Wikimedia Commons, linked to the correct businesses and stored in the `business_images` table with photographer, license and source metadata. The other 10 businesses intentionally have a **"Photo unavailable"** placeholder until an authorized image is provided.
- A **business-entry form**, **review-entry form**, **user registration**, and **photo upload form**.
- **Two required dynamic reports** and an extra first-party user-review report.
- Database browser, CSV export and source attribution.

## 1. Setup (Windows / VS Code)

Download/extract the entire `BisLK_Project_Updated` folder. **Do not mix files or reuse the old `bislk.db`**, because this version has additional source/license metadata columns and fresh seed records.

Open this *new folder* in VS Code. In VS Code, choose **Terminal → New Terminal**, then enter:

```powershell
python -m pip install -r requirements.txt
python seed.py
python -m streamlit run app.py
```

Open the local URL printed in the terminal (normally `http://localhost:8501`). Stop the app with **Ctrl+C** in the terminal.

**The ZIP already includes `bislk.db` populated with the 15 businesses.** Running `seed.py` is safe, because it avoids duplicate insertions.

## 2. Photos and offline access

Five business photo links point to **Wikimedia Commons thumbnails**, with attribution shown in the application and the original Commons pages in `PHOTO_LICENSES.md`. They require internet to display in the app initially.

**Recommended before the viva**, run on a computer with internet:

```powershell
python cache_images.py
```

This fetches those five Commons thumbnails into `images/` and updates the existing image `file_path` fields, without altering the source credits or license. This optional step is not required to run the app. If a remote host blocks fetching, the program keeps the source URL and doesn't generate a pretend image.

You can use the **Upload business photo** page to add other images, but only with the owner's permission / a verified reuse license. An image is saved as a file and its **path, business foreign key and attribution** are recorded in `business_images`. This is an example of one-to-many relationship.

## 3. Demonstration sequence (for the viva)

1. On **Discover businesses**, filter to **Kurunegala** or **Moratuwa**, then filter by category.
2. Open **Business details** → select **Queen's Hotel Kandy** → show its real photo, credit, location, review summary and source.
3. Open **Database & sources** → inspect `businesses`, `business_categories` and `business_images`.
4. Open **Add business** → enter a *clearly labelled new classroom test business* using an address your group can verify. Save it.
5. Open **Database & sources** → show a new row in `businesses` and link row in `business_categories`.
6. Open **Register user**, or choose one of the three `Demo Reviewer` accounts already present (they are openly identified as demonstration users).
7. Open **Add review** → enter an original review. Inspect `reviews` and the extra BisLK reviews report.
8. Open **Reports** → show the public-rating leaderboard (Report 1) and the businesses-by-location-and-category chart (Report 2). Download CSV files.
9. Optionally upload a photograph you own, then demonstrate that `business_images.business_id` links it to the correct business.

## 4. Key DBMS concepts to explain

| Topic | Where it appears |
|---|---|
| PK | `users.user_id`, `businesses.business_id`, etc. |
| FK | `reviews.user_id` → `users.user_id`; `business_images.business_id` → `businesses.business_id` |
| Many-to-many | `businesses` and `categories` via `business_categories` |
| Composite PK | `(business_id, category_id)` in `business_categories` |
| Normalization | Repeated categories and photographs live in separate tables |
| Constraints | `email UNIQUE`, rating `CHECK`, FK constraints |
| Transactions | `db.add_business()` creates the business and its category links together |
| Database programming | Parameterized `INSERT` methods; `JOIN`, `GROUP BY`, `COUNT`, `AVG` queries |
| Reporting | `REPORT_TOP_RATED`, `REPORT_DISTRICT_CATEGORY`, `REPORT_USER_REVIEWS` |
| Images | `business_images` stores path / credits; uploaded bytes are on disk |

## 5. Important academic integrity notes

- **All 15 business names and locations were checked against public listings**, but addresses and service details can change; source links are embedded in the database and documented in `BUSINESS_SOURCES.csv`.
- Published ratings and review totals are **dated third-party snapshots**. They can fluctuate and they are not the arithmetic average of the locally stored `reviews` table.
- **No third-party review author's identity, review text or individual star ratings are faked**. Public review themes are separately attributed original short paraphrases. New reviews created in the student app are actual rows in `reviews`.
- The initial `reviews` table is intentionally empty. This accurately reflects the absence of real BisLK customers. Three test users are seeded solely for classroom input demonstration.
- Image links do not transfer copyright ownership: comply with the source license and credit authors. `PHOTO_LICENSES.md` contains the original file pages and rights requirements.
- Most businesses have no *precisely verified coordinates*. They therefore have NULL latitude/longitude instead of an invented geocoding. **Map buttons open an exact-name/address search**, and the optional pin map plots only the two verified points.
- The original user-submitted ER diagram does not include the additional provenance fields; see `ER_MODEL_CHANGES.md` for the tiny schema extension.

## 6. Project files

| File | Purpose |
|---|---|
| `app.py` | Streamlit screens, input and reports |
| `db.py` | SQLite connection, parameterized SQL, functions, report queries |
| `schema.sql` | Eight relational tables plus integrity constraints |
| `seed.py` | 15 sourced businesses and five Commons image records |
| `bislk.db` | Ready-populated SQLite database |
| `cache_images.py` | Optional locally cache credited Commons images for offline presentation |
| `BUSINESS_SOURCES.csv` | Exact public review / address source for each listing |
| `PHOTO_LICENSES.md` | Photo authors, licenses, links and attribution |
| `report_queries.sql` | SQL for the required reports |
| `tests/test_project.py` | Small verification script |

## 7. Reset if needed

You can reset *only this updated classroom database* to the original 15 businesses by stopping the app, making a backup of `bislk.db`, then deleting `bislk.db` in **the updated folder** and running `python seed.py`. All user-entered changes will be lost if you do this. Photos uploaded by the app stay on disk unless removed manually.

Use `python tests/test_project.py` for simple sanity checks.
