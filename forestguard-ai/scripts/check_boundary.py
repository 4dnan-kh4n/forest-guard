"""Check a small single-ring candidate offline; does not approve geography."""
import argparse
import hashlib
import json
from decimal import Decimal
from pathlib import Path


def check_ring(coordinates):
    if not 4 <= len(coordinates) <= 500:
        raise ValueError('Expected 4-500 vertices including closure.')
    points = []
    for point in coordinates:
        if len(point) != 2:
            raise ValueError('Expected 2D longitude/latitude coordinates.')
        x, y = (Decimal(str(v)) for v in point)
        if not x.is_finite() or not y.is_finite() or not -180 <= x <= 180 or not -90 <= y <= 90:
            raise ValueError('Invalid geographic coordinates.')
        points.append((x, y))
    if points[0] != points[-1]:
        raise ValueError('Ring is not closed.')
    if max(p[0] for p in points)-min(p[0] for p in points) > 1 or max(p[1] for p in points)-min(p[1] for p in points) > 1:
        raise ValueError('This planar check is limited to small local boundaries.')

    def cross(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

    def on_segment(a, b, p):
        return min(a[0],b[0]) <= p[0] <= max(a[0],b[0]) and min(a[1],b[1]) <= p[1] <= max(a[1],b[1])

    edges = list(zip(points, points[1:]))
    if any(a == b for a,b in edges):
        raise ValueError('Zero-length boundary edge.')
    unique = points[:-1]
    for i,b in enumerate(unique):
        a,c = unique[i-1],unique[(i+1) % len(unique)]
        if cross(a,b,c) == 0 and (b[0]-a[0])*(c[0]-b[0])+(b[1]-a[1])*(c[1]-b[1]) < 0:
            raise ValueError('Adjacent boundary edges overlap/backtrack.')
    # ponytail: O(n²), bounded to 500 vertices; use a spatial library for large geometries.
    comparisons = 0
    for i,(a,b) in enumerate(edges):
        for j in range(i+1, len(edges)):
            if j == i+1 or (i == 0 and j == len(edges)-1):
                continue
            c,d = edges[j]
            comparisons += 1
            o1,o2,o3,o4 = cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)
            if (o1*o2 < 0 and o3*o4 < 0) or any([
                o1 == 0 and on_segment(a,b,c), o2 == 0 and on_segment(a,b,d),
                o3 == 0 and on_segment(c,d,a), o4 == 0 and on_segment(c,d,b)]):
                raise ValueError(f'Nonadjacent edges intersect/touch: {i}, {j}.')
    if sum(cross(points[0], a, b) for a,b in edges) == 0:
        raise ValueError('Zero signed ring area.')
    return {'vertices_including_closure':len(points),'nonadjacent_edge_pairs_checked':comparisons}


def self_check():
    square = [[0,0],[.1,0],[.1,.1],[0,.1],[0,0]]
    assert check_ring(square)['nonadjacent_edge_pairs_checked'] == 2
    check_ring(list(reversed(square)))
    for bad in [square[:-1], [[0,0],[.1,.1],[0,.1],[.1,0],[0,0]],
                [[0,0],[.1,0],[.1,0],[0,.1],[0,0]]]:
        try:
            check_ring(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('Malformed test geometry accepted.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('geojson', type=Path, nargs='?')
    args = parser.parse_args()
    self_check()  # Synthetic malformed inputs test the checker, not forest results.
    if args.geojson:
        content = args.geojson.read_bytes()
        if len(content) > 1024**2:
            raise ValueError('Candidate exceeds 1 MiB limit.')
        document = json.loads(content)
        if document.get('type') != 'FeatureCollection' or len(document['features']) != 1:
            raise ValueError('Expected one candidate feature.')
        geometry = document['features'][0]['geometry']
        if geometry['type'] != 'MultiPolygon' or len(geometry['coordinates']) != 1 or len(geometry['coordinates'][0]) != 1:
            raise ValueError('This check supports one polygon without holes only.')
        result = check_ring(geometry['coordinates'][0][0])
        result.update(simple_ring_topology='PASS', source_sha256=hashlib.sha256(content).hexdigest(),
            spatial_registration='NOT CHECKED', current_beat_boundary='NOT VERIFIED',
            approved_study_area=False, use='pipeline checks only; user decision')
        (args.geojson.parent/'boundary_topology_report.json').write_text(json.dumps(result,indent=2)+'\n')
        assert args.geojson.read_bytes() == content
        print(json.dumps(result,indent=2))
    else:
        print('PASS: geometry checker self-check, including malformed synthetic inputs.')
