"""Promotion rejects stale/failed builds and altered binary assets."""
import tempfile
import unittest
from pathlib import Path

from promote import validate_ci, verify_bytes


class PromotionTests(unittest.TestCase):
  def test_ci_must_match_source_and_all_jobs(self) -> None:
    source = 'a' * 40
    good: dict[str, object] = {'headSha':source,'status':'completed','conclusion':'success','jobs':[
      {'name':'Recovery source and updater checks','conclusion':'success'},
      {'name':'Compile comma-three installer and UI on ARM64','conclusion':'success'}]}
    validate_ci(good, source)
    for key, value in [('headSha','b'*40),('status','in_progress'),('conclusion','failure'),('jobs',[])]:
      with self.subTest(key=key), self.assertRaises(ValueError):
        validate_ci(dict(good,**{key:value}), source)

  def test_rejects_modified_artifact(self) -> None:
    with tempfile.TemporaryDirectory() as directory:
      binary = Path(directory)/'installer'
      binary.write_bytes(b'changed')
      with self.assertRaises(ValueError):
        verify_bytes(binary, {'size_bytes':7,'sha256':'0'*64})


if __name__ == '__main__':
  unittest.main()
