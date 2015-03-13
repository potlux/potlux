import unittest
from potlux.helpers import *

class TestHelperFuntions(unittest.TestCase):
	def test_generate_trie(self):
		schools_trie = Trie()
		print schools_trie.root
		print schools_trie.traverse_trie('wes')

if __name__ == '__main__':
    unittest.main()