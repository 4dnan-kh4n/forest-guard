"""Synthetic file-contract checks only; these are not satellite validation."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from verify_sample import FILES, verify


class SampleContractTests(unittest.TestCase):
    def test_manifest_and_report_failures(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            for name in FILES:
                (folder/name).write_bytes(b'synthetic contract fixture; not a raster')
            report = {
                'scene_id':'SYNTHETIC-NOT-A-SATELLITE-SCENE', 'date':'2000-01-01T00:00:00Z',
                'band_order':['B02','B03','B04','B08'], 'model_trained':False,
                'forest_labels_available':False, 'shape':[2,2], 'study_pixels':4,
                'usable_pixels':2, 'usable_fraction':.5, 'scene_class_counts_inside_study':{'4':2,'3':2},
            }
            (folder/'source_stac_item.json').write_text(json.dumps({
                'id':report['scene_id'],'properties':{'datetime':report['date']}}))

            def save():
                (folder/'sample_report.json').write_text(json.dumps(report))
                manifest = {n:{'bytes':(folder/n).stat().st_size,
                    'sha256':hashlib.sha256((folder/n).read_bytes()).hexdigest()} for n in FILES}
                (folder/'checksums.json').write_text(json.dumps(manifest))

            save()
            self.assertEqual(verify(folder)['usable_fraction'], .5)
            (folder/'preview.png').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError, 'File size mismatch'):
                verify(folder)
            save()
            (folder/'preview.png').write_bytes(b'CORRUPT')
            with self.assertRaisesRegex(ValueError, 'Checksum mismatch'):
                verify(folder)
            report['usable_fraction'] = .9
            save()
            with self.assertRaisesRegex(ValueError, 'denominator'):
                verify(folder)
            report['usable_fraction'] = .5
            report['date'] = 'wrong'
            save()
            with self.assertRaisesRegex(ValueError, 'provenance'):
                verify(folder)
            report['date'] = '2000-01-01T00:00:00Z'
            report['model_trained'] = True
            save()
            with self.assertRaisesRegex(ValueError, 'cannot claim'):
                verify(folder)


if __name__ == '__main__':
    unittest.main()
