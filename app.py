"""BisLK business directory — classroom database programming application.
Launch: python -m streamlit run app.py
"""
from __future__ import annotations

import math
import sqlite3
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st

from db import (ROOT, REPORT_DISTRICT_CATEGORY, REPORT_TOP_RATED, REPORT_USER_REVIEWS,
                add_business, add_photo_bytes, add_review, add_user, init_db, query)

st.set_page_config(page_title='BisLK | Discover Sri Lanka', page_icon='🏙️', layout='wide')
init_db()

STYLES = '''<style>
.block-container {padding-top: 1.4rem; max-width: 1400px;}
[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.17); padding: 12px; border-radius: 10px;}
</style>'''
st.markdown(STYLES, unsafe_allow_html=True)


def cats_df():
    return query('SELECT category_id, name FROM categories ORDER BY name')


def get_photos(bid):
    return query('''SELECT image_id, file_path, caption, image_author, image_license,
                    license_url, source_url, image_origin
                    FROM business_images WHERE business_id=? ORDER BY image_id''', [bid])


def show_photo(bid, caption=False):
    photos = get_photos(bid)
    if photos.empty:
        st.image(str(ROOT/'assets'/'photo_unavailable.png'), use_container_width=True)
        st.caption('No verified reusable photo currently available; image upload supported.')
        return
    item = photos.iloc[0]
    path = item['file_path']
    if not path.startswith(('https://','http://')):
        path = str(ROOT / path)
    try:
        st.image(path, use_container_width=True)
    except Exception:
        st.image(str(ROOT/'assets'/'photo_unavailable.png'), use_container_width=True)
        st.caption('The remote image could not load. Open its source link or try again online.')
    if caption:
        st.caption(f"{item['caption'] or 'Business photo'} — {item['image_author'] or 'Uploader'} · {item['image_license'] or 'Rights supplied by uploader'}")
        if pd.notna(item['source_url']) and item['source_url']:
            st.link_button('Photo source and licence', item['source_url'])


def public_rating(b):
    if pd.isna(b['public_rating']):
        return 'Public rating not available'
    count = b.get('public_review_count')
    suffix = f" · {int(count):,} ratings" if pd.notna(count) else ' · count not verified'
    return f"⭐ {float(b['public_rating']):.1f}/5 on {b['public_source_name']}{suffix}"


def map_url(name, address):
    return 'https://www.google.com/maps/search/?api=1&query=' + quote_plus(str(name) + ', ' + str(address))


def top_businesses():
    return query('''SELECT b.*, GROUP_CONCAT(DISTINCT c.name) AS category_list,
                  COUNT(DISTINCT r.review_id) AS bislk_review_count,
                  ROUND(AVG(r.rating), 2) AS bislk_average
                  FROM businesses b
                  LEFT JOIN business_categories bc ON bc.business_id=b.business_id
                  LEFT JOIN categories c ON bc.category_id=c.category_id
                  LEFT JOIN reviews r ON r.business_id=b.business_id
                  GROUP BY b.business_id ORDER BY b.district, b.name''')


st.sidebar.title('🏙️ BisLK')
st.sidebar.caption('Real-world listings | DBMS mini project')
page = st.sidebar.radio('Navigation', [
    'Discover businesses', 'Business details', 'Add business', 'Upload business photo',
    'Add review', 'Register user', 'Reports', 'Database & sources',
])
st.sidebar.divider()
st.sidebar.info('15 verified business locations. Five openly licensed photos. Public ratings are snapshots, not internal BisLK reviews.')
st.sidebar.caption('All data is stored in `bislk.db` in this folder.')

if page == 'Discover businesses':
    st.title('Find local businesses in Sri Lanka')
    st.write('Search real businesses in **Kandy**, **Kurunegala**, and **Moratuwa**.')
    all_b = top_businesses()
    col1, col2, col3 = st.columns([2,1,1])
    term = col1.text_input('Search by name or description', placeholder='Hotel, café, pizza, ...').strip().casefold()
    town = col2.selectbox('Town / district', ['All','Kandy','Kurunegala','Moratuwa'])
    cat = col3.selectbox('Category', ['All'] + cats_df()['name'].tolist())
    df = all_b.copy()
    if term:
        df = df[df[['name','description','address']].fillna('').apply(
            lambda row: any(term in str(value).casefold() for value in row), axis=1)]
    if town != 'All':
        df = df[df.district == town]
    if cat != 'All':
        # Use SQL EXISTS in a parameterized query: don't match partial category text.
        matching_ids = query('''SELECT DISTINCT bc.business_id FROM business_categories bc
                              JOIN categories c ON c.category_id=bc.category_id
                              WHERE c.name=?''', [cat])['business_id'].tolist()
        df = df[df.business_id.isin(matching_ids)]
    a,b,c = st.columns(3)
    a.metric('Matching businesses', len(df))
    b.metric('Listings with licensed photo', int(df['business_id'].isin(query('SELECT DISTINCT business_id FROM business_images')['business_id']).sum()))
    c.metric('Covered towns', df['district'].nunique())
    st.caption('Images are displayed only when the source permits reuse. No generic stock photos are mislabelled as actual storefronts.')
    if df.empty:
        st.warning('No businesses match your filters.')
    else:
        rows = df.to_dict('records')
        for offset in range(0, len(rows), 3):
            cols = st.columns(3)
            for col, business in zip(cols, rows[offset:offset+3]):
                with col:
                    with st.container(border=True):
                        show_photo(business['business_id'])
                        st.subheader(business['name'])
                        st.caption(business['district'] + ' · ' + (business['category_list'] or 'Uncategorized'))
                        st.write(business['address'])
                        st.write(public_rating(business))
                        st.caption('Public platform score; independently sourced. BisLK user reviews are separate.')
                        st.link_button('View location on Google Maps', map_url(business['name'],business['address']))
    with st.expander('Verified-coordinate map and straight-line distance (optional)'):
        st.caption('Only entries with independently verified coordinates are mapped; blank is better than fabricated coordinates.')
        points = df.dropna(subset=['latitude','longitude'])
        if not points.empty:
            st.map(points[['latitude','longitude']].rename(columns={'latitude':'lat','longitude':'lon'}))
        else:
            st.info('No verified coordinates for these listings. Use each business\'s Maps search button instead.')

elif page == 'Business details':
    st.title('Business profile and photos')
    df = top_businesses()
    selected = st.selectbox('Choose business', list(df['business_id']),
                            format_func=lambda bid: df.loc[df.business_id==bid,'name'].iloc[0])
    b = df.loc[df.business_id==selected].iloc[0]
    left, right = st.columns([1, 1.3])
    with left:
        show_photo(int(selected), caption=True)
        photos = get_photos(int(selected))
        if len(photos)>1:
            with st.expander('Additional photos'):
                for item in photos.iloc[1:].to_dict('records'):
                    st.image(item['file_path'] if item['file_path'].startswith('https://') else str(ROOT/item['file_path']))
                    st.caption(f"{item['caption']} · {item['image_author']} · {item['image_license']}")
                    if item['source_url']: st.link_button('Original photo', item['source_url'])
    with right:
        st.subheader(b['name'])
        st.write(b['description'])
        st.write('**Address:**', b['address'])
        st.write('**Categories:**', b['category_list'])
        st.write('**Public rating:**', public_rating(b))
        st.write('**Paraphrase of public review themes (attributed to source):**')
        st.write(b['public_review_summary'] or 'No verified review summary.')
        st.caption(f"Public snapshot checked: {b['public_checked_on'] or 'Not recorded'}. Ratings may change over time.")
        if pd.notna(b['public_source_url']):
            st.link_button('Read reviews at source', b['public_source_url'])
        if pd.notna(b['address_source_url']):
            st.link_button('Verify street address', b['address_source_url'])
        st.link_button('Search exact place on Maps', map_url(b['name'], b['address']))
    st.divider()
    st.subheader('Category-specific attributes')
    attrs = query('''SELECT c.name AS category, ca.attribute_name, bav.value FROM business_attribute_values bav
                   JOIN category_attributes ca ON ca.attribute_id=bav.attribute_id
                   JOIN categories c ON c.category_id=ca.category_id
                   WHERE bav.business_id=? ORDER BY c.name''', [selected])
    if attrs.empty: st.caption('No category-specific values recorded for this business yet.')
    else: st.dataframe(attrs, hide_index=True, use_container_width=True)
    st.subheader('Reviews submitted within BisLK')
    internal = query('''SELECT u.full_name AS reviewer, r.rating, r.comment, r.reviewed_at
                      FROM reviews r JOIN users u ON u.user_id=r.user_id
                      WHERE r.business_id=? ORDER BY r.reviewed_at DESC''', [selected])
    if internal.empty:
        st.info('No BisLK user reviews yet. Public third-party summaries above are NOT presented as user-submitted reviews.')
    else:
        st.dataframe(internal, hide_index=True, use_container_width=True)

elif page == 'Add business':
    st.title('Register a new business')
    st.caption('Required database programming interface: INSERT into businesses plus related rows in business_categories.')
    categories = cats_df()
    ids = dict(zip(categories['name'], categories['category_id']))
    with st.form('business_form', clear_on_submit=True):
        name=st.text_input('Business name *')
        description=st.text_area('Description')
        address=st.text_input('Real street address *', placeholder='Number / road / town — do not invent an address')
        district=st.selectbox('Town *',['Kandy','Kurunegala','Moratuwa'])
        chosen=st.multiselect('Categories *',list(ids))
        c1,c2=st.columns(2)
        phone=c1.text_input('Telephone (optional)')
        email=c2.text_input('Business email (optional)')
        website=st.text_input('Website (optional)')
        c3,c4=st.columns(2)
        lat=c3.text_input('Verified latitude (optional)')
        lon=c4.text_input('Verified longitude (optional)')
        submitted=st.form_submit_button('Save business', type='primary')
    if submitted:
        try:
            if bool(lat.strip()) != bool(lon.strip()): raise ValueError('Both coordinates are required together.')
            bid=add_business(name,description,address,district,[ids[x] for x in chosen],
                             phone,email,website,float(lat) if lat.strip() else None,
                             float(lon) if lon.strip() else None)
            st.success(f'Saved! Business ID: {bid}. Now add its photo using the photo upload page.')
        except (ValueError,sqlite3.IntegrityError) as e: st.error(str(e))

elif page == 'Upload business photo':
    st.title('Add an image to a business')
    st.write('This demonstrates the **business_images** table: one business can have many photos.')
    st.warning('Upload only images you took, own, or are authorized to reuse. Do not download random Google review photos without permission.')
    businesses=query('SELECT business_id,name,district FROM businesses ORDER BY district,name')
    labels={f"{r.name} — {r.district}":r.business_id for r in businesses.itertuples()}
    with st.form('photo_form'):
        business_label=st.selectbox('Business *', list(labels))
        photo=st.file_uploader('Upload licensed photo', type=['jpg','jpeg','png','webp'])
        author=st.text_input('Photographer / owner attribution *')
        rights=st.selectbox('Rights / licence confirmation *',[
            'I own the image and permit its use in this classroom project',
            'I have explicit permission from its copyright owner',
            'I verified a reusable Creative Commons or public-domain licence',
        ])
        confirm=st.checkbox('I confirm I am authorized to upload this image')
        save=st.form_submit_button('Add image to database',type='primary')
    if save:
        try:
            if not photo or not author.strip() or not confirm:
                raise ValueError('Choose an image, credit the photographer, and confirm rights.')
            image_id=add_photo_bytes(labels[business_label], photo.name, photo.getvalue(), rights, author)
            st.success(f'Photo saved locally and linked to business_images (image_id={image_id}).')
        except (ValueError,sqlite3.IntegrityError) as e: st.error(str(e))

elif page == 'Add review':
    st.title('Write a new BisLK review')
    st.caption('These are newly entered app reviews. No imported review author or rating has been impersonated.')
    people=query('SELECT user_id,full_name FROM users ORDER BY user_id')
    businesses=query('SELECT business_id,name FROM businesses ORDER BY name')
    u={f"{r.user_id} · {r.full_name}":r.user_id for r in people.itertuples()}
    b={f"{r.business_id} · {r.name}":r.business_id for r in businesses.itertuples()}
    if not u: st.warning('Register a user first.')
    else:
        with st.form('review_form',clear_on_submit=True):
            chosen_user=st.selectbox('Review author',list(u))
            chosen_business=st.selectbox('Business',list(b))
            score=st.slider('Rating',1,5,4)
            comment=st.text_area('Your own review')
            submitted=st.form_submit_button('Save review',type='primary')
        if submitted:
            rid=add_review(u[chosen_user],b[chosen_business],score,comment)
            st.success(f'New review {rid} added to reviews table. The local-reviews report will update.')

elif page == 'Register user':
    st.title('Create a BisLK demo user')
    with st.form('registration',clear_on_submit=True):
        name=st.text_input('Full name *')
        email=st.text_input('Email *')
        password=st.text_input('Password (8+ characters) *',type='password')
        district=st.selectbox('District',['Kandy','Kurunegala','Moratuwa'])
        phone=st.text_input('Phone')
        submitted=st.form_submit_button('Register user',type='primary')
    if submitted:
        try: st.success(f'New user ID: {add_user(name,email,password,phone,district)}')
        except (ValueError,sqlite3.IntegrityError) as e: st.error(str(e))
    st.caption('Passwords are salted PBKDF2 hashes. This student project does not implement authentication.')

elif page == 'Reports':
    st.title('Live SQL reports')
    st.write('All report numbers are calculated by SQL from `bislk.db`.')
    st.subheader('Report 1 — Most highly rated businesses (public platform snapshots)')
    minimum=st.number_input('Minimum source-reported review count',min_value=0,max_value=5000,value=0,step=10)
    r1=query(REPORT_TOP_RATED,[minimum,minimum])
    st.dataframe(r1,hide_index=True,use_container_width=True)
    if not r1.empty:
        chart=r1.head(15).set_index('business')['public_rating_out_of_5']
        st.bar_chart(chart, y_label='Published rating out of 5')
        st.download_button('Export Report 1 (.csv)',r1.to_csv(index=False).encode('utf-8'),
                           'bislk_public_rating_report.csv',mime='text/csv')
    st.caption('IMPORTANT: External aggregate ratings are sourced snapshots; they are not calculated from BisLK user reviews.')
    st.divider()
    st.subheader('Report 2 — Businesses by town and category')
    r2=query(REPORT_DISTRICT_CATEGORY)
    st.dataframe(r2,hide_index=True,use_container_width=True)
    if not r2.empty:
        pivot=r2.pivot(index='district',columns='category',values='businesses').fillna(0)
        st.bar_chart(pivot,y_label='Business listings')
        st.download_button('Export Report 2 (.csv)',r2.to_csv(index=False).encode('utf-8'),
                           'bislk_town_category_report.csv',mime='text/csv')
    st.caption('Multi-category businesses are counted under each of their registered categories.')
    st.divider()
    st.subheader('Extra report — Reviews submitted by BisLK users')
    r3=query(REPORT_USER_REVIEWS)
    if r3.empty: st.info('No app-user reviews yet. Add one on the Add review page to populate this report.')
    else:
        st.dataframe(r3,hide_index=True,use_container_width=True)
        st.download_button('Export BisLK reviews report',r3.to_csv(index=False).encode('utf-8'),
                           'bislk_user_review_report.csv',mime='text/csv')

elif page == 'Database & sources':
    st.title('Database tables and verification sources')
    st.write('Eight entity tables, with provenance fields added to businesses and business_images.')
    tables=query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    stats=[]
    for tab in tables['name']:
        # tab is one of the validated names returned from sqlite_master, not user input.
        stats.append({'table':tab,'rows':int(query(f'SELECT COUNT(*) AS n FROM "{tab}"').iloc[0]['n'])})
    st.dataframe(pd.DataFrame(stats),hide_index=True,use_container_width=True)
    table=st.selectbox('Inspect a database table',list(tables['name']))
    st.dataframe(query(f'SELECT * FROM "{table}" LIMIT 100'),hide_index=True,use_container_width=True)
    st.subheader('Review source audit')
    src=query('''SELECT name,district,address,public_rating AS published_score_out_of_5,
                public_review_count,public_source_name,public_source_url,address_source_url
                FROM businesses ORDER BY district,name''')
    st.dataframe(src,hide_index=True,use_container_width=True)
    st.download_button('Download business source list',src.to_csv(index=False).encode('utf-8'),
                       'bislk_business_sources.csv',mime='text/csv')
    st.subheader('Image provenance and licences')
    image_src=query('''SELECT b.name,bi.caption,bi.image_author,bi.image_license,
                      bi.license_url,bi.source_url,bi.file_path
                      FROM business_images bi JOIN businesses b ON b.business_id=bi.business_id
                      ORDER BY b.name''')
    st.dataframe(image_src,hide_index=True,use_container_width=True)
    st.caption('Remote Wikimedia Commons images require internet access. No unlicensed commercial listing photos were copied into the ZIP.')
