import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import io
import zipfile

url = "https://www.sec.gov/opa/data/market-structure/marketstructuredownloadshtml-by_security"
page = requests.get(url).content
soup = BeautifulSoup(page, 'html.parser')

zip_links = [l.get('href') for l in soup.find_all('a', href=True) if re.search('zip', str(l))]

zip_base = 'https://www.sec.gov/'

def link_to_df(link):
    r = requests.get(link)
    b = io.BytesIO(r.content)
    z= zipfile.ZipFile(b)
    # see if the hoped for contents are there, and if not, dig into any folders in here.
    if any(".zip" in f.filename for f in z.filelist):
        path = z.extract(z.namelist()[0])
        z = zipfile.ZipFile(path)
    print([f.filename for f in z.filelist])
    keep = [f.filename for f in z.filelist if re.search('csv', f.filename)][0]
    path = z.extract(keep)
    return pd.read_csv(path)

df = link_to_df(zip_base + zip_links[0])

for z in zip_links[1:]:
    this_df = link_to_df(zip_base + z)
    df = pd.concat([df, this_df])

df.sample(10)
