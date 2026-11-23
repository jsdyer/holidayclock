import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import refresh

class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.seed=json.loads((refresh.ROOT/'web/data/canada.json').read_text())
        self.rows=self.seed['years']['2026']
    def test_current_cache_validates(self):
        for year,rows in self.seed['years'].items():
            self.assertEqual(refresh.validate({'holidays':rows},int(year)),rows)
    def test_bad_calendar_records_rejected(self):
        for changed in [[],self.rows+[self.rows[0]],[dict(self.rows[0],observedDate='2026-02-30')],[dict(self.rows[0],date='2025-01-01')]]:
            with self.subTest(changed=str(changed)[:60]),self.assertRaises(ValueError):refresh.validate({'holidays':changed},2026)
    def test_refresh_failure_keeps_previous_cache_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'web/data').mkdir(parents=True)
            (root/'web/config.json').write_text(json.dumps({'seedYearOffsets':[0,1],'minimumYear':2013,'maximumYear':2038,'sources':{'canadaBase':'https://canada-holidays.ca/api/v1/holidays'}}))
            target=root/'web/data/canada.json';target.write_text('previous-good-cache')
            def response(request,**kwargs):
                year=int(request.full_url.split('year=')[1]);rows=copy.deepcopy(self.rows)
                for row in rows:
                    row['date']=str(year)+row['date'][4:];row['observedDate']=str(year)+row['observedDate'][4:]
                if not hasattr(response,'done'):response.done=True;return io.BytesIO(json.dumps({'holidays':rows}).encode())
                raise OSError('provider unavailable')
            with patch.object(refresh,'ROOT',root),patch.object(refresh.urllib.request,'urlopen',response),self.assertRaises(OSError):refresh.main()
            self.assertEqual(target.read_text(),'previous-good-cache')
    def test_complete_refresh_installs_validated_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'web/data').mkdir(parents=True)
            (root/'web/config.json').write_text(json.dumps({'seedYearOffsets':[0],'minimumYear':2013,'maximumYear':2038,'sources':{'canadaBase':'https://canada-holidays.ca/api/v1/holidays'}}))
            def response(request,**kwargs):
                year=int(request.full_url.split('year=')[1]);rows=copy.deepcopy(self.rows)
                for row in rows:
                    row['date']=str(year)+row['date'][4:];row['observedDate']=str(year)+row['observedDate'][4:]
                return io.BytesIO(json.dumps({'holidays':rows}).encode())
            with patch.object(refresh,'ROOT',root),patch.object(refresh.urllib.request,'urlopen',response):refresh.main()
            cache=json.loads((root/'web/data/canada.json').read_text());self.assertEqual(cache['schema'],'coolcode.holidays.canada.v1');self.assertEqual(len(cache['years']),1);self.assertFalse((root/'web/data/canada.tmp').exists())
