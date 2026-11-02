"""Seed 15 verified business listings. Idempotent; *no fabricated third-party reviews*."""
from db import init_db, connect_db, hash_password

CHECKED = '2026-11-02'
CATEGORIES = [
 ('Hotels', 'Accommodation and resorts'),
 ('Restaurants', 'Dine-in and takeaway food businesses'),
 ('Cafés', 'Coffee and casual dining'),
 ('Bakeries', 'Cakes and baked goods'),
 ('Retail', 'Stores, shopping centres and supermarkets'),
]

# Review summaries are ORIGINAL, short paraphrases of public review topics, not copied reviews.
# Address and rating citations deliberately separate where sources differ.
BUSINESSES = [
 dict(name="Queen's Hotel Kandy", district='Kandy', address='No. 4, Dalada Veediya, Kandy 20000, Sri Lanka', cats=['Hotels'],
  desc='Historic colonial-era hotel near Kandy Lake and the Temple of the Tooth.',
  rating=3.7, count=2290, source='Tripadvisor', source_url='https://www.tripadvisor.com/Hotel_Review-g304138-d455946-Reviews-Queen_s_Hotel-Kandy_Kandy_District_Central_Province.html',
  address_source='https://www.booking.com/hotel/lk/queen-s.en-gb.html',
  summary='Reviewers often praise its central sightseeing location and historic character. Some mention dated facilities and traffic noise.',
  lat=7.2932, lon=80.6384, phone='+94 81 223 3026'),
 dict(name='Hotel Suisse Kandy', district='Kandy', address='30 Sangaraja Mawatha, Kandy 20000, Sri Lanka', cats=['Hotels'],
  desc='Lakeside heritage hotel with gardens and a swimming pool.',
  rating=4.0, count=2172, source='Tripadvisor', source_url='https://www.tripadvisor.com/Hotel_Review-g304138-d447508-Reviews-Hotel_Suisse_Kandy_since_1890-Kandy_Kandy_District_Central_Province.html',
  address_source='https://www.tripadvisor.com/Hotel_Review-g304138-d447508-Reviews-Hotel_Suisse_Kandy_since_1890-Kandy_Kandy_District_Central_Province.html',
  summary='Guests frequently highlight the peaceful lake setting, heritage atmosphere and helpful staff; a few note older room fixtures.'),
 dict(name="Earl's Regency Hotel", district='Kandy', address="Earl's Regency, Tennekumbura, Kundasale, Kandy, Sri Lanka", cats=['Hotels'],
  desc='Large resort-style hotel in the Kundasale area near Kandy.',
  rating=4.3, count=3735, source='Tripadvisor', source_url='https://www.tripadvisor.com/Hotel_Review-g1199465-d316956-Reviews-Earls_Regency-Kundasale_Kandy_District_Central_Province.html',
  address_source='https://www.booking.com/hotel/lk/earl-s-regency.html',
  summary='Reviews commonly mention attractive green surroundings, generous buffet choices and supportive staff; some describe aging facilities.'),
 dict(name='Olde Empire Hotel', district='Kandy', address='21 Temple Street, Kandy 20000, Sri Lanka', cats=['Hotels','Cafés'],
  desc='Traditional guesthouse above/near the Empire Café in central Kandy.',
  rating=3.6, count=212, source='Tripadvisor', source_url='https://www.tripadvisor.com/Hotel_Review-g304138-d447513-Reviews-Olde_Empire_Hotel-Kandy_Kandy_District_Central_Province.html',
  address_source='https://www.booking.com/hotel/lk/olde-empire-kandy.en-gb.html',
  summary='Travelers value the temple-side location and old building. Others note that bathrooms and basic room furnishings show their age.',
  lat=7.293658, lon=80.638908),
 dict(name='Amaya Hills Kandy', district='Kandy', address='Heerassagala, Kandy 20000, Sri Lanka', cats=['Hotels'],
  desc='Hillside resort known for panoramic greenery and outdoor recreation.',
  rating=4.3, count=4548, source='Tripadvisor', source_url='https://www.tripadvisor.com/Hotel_Review-g12220047-d480276-Reviews-Amaya_Hills_Kandy-Heerassagala_Kandy_Kandy_District_Central_Province.html',
  address_source='https://www.tripadvisor.com/Hotel_Review-g12220047-d480276-Reviews-Amaya_Hills_Kandy-Heerassagala_Kandy_Kandy_District_Central_Province.html',
  summary='Guests repeatedly mention expansive hillside views, attentive service and comfortable stays. A few report stairs or older rooms.'),
 dict(name='The Epitome Hotel', district='Kurunegala', address='57 Kurunegala–Dambulla Road, Badagamuwa, Kurunegala 60000, Sri Lanka', cats=['Hotels','Restaurants'],
  desc='Upscale hotel and dining venue in Badagamuwa, near Kurunegala.',
  rating=4.8, count=145, source='Tripadvisor', source_url='https://www.tripadvisor.com/Hotel_Review-g21294776-d21294624-Reviews-The_Epitome-Thorayaya_North_Western_Province.html',
  address_source='https://www.google.com.sg/travel/hotels/entity/ChoIqOexo62N46vFARoNL2cvMTFqZ3FzbjlmehAB',
  summary='Recent travelers praise staff, the dining facilities and the comfortable hotel atmosphere. Views vary with room and stay.'),
 dict(name='Kandyan Reach Hotel', district='Kurunegala', address='No. 344–350, Kandy Road, Kurunegala 60000, Sri Lanka', cats=['Hotels','Restaurants'],
  desc='Hotel with restaurant and event facilities near central Kurunegala.',
  rating=4.4, count=260, source='Tripadvisor', source_url='https://www.tripadvisor.com/Hotel_Review-g668534-d2292063-Reviews-Kandyan_Reach_Hotel-Kurunegala_North_Western_Province.html',
  address_source='https://www.booking.com/hotel/lk/kandyan-reach-kurunegala.html',
  summary='Guest comments often appreciate service, food and its convenience for staying in Kurunegala.'),
 dict(name='The Hangout by Ransara', district='Kurunegala', address='136B Colombo Road, Kurunegala 60000, Sri Lanka', cats=['Restaurants','Cafés','Bakeries'],
  desc='Family restaurant, bakery and café on Colombo Road.',
  rating=3.1, count=82, source='Tripadvisor', source_url='https://www.tripadvisor.com/Restaurant_Review-g668534-d7368307-Reviews-The_Hangout_by_Ransara-Kurunegala_North_Western_Province.html',
  address_source='https://www.tripadvisor.com/Restaurant_Review-g668534-d7368307-Reviews-The_Hangout_by_Ransara-Kurunegala_North_Western_Province.html',
  summary='Public reviews describe a broad menu and bakery offerings; feedback on food consistency and customer service is mixed.'),
 dict(name='Cafe Amakie Kurunegala', district='Kurunegala', address='84 Dambulla Road, Yaggapitiya, Kurunegala 60000, Sri Lanka', cats=['Cafés','Restaurants'],
  desc='Coffee shop and casual multi-cuisine café.',
  rating=4.5, count=39, source='Tripadvisor', source_url='https://www.tripadvisor.com/Restaurant_Review-g668534-d25336742-Reviews-Cafe_Amakie_Kurunegala-Kurunegala_North_Western_Province.html',
  address_source='https://www.tripadvisor.com/Restaurant_Review-g668534-d25336742-Reviews-Cafe_Amakie_Kurunegala-Kurunegala_North_Western_Province.html',
  summary='Visitors commonly highlight coffee and a pleasant dining space, while some find prices higher than expected.'),
 dict(name='Saruketha by Oak Ray', district='Kurunegala', address='No. 95, Dambulla Road, 2nd Mile Post, Yaggapitiya, Kurunegala 60000, Sri Lanka', cats=['Restaurants'],
  desc='Sri Lankan and Asian restaurant near Kurunegala.',
  rating=4.8, count=160, source='Tripadvisor', source_url='https://www.tripadvisor.com/Restaurant_Review-g668534-d28141836-Reviews-Saruketha_By_Oak_Ray-Kurunegala_North_Western_Province.html',
  address_source='https://www.tripadvisor.com/Restaurant_Review-g668534-d28141836-Reviews-Saruketha_By_Oak_Ray-Kurunegala_North_Western_Province.html',
  summary='Diners often compliment the leafy atmosphere, diverse local dishes, refreshments and friendly waiting staff.'),
 dict(name='Pizza Hut – Moratuwa', district='Moratuwa', address='491 Galle Road (A2), Rawathawatta, Moratuwa 10400, Sri Lanka', cats=['Restaurants'],
  desc='Pizza Hut branch serving dine-in, takeaway and delivery.',
  rating=4.2, count=11, source='Tripadvisor', source_url='https://www.tripadvisor.com/Restaurant_Review-g1759915-d10070278-Reviews-Pizza_Hut-Moratuwa_Western_Province.html',
  address_source='https://www.srilanka-places.com/places/pizza-hut-moratuwa',
  summary='Tripadvisor reviewers describe the familiar pizza menu and convenient branch; experiences can vary during busy periods.'),
 dict(name='KFC – Moratuwa', district='Moratuwa', address='No. 4 Old Galle Road, Moratuwa 10400, Sri Lanka', cats=['Restaurants'],
  desc='Quick-service chicken restaurant in Moratuwa.',
  rating=3.8, count=1122, source='Google (via Restaurant Guru)', source_url='https://restaurantguru.com/KFC-Moratuwa-Moratuwa',
  address_source='https://restaurantguru.com/KFC-Moratuwa-Moratuwa',
  summary='Review themes include takeaway and delivery convenience. Customer reports about service speed and order accuracy are mixed.'),
 dict(name="Domino's Pizza – Moratuwa", district='Moratuwa', address='473 Galle Road, Rawathawatta, Moratuwa 10400, Sri Lanka', cats=['Restaurants'],
  desc='Pizza delivery and takeaway outlet on Galle Road.',
  rating=3.9, count=1106, source='Google (via Restaurant Guru)', source_url='https://restaurantguru.com/Dominos-Pizza-Moratuwa-Boralesgamuwa',
  address_source='https://www.ubereats.com/lk/store/dominos-pizza-moratuwa/835Sk62mWWyktxToIuY_LQ',
  summary='Visible reviews frequently discuss delivery and takeaway; some complain about communication and delays.'),
 dict(name='The Fab – Rawathawatta Moratuwa', district='Moratuwa', address='635 Galle Road, Rawathawatta, Moratuwa, Sri Lanka', cats=['Bakeries','Cafés'],
  desc='Bakery and snack outlet offering pastries, cakes and prepared meals.',
  rating=4.2, count=1009, source='Google (via Restaurant Guru)', source_url='https://restaurantguru.com/The-Fab-Rawathawatte-Moratuwa-Moratuwa',
  address_source='https://restaurantguru.com/The-Fab-Rawathawatte-Moratuwa-Moratuwa',
  summary='Many reviewers mention cakes, pastries and lunch items; some report inconsistent service at the branch.'),
 dict(name='Cargills Food City – Katubedda', district='Moratuwa', address='241 Galle Road, Katubedda, Moratuwa 10400, Sri Lanka', cats=['Retail'],
  desc='Grocery supermarket located in the Katubedda area.',
  rating=4.2, count=None, source='Google Maps', source_url='https://www.google.com/maps/search/Cargills%2BFood%2BCity%2BMoratuwa%2BSri%2BLanka?hl=en',
  address_source='https://www.google.com/maps/search/Cargills%2BFood%2BCity%2BMoratuwa%2BSri%2BLanka?hl=en',
  summary='The public listing shows a positive aggregate rating. Specific attributed review themes were not independently checked.'),
]

# These images depict the EXACT listed hotels. Nothing is claimed for other businesses.
PHOTOS = {
 "Queen's Hotel Kandy": dict(url="https://thumb.wikimedia.org/wikipedia/commons/thumb/8/81/Queen%27s_Hotel_Kandy_Sri_Lanka.jpg/960px-Queen%27s_Hotel_Kandy_Sri_Lanka.jpg", caption="Historic front of Queen's Hotel, Kandy", author='Kurun', license='Public domain (PD-self)', license_url='https://commons.wikimedia.org/wiki/File:Queen%27s_Hotel_Kandy_Sri_Lanka.jpg', source='https://commons.wikimedia.org/wiki/File:Queen%27s_Hotel_Kandy_Sri_Lanka.jpg'),
 'Hotel Suisse Kandy': dict(url='https://thumb.wikimedia.org/wikipedia/commons/thumb/6/62/Hotel_Suisse_Kandy.jpg/960px-Hotel_Suisse_Kandy.jpg', caption='Hotel Suisse viewed from across Kandy Lake', author='Bernard Gagnon', license='CC BY-SA 3.0', license_url='https://creativecommons.org/licenses/by-sa/3.0/', source='https://commons.wikimedia.org/wiki/File:Hotel_Suisse_Kandy.jpg'),
 "Earl's Regency Hotel": dict(url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Earl%27s_Regency_Hotel-Kandy_Sri_Lanka_I.jpg/960px-Earl%27s_Regency_Hotel-Kandy_Sri_Lanka_I.jpg", caption="Swimming pool at Earl's Regency Hotel", author='MediaJet', license='CC BY-SA 3.0', license_url='https://creativecommons.org/licenses/by-sa/3.0/', source="https://commons.wikimedia.org/wiki/File:Earl%27s_Regency_Hotel-Kandy_Sri_Lanka_I.jpg"),
 'Olde Empire Hotel': dict(url='https://thumb.wikimedia.org/wikipedia/commons/thumb/7/7c/SL_Kandy_asv2020-01_img27_Empire_Hotel.jpg/960px-SL_Kandy_asv2020-01_img27_Empire_Hotel.jpg', caption='Empire Hotel facade in Kandy', author='A.Savin, Wikipedia', license='Free Art License (FAL)', license_url='https://artlibre.org/licence/lal/en/', source='https://commons.wikimedia.org/wiki/File:SL_Kandy_asv2020-01_img27_Empire_Hotel.jpg'),
 'Amaya Hills Kandy': dict(url='https://thumb.wikimedia.org/wikipedia/commons/thumb/5/53/Amaya_Hills.jpg/960px-Amaya_Hills.jpg', caption='Amaya Hills resort pool and hill view', author='vasse nicolas,antoine', license='CC BY 2.0', license_url='https://creativecommons.org/licenses/by/2.0/', source='https://commons.wikimedia.org/wiki/File:Amaya_Hills.jpg'),
}


def seed():
    init_db()
    with connect_db() as con:
        existing = con.execute('SELECT COUNT(*) FROM businesses').fetchone()[0]
        if existing:
            print(f'{existing} business records already exist; keeping your data. No duplicates added.')
            return
        con.executemany('INSERT OR IGNORE INTO categories (name, description) VALUES (?,?)', CATEGORIES)
        cats = {r['name']:r['category_id'] for r in con.execute('SELECT category_id,name FROM categories')}
        for name, email, district in [
          ('Demo Reviewer One','demo1@example.org','Kandy'),
          ('Demo Reviewer Two','demo2@example.org','Kurunegala'),
          ('Demo Reviewer Three','demo3@example.org','Moratuwa')]:
            con.execute('INSERT INTO users(full_name,email,password_hash,district) VALUES(?,?,?,?)',
                        (name,email,hash_password('classroom-demo-only'),district))
        ids={}
        for b in BUSINESSES:
            cur=con.execute('''INSERT INTO businesses(name,description,address,district,phone,
                latitude,longitude,public_rating,public_review_count,public_source_name,
                public_source_url,public_review_summary,public_checked_on,address_source_url)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (b['name'],b['desc'],b['address'],b['district'],b.get('phone'),b.get('lat'),b.get('lon'),
                 b['rating'],b['count'],b['source'],b['source_url'],b['summary'],CHECKED,b['address_source']))
            bid=cur.lastrowid
            ids[b['name']]=bid
            for cat in b['cats']:
                con.execute('INSERT INTO business_categories(business_id,category_id) VALUES (?,?)', (bid,cats[cat]))
            if b['name'] in PHOTOS:
                p=PHOTOS[b['name']]
                con.execute('''INSERT INTO business_images
                    (business_id,file_path,caption,image_author,image_license,license_url,source_url,image_origin)
                    VALUES(?,?,?,?,?,?,?,'wikimedia_commons')''',
                    (bid,p['url'],p['caption'],p['author'],p['license'],p['license_url'],p['source']))
        for cat, field, typ in [('Restaurants','Cuisine','text'),('Hotels','Hotel setting','text'),
                                ('Cafés','Specialty','text'),('Bakeries','Product type','text'),
                                ('Retail','Store type','text')]:
            con.execute('INSERT INTO category_attributes(category_id,attribute_name,data_type) VALUES(?,?,?)',
                        (cats[cat],field,typ))
        attrs={r['attribute_name']:r['attribute_id'] for r in con.execute('SELECT attribute_id, attribute_name FROM category_attributes')}
        # Only values explicitly supported by published listings, no invented facilities.
        details={
          'Saruketha by Oak Ray':('Cuisine','Sri Lankan and Asian'),
          'Cafe Amakie Kurunegala':('Specialty','Coffee and multi-cuisine meals'),
          'KFC – Moratuwa':('Cuisine','Fast food / fried chicken'),
          "Domino's Pizza – Moratuwa":('Cuisine','Pizza'),
          'Cargills Food City – Katubedda':('Store type','Supermarket'),
          'The Fab – Rawathawatta Moratuwa':('Product type','Cakes and pastries'),
          "Queen's Hotel Kandy":('Hotel setting','Heritage city hotel'),
        }
        for name,(attribute,value) in details.items():
            con.execute('INSERT INTO business_attribute_values(business_id,attribute_id,value) VALUES(?,?,?)',
                        (ids[name],attrs[attribute],value))
    print(f'Seeded 15 REAL business listings across 3 locations; {len(PHOTOS)} openly licensed photos.')
    print('Public rating snapshots are source-linked; initial BisLK user reviews = 0.')

if __name__ == '__main__':
    seed()
