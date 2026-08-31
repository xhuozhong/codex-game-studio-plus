"""Behavior checks for offline production helpers using original temporary fixtures."""
import copy
import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
import wave
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]

def module(skill, file):
    spec = importlib.util.spec_from_file_location(file, ROOT/'skills'/skill/'scripts'/f'{file}.py')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

assets = module('asset-production-director', 'asset_manifest')
levels = module('game-level-builder', 'level_audit')
audio = module('game-audio-director', 'audio_audit')
locale = module('narrative-localization-engineer', 'localization_audit')

class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='studio-production-')
        self.root = Path(self.temp.name)
        (self.root/'art.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        (self.root/'license.txt').write_text('Original test fixture, public domain dedication for this test.')
        (self.root/'runtime.txt').write_text('Synthetic evidence file; not a claim that a renderer ran.')
        self.asset = {'id':'art','kind':'image','path':'art.svg','sha256':assets.digest(self.root/'art.svg'),
                      'source':'self-authored test','license':{'id':'CC0-1.0','reviewed':True,'evidence':'license.txt'},
                      'status':'verified','evidence':['runtime.txt']}

    def tearDown(self):
        self.assertEqual(self.root.resolve().parent, Path(tempfile.gettempdir()).resolve())
        self.assertTrue(self.root.name.startswith('studio-production-'))
        self.temp.cleanup()

    def manifest(self, asset=None):
        return {'schema_version':1,'assets':[asset or self.asset]}

    def test_release_checks_declared_evidence_and_hash(self):
        self.assertTrue(assets.audit(self.root,self.manifest(),True)['ok'])
        (self.root/'art.svg').write_text('changed without approval')
        self.assertFalse(assets.audit(self.root,self.manifest(),True)['ok'])

    def test_draft_cannot_be_released(self):
        self.asset['status']='processed'
        self.assertTrue(assets.audit(self.root,self.manifest())['ok'])
        self.assertFalse(assets.audit(self.root,self.manifest(),True)['ok'])

    def test_unknown_license_and_missing_evidence(self):
        self.asset['license']['id']='UNKNOWN'
        self.assertFalse(assets.audit(self.root,self.manifest(),True)['ok'])
        self.asset['license']['id']='CC0-1.0'
        (self.root/'runtime.txt').unlink()
        self.assertFalse(assets.audit(self.root,self.manifest(),True)['ok'])

    def test_traversal_absolute_ads_and_windows_path_are_rejected(self):
        for unsafe in ('../license.txt','/license.txt','C:/license.txt','art.svg:stream','a\\b','./art.svg'):
            with self.subTest(path=unsafe), self.assertRaises((ValueError,OSError)):
                assets.local_file(self.root,unsafe)

    def test_duplicate_path_id_missing_dependency_and_size_budget(self):
        duplicate=copy.deepcopy(self.asset)
        self.assertFalse(assets.audit(self.root,{'schema_version':1,'assets':[self.asset,duplicate]})['ok'])
        duplicate['id']='different'
        self.assertFalse(assets.audit(self.root,{'schema_version':1,'assets':[self.asset,duplicate]})['ok'])
        self.asset['depends_on']=['not-listed']
        self.assertFalse(assets.audit(self.root,self.manifest())['ok'])
        self.asset.pop('depends_on')
        self.asset['max_bytes']=1
        self.assertFalse(assets.audit(self.root,self.manifest())['ok'])

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"assets":[],"assets":[]}',object_pairs_hook=assets.unique_object)

    def map(self):
        return {'type':'map','width':2,'height':2,'tilewidth':32,'tileheight':32,
                'tilesets':[{'firstgid':1,'tilecount':1,'image':'art.svg'}],
                'layers':[{'name':'Collision','type':'tilelayer','width':2,'height':2,'data':[1,0,0,0]},
                          {'name':'Spawns','type':'objectgroup','objects':[{'id':1,'point':True,'x':48,'y':48}]}]}

    def checkmap(self,data,spawns=False):
        (self.root/'map.json').write_text(json.dumps(data))
        return levels.inspect(self.root,'map.json','Spawns' if spawns else None,'Collision' if spawns else None)

    def test_map_resources_flip_flags_and_spawn(self):
        data=self.map()
        data['layers'][0]['data'][0]=0x80000001
        self.assertTrue(self.checkmap(data,True)['ok'])
        data['layers'][1]['objects'][0].update(x=0,y=0)
        self.assertFalse(self.checkmap(data,True)['ok'])

    def test_map_missing_reference_invalid_gid_and_object_id(self):
        data=self.map();data['tilesets'][0]['image']='missing.svg'
        self.assertFalse(self.checkmap(data)['ok'])
        data=self.map();data['layers'][0]['data'][1]=5
        self.assertFalse(self.checkmap(data)['ok'])
        data=self.map();data['layers'][1]['objects']*=2
        self.assertFalse(self.checkmap(data)['ok'])

    def test_map_unsupported_formats_do_not_pass(self):
        data=self.map();data['infinite']=True
        self.assertFalse(self.checkmap(data)['ok'])
        data=self.map();data['layers'][0]['data']='encoded'
        self.assertFalse(self.checkmap(data)['ok'])
        data=self.map();data['layers'][0]['offsetx']=2
        self.assertFalse(self.checkmap(data,True)['ok'])

    def test_tiled_sparse_image_collection_ids(self):
        data=self.map()
        data['tilesets']=[{'firstgid':1,'tilecount':2,'columns':0,'tiles':[{'id':0,'image':'art.svg'},{'id':5,'image':'art.svg'}]}]
        data['layers'][0]['data'][0]=6
        self.assertTrue(self.checkmap(data)['ok'])
        data['layers'][0]['data'][0]=4
        self.assertFalse(self.checkmap(data)['ok'])

    def test_ldtk_external_level_and_duplicate_entity(self):
        level={'layerInstances':[{'__identifier':'Entities','entityInstances':[{'iid':'unique'}]}]}
        (self.root/'one.ldtkl').write_text(json.dumps(level))
        data={'defs':{'tilesets':[{'relPath':'art.svg'}]},'levels':[{'externalRelPath':'one.ldtkl'}]}
        self.assertTrue(self.checkmap(data)['ok'])
        data['levels']*=2
        self.assertFalse(self.checkmap(data)['ok'])

    def wav(self, values, width=2):
        file=self.root/'test.wav'
        with wave.open(str(file),'wb') as writer:
            writer.setnchannels(1);writer.setsampwidth(width);writer.setframerate(24000)
            writer.writeframes(b''.join((int(v).to_bytes(width,'little',signed=True) if width>1 else bytes([v+128])) for v in values))
        return file

    def test_audio_pcm_peak_silence_and_loop_bounds(self):
        result=audio.inspect(self.wav([0,16384,-32768,32767]))
        self.assertEqual(result['full_scale_samples'],2)
        self.assertEqual(result['peak_linear'],1)
        self.assertFalse(result['silent'])
        self.assertTrue(audio.inspect(self.wav([0]*10))['silent'])
        with self.assertRaises(ValueError):audio.inspect(self.root/'test.wav',0,11)

    def test_audio_8bit_and_24bit_pcm(self):
        for width in (1,3):
            self.assertEqual(audio.inspect(self.wav([0,-2**(width*8-1)],width))['peak_linear'],1)

    def strings(self):
        return {'schema_version':1,'default_locale':'en','locales':{'en':{'hello':'Hello {name}'},'zh-CN':{'hello':'你好，{name}'}}}

    def test_localized_placeholders_and_missing_ids(self):
        data=self.strings();self.assertTrue(locale.audit(data)['ok'])
        data['locales']['zh-CN']['hello']='你好，{user}'
        self.assertFalse(locale.audit(data)['ok'])
        data=self.strings();data['locales']['zh-CN']['hello']='{name} {name}'
        self.assertFalse(locale.audit(data)['ok'])
        data=self.strings();del data['locales']['zh-CN']['hello']
        self.assertFalse(locale.audit(data)['ok'])

    def test_empty_translation_and_duplicate_key(self):
        data=self.strings();data['locales']['zh-CN']['hello']=' '
        self.assertFalse(locale.audit(data)['ok'])
        with self.assertRaises(ValueError):
            json.loads('{"a":"one","a":"two"}',object_pairs_hook=locale.unique_object)

if __name__=='__main__':
    unittest.main(verbosity=2)
