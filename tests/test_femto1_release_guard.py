import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'/'femto1'))
from release_guard import validate_gates
from reveal_v2 import consume_marker
from release_guard import canonical_sha
from common import sha

def synthetic_evidence(folder):
    folder=Path(folder)
    geometry={'synthetic':True,'coordinates':[1e-6,2e-6]}
    files={}
    def record(name,value):
        f=folder/(name+'.json');f.write_text(json.dumps(value),encoding='utf8')
        files[name]={'path':str(f.resolve()),'sha256':sha(f)}
    record('geometry',geometry)
    record('F0',{'supplier_domain':'femtoprint.ch','reply_message_id':'SYNTHETIC_NOT_REAL_REPLY',
                 'written_rules_confirmed':True,'accepted_design_formats':['SYNTHETIC_FORMAT']})
    record('F3',{'passed':True,'error_count':0,'supplier_rules_confirmed':True,
                 'F0_evidence_sha256':files['F0']['sha256'],'geometry_sha256':files['geometry']['sha256']})
    canonical=canonical_sha(geometry)
    record('F4',{'roundtrip_identical':True,'geometry_canonical_sha256':canonical,'export_canonical_sha256':canonical})
    record('F5',{'passed':True,'geometry_canonical_sha256':canonical,'supplier_profile_confirmed':True,
                 'polarizations_validated':2,'maximum_split_absolute_error':.01,'maximum_integrated_interference_fraction':.005})
    record('F6',{'passed':True,'geometry_canonical_sha256':canonical,'all_required_error_sources_included':True,
                 'minimum_polarization_mean_accuracy':.86,'source_power_required_W':.009,'unresolved_blockers':0})
    f=folder/'release.json';f.write_text(json.dumps({'schema':'femto1_release_evidence_v1','evidence':files}),encoding='utf8')
    return f,files

class ReleaseGate(unittest.TestCase):
    def test_ready_boolean_cannot_substitute_for_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            f=Path(folder)/'fake.json';f.write_text(json.dumps({'sealed_test_ready':True}))
            with self.assertRaisesRegex(RuntimeError,'schema'):validate_gates(f)

    def test_schema_without_hashes_remains_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            f=Path(folder)/'fake.json';f.write_text(json.dumps({'schema':'femto1_release_evidence_v1','sealed_test_ready':True}))
            with self.assertRaisesRegex(RuntimeError,'hashed'):validate_gates(f)

    def test_consumption_marker_precedes_any_label_export_and_is_exclusive(self):
        with tempfile.TemporaryDirectory() as folder:
            f=Path(folder)/'reveal_started.json'
            consume_marker(f,{'release':'synthetic'})
            with self.assertRaises(FileExistsError):consume_marker(f,{'release':'second'})
            self.assertEqual(json.loads(f.read_text()),{'release':'synthetic'})

    def test_hash_linked_synthetic_fixture_only(self):
        with tempfile.TemporaryDirectory() as folder:
            f,_=synthetic_evidence(folder)
            self.assertTrue(validate_gates(f)['verified'])

    def test_changed_upstream_artifact_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            f,files=synthetic_evidence(folder)
            Path(files['F3']['path']).write_text('{}')
            with self.assertRaisesRegex(RuntimeError,'changed F3'):validate_gates(f)

    def test_resigned_geometry_still_must_match_drc(self):
        with tempfile.TemporaryDirectory() as folder:
            f,files=synthetic_evidence(folder)
            g=Path(files['geometry']['path']);g.write_text('{"synthetic_changed":true}')
            m=json.loads(f.read_text());m['evidence']['geometry']['sha256']=sha(g);f.write_text(json.dumps(m))
            with self.assertRaisesRegex(RuntimeError,'another geometry'):validate_gates(f)

    def test_one_polarization_cannot_pass_even_with_updated_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            f,files=synthetic_evidence(folder)
            g=Path(files['F5']['path']);v=json.loads(g.read_text());v['polarizations_validated']=1;g.write_text(json.dumps(v))
            m=json.loads(f.read_text());m['evidence']['F5']['sha256']=sha(g);f.write_text(json.dumps(m))
            with self.assertRaisesRegex(RuntimeError,'polarization'):validate_gates(f)

    def test_conditional_power_model_is_not_full_f6(self):
        with tempfile.TemporaryDirectory() as folder:
            f,files=synthetic_evidence(folder)
            g=Path(files['F6']['path']);v=json.loads(g.read_text());v['all_required_error_sources_included']=False;g.write_text(json.dumps(v))
            m=json.loads(f.read_text());m['evidence']['F6']['sha256']=sha(g);f.write_text(json.dumps(m))
            with self.assertRaisesRegex(RuntimeError,'Complete tolerance'):validate_gates(f)

if __name__=='__main__':unittest.main()
