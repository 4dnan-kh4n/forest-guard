"""Extract the official Handia KML's Joga 278 candidate; no boundary approval."""
import argparse
import hashlib
import html
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {'k': 'http://www.opengis.net/kml/2.2'}


def extract(path):
    original = path.read_bytes()
    if len(original) > 2 * 1024**2 or b'<!DOCTYPE' in original.upper():
        raise ValueError('Unexpected or oversized KML.')
    repaired = False
    try:
        root = ET.fromstring(original)
    except ET.ParseError:
        if b'xmlns:xsi=' in original or b'xsi:schemaLocation=' not in original:
            raise
        # The official export omits this namespace. Repair only the parsing copy.
        content = original.replace(b'<Document ',
            b'<Document xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ', 1)
        root = ET.fromstring(content)
        repaired = True
    places = root.findall('.//k:Placemark', NS)
    candidates = []
    for place in places:
        description = place.findtext('k:description', default='', namespaces=NS)
        # Specific to this export's adjacent attribute/value table cells.
        props = {key: html.unescape(value.strip()) for key, value in re.findall(
            r'<td>\s*([A-Za-z0-9_]+)\s*</td>\s*<td>(.*?)</td>', description, re.S)}
        if props.get('N_BEAT') != 'JOGA':
            continue
        if (props.get('Range'), props.get('COMPT_NO'), props.get('LGL_Status')) != ('HANDIA', '278', 'RF'):
            raise ValueError('Additional/different Joga compartment: review before extraction.')
        polygons = []
        for polygon in place.findall('.//k:Polygon', NS):
            rings = []
            boundaries = polygon.findall('k:outerBoundaryIs', NS) + polygon.findall('k:innerBoundaryIs', NS)
            if len(polygon.findall('k:outerBoundaryIs', NS)) != 1:
                raise ValueError('Polygon must have one outer boundary.')
            for index, boundary in enumerate(boundaries):
                text = boundary.findtext('k:LinearRing/k:coordinates', namespaces=NS) or ''
                ring = [list(map(float, item.split(',')[:2])) for item in text.split()]
                if len(ring) < 4 or ring[0] != ring[-1]:
                    raise ValueError('Unclosed/short ring; no geometry repair performed.')
                if not all(len(p) == 2 and all(math.isfinite(v) for v in p)
                           and -180 <= p[0] <= 180 and -90 <= p[1] <= 90 for p in ring):
                    raise ValueError('Invalid longitude/latitude.')
                origin = ring[0]
                area2 = sum((a[0]-origin[0])*(b[1]-origin[1]) - (b[0]-origin[0])*(a[1]-origin[1])
                            for a,b in zip(ring, ring[1:]))
                if area2 == 0:
                    raise ValueError('Zero-area ring.')
                if (area2 > 0) != (index == 0):
                    ring.reverse()  # GeoJSON orientation; same source vertices/geometry.
                rings.append(ring)
            polygons.append(rings)
        if not polygons:
            raise ValueError('No Joga polygons.')
        props.update(source_sha256=hashlib.sha256(original).hexdigest(),
            source_url='https://mpforest.gov.in/publicdomain/Workingplanlibrary/WPLuploaddata//27111.kml',
            status='official-source compartment candidate; pending spatial/current-boundary review',
            current_boundary_verified=False, pilot_approved=False, forest_ground_truth=False)
        candidates.append({'type':'Feature','properties':props,
            'geometry':{'type':'MultiPolygon','coordinates':polygons}})
    if len(candidates) != 1:
        raise ValueError('Expected one Joga candidate; review source changes.')
    coords = [p for f in candidates for polygon in f['geometry']['coordinates'] for ring in polygon for p in ring]
    bbox = [min(p[0] for p in coords), min(p[1] for p in coords),
            max(p[0] for p in coords), max(p[1] for p in coords)]
    return {'type':'FeatureCollection','bbox':bbox,'features':candidates}, {
        'placemarks_inspected':len(places),'joga_candidates':len(candidates),
        'missing_xsi_namespace_added_in_memory':repaired,'source_file_unchanged':True,
        'coordinate_order':'longitude, latitude; KML geographic coordinates',
        'altitudes_discarded_for_2d_boundary':True,'vertices_including_closure':len(coords),
        'ring_structure_checks':'PASS','topology_and_spatial_registration':'NOT CHECKED',
        'source_area_ha_attribute':candidates[0]['properties']['AREA_HA'],
        'area_measured_from_geometry':False,'bbox':bbox}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kml', type=Path)
    args = parser.parse_args()
    before = hashlib.sha256(args.kml.read_bytes()).hexdigest()
    collection, report = extract(args.kml)
    assert hashlib.sha256(args.kml.read_bytes()).hexdigest() == before
    out = args.kml.parent
    (out/'joga_278.candidate.geojson').write_text(json.dumps(collection,indent=2)+'\n')
    (out/'boundary_extraction_report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
