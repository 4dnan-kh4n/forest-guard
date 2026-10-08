"""Offline real-source selection check; makes no forest or geometry-approval claim."""
from pathlib import Path
from extract_handia_boundary import extract, OFFICIAL_SOURCE_URL
from check_boundary import check_ring

source = Path(__file__).resolve().parents[1]/'data/reference/handia_working_plan_2022_2032/handia_27111.kml'
before = source.read_bytes()
for number, beat, status, vertices in [(278,'JOGA','RF',57),(279,'RAMPURA','PF',95)]:
    collection, report = extract(source, number)
    assert len(collection['features']) == 1
    feature = collection['features'][0]
    assert (feature['properties']['COMPT_NO'],feature['properties']['N_BEAT'],feature['properties']['LGL_Status']) == (str(number),beat,status)
    assert feature['properties']['pilot_approved'] is False
    assert feature['properties']['forest_ground_truth'] is False
    assert feature['properties']['source_url'] == OFFICIAL_SOURCE_URL
    assert check_ring(feature['geometry']['coordinates'][0][0])['vertices_including_closure'] == vertices
    assert report['requested_compartment'] == number
for number in [0,99999]:
    try:
        extract(source, number)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid/missing compartment was accepted.')
assert source.read_bytes() == before
# A similar user export must not inherit the official download's origin claim.
user_source = source.parents[1]/'user_comp_pf_2026_10_08/comp_PF.kml'
if user_source.exists():
    user_before = user_source.read_bytes()
    collection, report = extract(user_source, 279)
    assert collection['features'][0]['properties']['source_url'] is None
    assert report['source_kind'] == 'user_provided_kml_origin_unverified'
    assert report['vertices_including_closure'] == 82
    check_ring(collection['features'][0]['geometry']['coordinates'][0][0])
    assert user_source.read_bytes() == user_before
print('PASS: 278/279 selected independently, source attributes retained, topology checked, source unchanged; no approval or forest labels inferred.')
