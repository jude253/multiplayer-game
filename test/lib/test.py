import unittest

from lib.data_structures import Point


class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual("foo".upper(), "FOO")

    def test_isupper(self):
        self.assertTrue("FOO".isupper())
        self.assertFalse("Foo".isupper())

    def test_split(self):
        s = "hello world"
        self.assertEqual(s.split(), ["hello", "world"])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


class TestPoint(unittest.TestCase):
    def test_point(self):
        pt = Point(0, 1)

        self.assertEqual(pt.x, 0)
        self.assertEqual(pt.y, 1)

        pt = Point(x=0, y=1)

        self.assertEqual(pt.x, 0)
        self.assertEqual(pt.y, 1)


if __name__ == "__main__":
    unittest.main()
