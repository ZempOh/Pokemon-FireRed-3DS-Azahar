"""Prevent stale builds/evidence from being promoted by the reusable gate."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('pipeline',Path(__file__).parents[1]/'scenery_pipeline.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class GateTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name);(self.root/'game/src').mkdir(parents=True)
  self.source=self.root/'game/src/render.c';self.source.write_text('tested source')
  self.config={'families':['plants','rocks'],'games':{'test':{'repo':'game','sources':['src'],'entrypoints':['src/render.c']}},'required_checks':['thor_field']}
  self.build=self.root/'candidate.apk';self.build.write_bytes(b'tested artifact')
  self.evidence=self.root/'capture.txt';self.evidence.write_text('synthetic test evidence')
  self.report={'game':'test','build_commit':'test-fixture','device':'AYN Thor','source_sha256':p.fingerprint(self.root/'game',self.config['games']['test'])[0],'artifact_sha256':p.digest(self.build),'claim':'partial_environment_update','checks':{'thor_field':{'passed':True,'evidence':[{'path':'capture.txt','sha256':p.digest(self.evidence)}]}}}
  self.path=self.root/'report.json'
 def gate(self):
  self.path.write_text(json.dumps(self.report));return p.gate(self.root,self.config,self.build,self.path)
 def test_exact_candidate(self):self.assertTrue(self.gate()['eligible'])
 def test_changed_source(self):
  self.source.write_text('changed source');self.assertFalse(self.gate()['eligible'])
 def test_changed_profile(self):
  self.config['games']['test']['rom_crc32']='different-revision';self.assertFalse(self.gate()['eligible'])
 def test_changed_artifact(self):
  self.build.write_bytes(b'new build');self.assertFalse(self.gate()['eligible'])
 def test_changed_evidence(self):
  self.evidence.write_text('changed capture');self.assertFalse(self.gate()['eligible'])
 def test_missing_pass(self):
  self.report['checks']['thor_field']['passed']=False;self.assertFalse(self.gate()['eligible'])
 def test_full_coverage_requires_each_family(self):
  self.report.update(claim='all_environment_assets',coverage={'plants':'passed'})
  self.assertFalse(self.gate()['eligible'])
 def test_host_cache_invalidates_changed_output(self):
  recipe=self.root/'steps.json';out=self.root/'host'
  recipe.write_text(json.dumps({'steps':[{'name':'geometry','kind':'host','commands':[['{python}','-c','from pathlib import Path; Path("result.txt").write_text("passed")']],'outputs':['{repo}/result.txt']}]}))
  first=p.run_host_steps(self.root,self.config,'test',recipe,out,'python-test')
  self.assertTrue(first['passed']);self.assertFalse(first['steps'][0]['cached'])
  self.assertTrue(p.run_host_steps(self.root,self.config,'test',recipe,out,'python-test')['steps'][0]['cached'])
  (self.root/'game/result.txt').write_text('changed')
  self.assertFalse(p.run_host_steps(self.root,self.config,'test',recipe,out,'python-test')['steps'][0]['cached'])
 def test_device_stages_cannot_be_cached(self):
  recipe=self.root/'device.json';recipe.write_text(json.dumps({'steps':[{'name':'thor','kind':'device'}]}))
  with self.assertRaises(ValueError):p.run_host_steps(self.root,self.config,'test',recipe,self.root/'host','test')
if __name__=='__main__':unittest.main()
