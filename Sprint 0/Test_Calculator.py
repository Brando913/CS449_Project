import unittest

from Simple_Calculator import add,subtract,multiply,divide

class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(5, 3), 8)

    def test_subtract(self):
        self.assertEqual(subtract(10, 4), 6)

    def test_multiply(self):
        self.assertEqual(multiply(5, 4), 20)

    def test_divide(self):
        self.assertEqual(divide(10, 2), 5)


if __name__ == "__main__":
    unittest.main()