"""Optional: download the freely licensed Wikimedia thumbnails for offline classroom demo.

Run once ON YOUR COMPUTER with internet: python cache_images.py
Database attribution/license/source fields remain unchanged. Failed downloads keep URL.
"""
import sqlite3
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from db import connect_db, IMAGE_DIR


def run():
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    count=0
    with connect_db() as con:
        photos=con.execute("SELECT image_id,file_path FROM business_images WHERE image_origin='wikimedia_commons'").fetchall()
        for photo in photos:
            url=photo['file_path']
            if not url.startswith('https://'):
                print(f"Photo {photo['image_id']}: cached already")
                continue
            parsed=urlparse(url)
            if parsed.hostname not in ('upload.wikimedia.org','thumb.wikimedia.org'):
                print(f"Photo {photo['image_id']}: skipped non-Wikimedia URL")
                continue
            dest=IMAGE_DIR / f"commons_{photo['image_id']}.jpg"
            try:
                req=Request(url,headers={'User-Agent':'BisLKStudentDBMSProject/1.0 (Wikimedia Commons photo cache)'})
                with urlopen(req, timeout=20) as res:
                    data=res.read(8_000_001)
                    if not res.headers.get('Content-Type','').startswith('image/'):
                        raise ValueError('Response was not an image.')
                    if len(data)>8_000_000:
                        raise ValueError('Photo larger than 8 MB.')
                from PIL import Image
                from io import BytesIO
                img=Image.open(BytesIO(data))
                img.verify()
                dest.write_bytes(data)
                con.execute('UPDATE business_images SET file_path=? WHERE image_id=?',
                            (f'images/{dest.name}',photo['image_id']))
                con.commit()
                count+=1
                print(f"Photo {photo['image_id']}: saved to {dest}")
            except Exception as e:
                dest.unlink(missing_ok=True)
                print(f"Photo {photo['image_id']}: could not cache ({e}); original online URL retained")
    print(f'Cached {count} photos. You can now run the Streamlit application.')

if __name__=='__main__':run()
