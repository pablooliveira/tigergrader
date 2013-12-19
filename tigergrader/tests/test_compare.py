import unittest
from testhelper import TestHelper
from tigergrader.compare import compare


class CompareTestCases(TestHelper):
    def test_compare_equal(self):
        res = compare("equal", "equal")
        assert res[0]

    def test_compare_tooshort(self):
        res = compare("1 2 3 4", "1 2 3")
        assert not res[0]
        assert "was expecting 4 at the end" in res[1]

    def test_compare_toolong(self):
        res = compare("1 2 3", "1 2 3 4")
        assert res[0]

    def test_compare_toolong_strict(self):
        res = compare("1 2 3", "1 2 3 4", strict=True)
        assert not res[0]
        assert "got 4 but nothing was expected" in res[1]

if __name__ == '__main__':
    unittest.main()
