import pandas as pd
import datetime
import json
import codecs
from copy import copy


with open("postnumre.geojson", "r") as f:
    postnumre = json.loads(f.readlines()[0])

salg = pd.read_csv("copenhagen_sales_info.csv").fillna(0)
salg['year'] = [int(datetime.datetime.strptime(d, "%d-%m-%Y").strftime("%Y")) for d in salg['date']]
new_features = []

for i in range(len(postnumre['features'])):
    within_postal_code = (salg['postal_code'] >= postnumre['features'][i]['properties']['POSTNR_FRA']) & (salg['postal_code'] <= postnumre['features'][i]['properties']['POSTNR_TIL'])
    if len(salg.loc[within_postal_code]) != 0:
        feature = postnumre['features'][i]
        n_salg_per_aar = {d: s for d, s in [(year, sales) for year, sales in zip(range(1992, 2017), [len(salg.loc[within_postal_code & (salg['year'] == y)]) for y in range(1992, 2017)])]}
        middel_per_aar = {d: s if not pd.isnull(s) else 0 for d, s in [(year, sales) for year, sales in zip(range(1992, 2017), [salg.loc[within_postal_code & (salg['year'] == y)]['sales_price'].mean() for y in range(1992, 2017)])]}
        total_per_aar = {d: s if not pd.isnull(s) else 0 for d, s in [(year, sales) for year, sales in zip(range(1992, 2017), [salg.loc[within_postal_code & (salg['year'] == y)]['sales_price'].sum() for y in range(1992, 2017)])]}
        n_salg_per_aar['2017'] = len(salg.loc[within_postal_code])
        middel_per_aar['2017'] = salg.loc[within_postal_code]['sales_price'].mean() 

        feature = copy(postnumre['features'][i])
        feature['properties']['POSTBYNAVN'] = feature['properties']['POSTBYNAVN'].encode("cp1252").decode("utf-8")
        feature['properties']['n_sales_info'] = n_salg_per_aar
        feature['properties']['avg_sales'] = middel_per_aar
        feature['properties']['total_sales'] = total_per_aar
        new_features.append(feature)

postnumre['features'] = new_features

with codecs.open("postnumre_og_salg.geojson", "w", "ISO-8859-1") as fp:
    json.dump(json.loads(json.dumps(postnumre, ensure_ascii=False)), fp)