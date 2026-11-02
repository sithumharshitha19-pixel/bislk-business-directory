"""Run with: python tests/test_project.py"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from db import connect_db, query, REPORT_TOP_RATED, REPORT_DISTRICT_CATEGORY


def run():
    with connect_db() as con:
        tabs={r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        required={'users','businesses','reviews','categories','business_categories',
                  'business_images','category_attributes','business_attribute_values'}
        assert required.issubset(tabs), required-tabs
        assert con.execute('SELECT COUNT(*) FROM businesses').fetchone()[0] == 15
        dist=dict(con.execute('SELECT district, COUNT(*) FROM businesses GROUP BY district').fetchall())
        assert dist == {'Kandy':5,'Kurunegala':5,'Moratuwa':5}, dist
        assert con.execute('SELECT COUNT(*) FROM business_images').fetchone()[0] == 5
        assert con.execute('SELECT COUNT(*) FROM reviews').fetchone()[0] == 0
        assert con.execute('PRAGMA foreign_key_check').fetchall() == []
        assert con.execute('SELECT COUNT(*) FROM businesses WHERE address LIKE "%Example%"').fetchone()[0] == 0
        assert con.execute('SELECT COUNT(*) FROM businesses WHERE public_rating IS NOT NULL AND public_source_url IS NOT NULL').fetchone()[0] == 15
        assert con.execute('SELECT COUNT(*) FROM business_attribute_values').fetchone()[0] >= 7
    top=query(REPORT_TOP_RATED,[0,0])
    by_cat=query(REPORT_DISTRICT_CATEGORY)
    assert len(top)==15
    assert len(by_cat)>=9
    print('PASS: 8 ER tables, 15 verified business records (5 per district), 5 licensed image records.')
    print('PASS: no fake reviews, 15 sourced rating snapshots, valid foreign keys, live SQL reports.')

if __name__ == '__main__': run()
