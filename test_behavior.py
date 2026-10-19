import struct
import unittest
from tiff_strip_map import inspect,example

def tag(b,number,value):
 b=bytearray(b);struct.pack_into('<I',b,10+number*12+8,value);return bytes(b)
class Behavior(unittest.TestCase):
 def test_example(self):
  r=inspect(example());self.assertEqual(r['pages'][0]['strips'][0]['range'],[122,126]);self.assertEqual(r['findings'],[])
 def test_big_endian(self):
  b=example();out=b'MM'+struct.pack('>HIH',42,8,9)
  for i in range(9):
   t,k,n=struct.unpack_from('<HHI',b,10+i*12);v=struct.unpack_from('<H' if k==3 else '<I',b,18+i*12)[0]
   out+=struct.pack('>HHI',t,k,n)+(struct.pack('>H',v)+bytes(2) if k==3 else struct.pack('>I',v))
  out+=bytes(4)+bytes(range(4));self.assertEqual(inspect(out)['pages'][0]['width'],2)
 def test_metadata_overlap(self):self.assertGreater(inspect(tag(example(),5,8))['overlap_count'],0)
 def test_cycle(self):
  b=bytearray(example());struct.pack_into('<I',b,118,8)
  with self.assertRaisesRegex(ValueError,'cycle'):inspect(b)
 def test_unsupported_format(self):
  for b in (b'II'+struct.pack('<H',43)+bytes(12),tag(example(),3,5),tag(example(),6,3),tag(example(),2,16)):
   with self.assertRaises(ValueError):inspect(b)
 def test_lengths_and_bounds(self):
  for b in (tag(example(),8,5),tag(example(),5,1000),example()[:-1]):
   with self.assertRaises(ValueError):inspect(b)
 def test_duplicate_tag(self):
  b=bytearray(example());struct.pack_into('<H',b,22,256)
  with self.assertRaisesRegex(ValueError,'duplicate'):inspect(b)
 def test_out_of_line_partial_strips_and_alias(self):
  b=bytearray(example());struct.pack_into('<I',b,18+7*12,1)
  for index,offset in ((5,126),(8,134)):
   struct.pack_into('<I',b,14+index*12,2);struct.pack_into('<I',b,18+index*12,offset)
  b+=struct.pack('<IIII',142,144,2,2)+bytes(4)
  r=inspect(b);self.assertEqual([s['rows'] for s in r['pages'][0]['strips']],[[0,1],[1,2]])
  struct.pack_into('<I',b,130,142);self.assertTrue(inspect(b)['findings'][0]['exact_alias'])
 def test_unknown_type(self):
  b=bytearray(example());struct.pack_into('<H',b,12,99)
  with self.assertRaises(ValueError):inspect(b)
