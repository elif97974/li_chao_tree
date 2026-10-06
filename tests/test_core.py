import unittest

from li_chao_tree import LiChaoTree, Line


class TestConstruction(unittest.TestCase):
    def test_basic_construction(self):
        tree = LiChaoTree(0, 10)
        self.assertEqual(tree.x_min, 0)
        self.assertEqual(tree.x_max, 10)
        self.assertEqual(len(tree), 11)
        self.assertTrue(tree.is_empty())

    def test_empty_query_before_insert(self):
        tree = LiChaoTree(0, 10)
        self.assertIsNone(tree.query(5))
        self.assertIsNone(tree.query_line(5))

    def test_single_point_domain(self):
        tree = LiChaoTree(7, 7)
        tree.add_line(2, 3)  # f(7) = 17
        self.assertEqual(tree.query(7), 17)

    def test_negative_domain(self):
        tree = LiChaoTree(-10, -1)
        tree.add_line(1, 0)  # f(x) = x
        self.assertEqual(tree.query(-10), -10)
        self.assertEqual(tree.query(-1), -1)

    def test_rejects_inverted_domain(self):
        with self.assertRaises(ValueError):
            LiChaoTree(10, 0)

    def test_query_out_of_range(self):
        tree = LiChaoTree(0, 10)
        tree.add_line(1, 0)
        with self.assertRaises(ValueError):
            tree.query(-1)
        with self.assertRaises(ValueError):
            tree.query(11)


class TestSingleLine(unittest.TestCase):
    def test_constant_line(self):
        tree = LiChaoTree(0, 10)
        tree.add_line(0, 5)
        for x in range(11):
            self.assertEqual(tree.query(x), 5)

    def test_positive_slope(self):
        tree = LiChaoTree(0, 10)
        tree.add_line(2, 1)  # 2x + 1
        self.assertEqual(tree.query(0), 1)
        self.assertEqual(tree.query(5), 11)
        self.assertEqual(tree.query(10), 21)

    def test_negative_slope(self):
        tree = LiChaoTree(0, 10)
        tree.add_line(-3, 30)  # -3x + 30
        self.assertEqual(tree.query(0), 30)
        self.assertEqual(tree.query(10), 0)


class TestTwoLines(unittest.TestCase):
    def test_crossing_inside_domain(self):
        # f1(x) = x        (slope 1)
        # f2(x) = 10 - x   (slope -1)
        # cross at x = 5: both equal 5; f2 wins left, f1 wins right.
        tree = LiChaoTree(0, 10)
        tree.add_line(1, 0)
        tree.add_line(-1, 10)
        for x in range(11):
            expected = max(x, 10 - x)
            self.assertEqual(tree.query(x), expected, f"failed at x={x}")

    def test_insert_ascending_then_descending(self):
        # Two lines that cross inside the domain; the envelope is the same
        # regardless of insertion order. This guards against a subtle bug
        # where the tree's push-down logic depends on which line arrives
        # first.
        for order in ("asc", "desc"):
            tree = LiChaoTree(0, 10)
            if order == "asc":
                tree.add_line(1, 0)
                tree.add_line(-1, 10)
            else:
                tree.add_line(-1, 10)
                tree.add_line(1, 0)
            for x in range(11):
                expected = max(x, 10 - x)
                self.assertEqual(
                    tree.query(x), expected, f"order={order} x={x}"
                )

    def test_crossing_outside_domain(self):
        # f1(x) = 2x, f2(x) = 2x + 5: parallel, f2 always wins by 5.
        tree = LiChaoTree(0, 10)
        tree.add_line(2, 0)
        tree.add_line(2, 5)
        for x in range(11):
            self.assertEqual(tree.query(x), 2 * x + 5)

    def test_parallel_strictly_dominant(self):
        # f1(x) = 3x + 1 (dominant), f2(x) = 3x - 4 (always worse)
        tree = LiChaoTree(0, 10)
        tree.add_line(3, 1)
        tree.add_line(3, -4)
        for x in range(11):
            self.assertEqual(tree.query(x), 3 * x + 1)


class TestManyLines(unittest.TestCase):
    def test_upper_envelope_of_several(self):
        # Lines: y = 0, y = x, y = 10 - x, y = 2x - 4, y = -2x + 16
        # Expected envelope = max of the five at each x in [0, 10].
        tree = LiChaoTree(0, 10)
        lines = [(0, 0), (1, 0), (-1, 10), (2, -4), (-2, 16)]
        for slope, intercept in lines:
            tree.add_line(slope, intercept)
        for x in range(11):
            expected = max(slope * x + intercept for slope, intercept in lines)
            self.assertEqual(tree.query(x), expected, f"failed at x={x}")

    def test_envelope_unchanged_by_inserting_dominated(self):
        tree = LiChaoTree(0, 10)
        tree.add_line(1, 0)
        tree.add_line(-1, 10)
        before = [tree.query(x) for x in range(11)]
        # Strictly dominated line.
        tree.add_line(0, -100)
        after = [tree.query(x) for x in range(11)]
        self.assertEqual(before, after)

    def test_query_line_returns_a_winner(self):
        tree = LiChaoTree(0, 10)
        tree.add_line(1, 0)
        tree.add_line(-1, 10)
        winner = tree.query_line(0)
        self.assertIsInstance(winner, Line)
        self.assertEqual(winner.eval_at(0), tree.query(0))
        winner_right = tree.query_line(10)
        self.assertEqual(winner_right.eval_at(10), tree.query(10))


class TestEdges(unittest.TestCase):
    def test_identical_lines_inserted_twice(self):
        tree = LiChaoTree(0, 5)
        tree.add_line(2, 3)
        tree.add_line(2, 3)
        for x in range(6):
            self.assertEqual(tree.query(x), 2 * x + 3)

    def test_wide_domain_sparse_queries(self):
        # Exercises the "size rounding up to next power of two" path: a
        # domain of width 1000 rounds up to 1024 leaves, and we query only
        # the endpoints plus the midpoint to confirm indexing stays correct
        # at the extremes.
        tree = LiChaoTree(0, 999)
        tree.add_line(1, 0)
        tree.add_line(-1, 999)
        self.assertEqual(tree.query(0), 999)
        self.assertEqual(tree.query(999), 999)
        mid = (0 + 999) >> 1
        expected = max(mid, 999 - mid)
        self.assertEqual(tree.query(mid), expected)

    def test_all_lines_same_slope(self):
        tree = LiChaoTree(0, 10)
        for intercept in range(10):
            tree.add_line(5, intercept)
        for x in range(11):
            self.assertEqual(tree.query(x), 5 * x + 9)


if __name__ == "__main__":
    unittest.main()
