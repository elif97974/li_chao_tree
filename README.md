# li-cao-tree

A small Python implementation of the Li Chao segment tree: insert linear
functions `f(x) = slope * x + intercept` and query the maximum value among
all inserted lines at any integer point `x`.

```python
from li_chao_tree import LiChaoTree

tree = LiChaoTree(0, 10)      # domain is the closed interval [0, 10]
tree.add_line(1, 0)           # f(x) = x
tree.add_line(-1, 10)         # g(x) = 10 - x

best = tree.query(3)          # 7, from g(3) = 7 > f(3) = 3
winner = tree.query_line(3)   # Line(slope=-1, intercept=10)
```

## Why this exists

The problem is the dynamic upper envelope of lines: given a stream of lines,
answer "which line is highest at x?" for many x. A brute-force scan is
O(lines) per query; a Li Chao tree is O(log W) per insert and per query,
where W is the domain width. The trade-off is that the domain must be a
fixed integer range known up front, and lines cannot be removed once
inserted — the tree has no per-line identity to retire.

## Domain and coordinates

The domain is a **closed** integer interval `[x_min, x_max]`. Both endpoints
are queryable. Only integer coordinates are supported; all comparisons are
integer arithmetic, so there are no floating-point rounding surprises.

## Edge cases you will hit

- `query` on an empty tree returns `None`, not a sentinel value. Check for
  it before doing arithmetic on the result.
- Inserting the same line twice is a no-op envelope-wise; the duplicate is
  kept internally but never affects query results.
- `query_line` returns a line that achieves the maximum; on ties it returns
  the one stored nearest the root, which is stable with respect to tree
  structure rather than insertion order.
- `x` outside `[x_min, x_max]` raises `ValueError`.
