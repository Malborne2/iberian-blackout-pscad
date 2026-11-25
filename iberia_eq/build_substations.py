"""Compile iberia_eq/substations.csv: every Fig 2-4 substation used in the equivalent, with its OSM coordinates and
the zone (equivalent bus) it is assigned to. Sources are recorded per row: OSM element id or Nominatim query.

usage: python iberia_eq/build_substations.py
Inputs (fetched 2026-11-23, OpenStreetMap contributors, ODbL):
  ext/osm_substations_400kV.json  Overpass: power=substation, voltage~400000, ES + PT
  ext/osm_substations_ree.json    Overpass: power=substation, operator~"Red El", ES
  ext/osm_nominatim_places.jsonl  Nominatim: town centroids for substations named after a town
"""
import csv, json, os, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__)); X = os.path.join(HERE, "ext")

# zone code -> description (the equivalent's Spanish 400 kV buses; PT/FR/MA external)
ZONES = {
    "GRA": "Granada / East Andalusia (event 3, 6a8 Malaga)",
    "WAN": "West Andalusia: Sevilla, Cadiz, Huelva, Gibraltar strait + Morocco tie (5a2, 5b2, 6a6-7)",
    "BAD": "Badajoz / South Extremadura + Portugal south tie (4a, 4b, 5b1, 6a3)",
    "CAC": "Caceres / Almaraz / North Extremadura + Portugal centre tie (5b3, 6a4)",
    "SCE": "South-centre corridor: Cordoba, Ciudad Real (Guadame, Cabra, Valdecaballeros, Brazatortas, Manzanares)",
    "MAD": "Madrid load centre",
    "CYL": "Castilla y Leon (Segovia 5a1/5a3, Duero hydro, Mudarra)",
    "NW":  "North-West: Galicia, Asturias, Leon + Portugal north tie",
    "N":   "North: Cantabria, Basque Country, Navarra + Hernani France tie",
    "ARA": "Aragon + Biescas France tie",
    "CAT": "Catalonia + Baixas AC and HVDC France ties",
    "VAL": "Valencia / Castilla-La Mancha east (Eliana, Cofrentes, La Muela, Cuenca 6b)",
    "SE":  "South-East: Murcia, Alicante, Almeria (Rocamora, Litoral; 6a5)",
}

# Fig 2-4 label -> (zone, OSM name fragment or None, nominatim query or None, note)
SUBS = [
    ("CAPARACENA", "GRA", "Caparacena", None, ""), ("HUENEJA", "GRA", "Hu", None, "Hueneja"),
    ("TABERNAS", "SE", "Subestación de Tabernas", None, ""), ("ARCHIDONA", "GRA", "Archidona", None, ""),
    ("CARTAMA", "GRA", "Cártama", None, ""), ("TAJO ENC.", "GRA", "Tajo de la Encantada", None, ""),
    ("JORDANA", "WAN", "Jordana", None, ""), ("PINAR REY", "WAN", "Pinar del Rey", None, ""),
    ("ARCOS FRT.", "WAN", "Arcos de la Frontera", None, ""), ("TARIFA", "WAN", "Subestación de Tarifa", None, ""),
    ("PTO. CRUZ", "WAN", "Puerto de la Cruz", None, "Morocco cable landing"),
    ("GUILLENA", "WAN", "Subestación de Guillena", None, ""), ("D.RODRIGO", "WAN", "Don Rodrigo", None, ""),
    ("CARMONA", "WAN", "Colectora Promotores Carmona", None, "collector, near REE Carmona"),
    ("PALOS", "WAN", "Palos de la Frontera", None, ""),
    ("BIENVENIDA", "BAD", "Subestación de Bienvenida", None, ""), ("BROVALES", "BAD", "SE Brovales", None, ""),
    ("BALBOA", "BAD", "SET Balboa", None, ""), ("S.SERVAN", "BAD", "SE Servan", None, ""),
    ("CARMONITA", "BAD", "SET CARMONITA", None, ""),
    ("ALMARAZ", "CAC", "Subestación Almaraz", None, ""), ("ARANUELO", "CAC", "SET Ara", None, ""),
    ("J.M.ORIOL", "CAC", "José María Oriol", None, "220 kV OSM entry, same site"),
    ("CEDILLO", "CAC", "Subestación de Cedillo", None, "Portugal tie"),
    ("CANAVERAL", "CAC", "SE Ca", None, "Cañaveral"),
    ("VALDECAB.", "SCE", "Subestación de Valdecaballeros", None, ""),
    ("CABRA", "SCE", "Subestación de Cabra", None, ""), ("BRAZATORT", "SCE", "Brazatortas", None, ""),
    ("MANZANARES", "SCE", "SE Manzanares", None, ""), ("RODAANDAL", "SCE", "La Roda de Andaluc", None, ""),
    ("GUADAME", "SCE", "Guadalquivir Medio", None, "INFERRED: SCADA code GUADAME = GUADAlquivir MEdio (no OSM "
                                    "'Guadame'); position fits Fig 2-4 links to Brazatortas/Cabra/Valdecaballeros"),
    ("MORATA", "MAD", "Subestación de Morata", None, ""), ("SS. REYES", "MAD", None, "San Sebastián de los Reyes", "town centroid"),
    ("GALAPAGAR", "MAD", "Subestación de Galapagar", None, ""), ("LA CEREAL", "MAD", "La Cereal", None, ""),
    ("MORALEJA", "MAD", "Subestación de Moraleja", None, ""), ("VILLAVICIOSA", "MAD", "Subestación de Villaviciosa", None, ""),
    ("LOECHES", "MAD", "Loeches", None, ""), ("ANCHUELO", "MAD", "SE Anchuelo", None, ""),
    ("BELINCHON", "MAD", "Belinchon", None, ""),
    ("SEGOVIA", "CYL", "Subestación de Segovia", None, ""), ("LASTRAS", "CYL", "Lastras del Pozo", None, ""),
    ("MUDARRA", "CYL", "La Mudarra", None, ""), ("TORDESILLAS", "CYL", "Subestación Tordesillas", None, ""),
    ("VILLARINO", "CYL", "Subestación de Villarino", None, "Duero hydro"),
    ("ALDEADAVILA", "CYL", "Aldead", None, "Duero hydro, Portugal tie"), ("HINOJOSA", "CYL", "Hinojosa", None, ""),
    ("GRIJOTA", "CYL", "Grijota", None, ""),
    ("MESON", "NW", "Mesón do Vento", None, ""), ("CARTELLE", "NW", "Subestación de Cartelle", None, "Portugal tie"),
    ("SOTO", "NW", "Soto de Ribera", None, ""), ("ROBLA", "NW", "SET La Robla", None, ""),
    ("MONTEARENAS", "NW", "Montearenas", None, ""), ("VELILLA", "NW", "Velilla del R", None, ""),
    ("AGUAYO", "N", "Subestación de Aguayo", None, "pumped storage"), ("HERRERA", "N", "Herrera", None, ""),
    ("GUENES", "N", "Subestación de G", None, "Güeñes"), ("ICHASO", "N", "Itxaso", None, ""),
    ("HERNANI", "N", "Hernani", None, "France tie (Argia)"), ("VITORIA", "N", None, "Vitoria-Gasteiz", "town centroid"),
    ("ARAGON", "ARA", "Subestación Eléctrica Aragón", None, ""), ("MAGALLON", "ARA", "Magall", None, ""),
    ("ESCATRON", "ARA", None, "Escatrón", "town centroid"), ("MEQUINENZA", "ARA", "Mequinenza", None, ""),
    ("VIC", "CAT", "Subestació de Vic", None, "France tie (Baixas)"), ("RUBI", "CAT", "Subestació de Rub", None, ""),
    ("SENTMENAT", "CAT", "Sentmenat", None, ""), ("VANDELLOS", "CAT", "Vandell", None, "nuclear"),
    ("ASCO", "CAT", None, "Ascó, Tarragona", "town centroid, nuclear"),
    ("LA ELIANA", "VAL", "La Eliana", None, ""), ("CATADAU", "VAL", "Catadau", None, ""),
    ("COFRENTES", "VAL", None, "Cofrentes", "town centroid, nuclear"), ("MINGLANILLA", "VAL", "Subestación de Minglanilla", None, ""),
    ("OLMEDILLA", "VAL", "Olmedilla", None, "Cuenca (6b)"), ("TRILLO", "MAD", "Subestación de Trillo", None, "nuclear"),
    ("ROMICA", "SE", "Romica", None, ""), ("PINILLA", "SE", "Subestación de Pinilla", None, ""),
    ("ROCAMORA", "SE", "Rocamora", None, ""), ("LITORAL", "SE", "Subestación Litoral", None, ""),
    ("ALQUEVA", "PT", "Subestação de Alqueva", None, "Portugal, tie to Brovales"),
    ("LINDOSO", "PT", "Posto de Corte do Alto Lindoso", None, "Portugal, tie to Cartelle"),
]


def norm(s): return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def load(fn):
    out = []
    for e in json.load(open(os.path.join(X, fn), encoding="utf-8"))["elements"]:
        c = e.get("center", e); t = e.get("tags", {})
        out.append((t.get("name", ""), t.get("operator", ""), t.get("voltage", ""), c["lat"], c["lon"], f"{e['type']}/{e['id']}"))
    return out


osm = load("osm_substations_400kV.json") + load("osm_substations_ree.json")
nom = [json.loads(l) for l in open(os.path.join(X, "osm_nominatim_places.jsonl"), encoding="utf-8")]
rows = []
for lab, zone, frag, q, note in SUBS:
    lat = lon = None; src = ""
    if frag:
        hits = [o for o in osm if norm(frag) in norm(o[0])]
        hits.sort(key=lambda o: ("400000" not in o[2], "Red El" not in o[1]))
        if hits:
            h = hits[0]; lat, lon = h[3], h[4]; src = f"OSM {h[5]} '{h[0]}' ({h[1] or 'no operator'}; {h[2]})"
    if q:
        h = next((n for n in nom if n["query"] == q), None)
        if h: lat, lon = h["lat"], h["lon"]; src = f"Nominatim '{q}' -> {h['name'][:60]}"
    rows.append({"fig2_4_label": lab, "zone": zone, "lat": "" if lat is None else f"{lat:.4f}",
                 "lon": "" if lon is None else f"{lon:.4f}", "source": src or "none", "note": note})
with open(os.path.join(HERE, "substations.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
miss = [r["fig2_4_label"] for r in rows if not r["lat"]]
print(f"{len(rows)} substations, {len(rows) - len(miss)} located; missing: {miss}")
for z in ZONES:
    s = [r for r in rows if r["zone"] == z and r["lat"]]
    if s:
        print(f"{z:4s} n={len(s):2d} centroid {sum(float(r['lat']) for r in s)/len(s):.3f},{sum(float(r['lon']) for r in s)/len(s):.3f}")
