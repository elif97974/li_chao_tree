from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Line:
    slope: int
    intercept: int

    def eval_at(self, x: int) -> int:
        return self.slope * x + self.intercept


_NO_LINE: Optional[Line] = None


class LiChaoTree:
    def __init__(self, x_min: int, x_max: int) -> None:
        if x_min > x_max:
            raise ValueError(
                f"x_min ({x_min}) must be <= x_max ({x_max})"
            )
        self._x_min = x_min
        self._x_max = x_max
        width = x_max - x_min + 1
        self._size = 1
        while self._size < width:
            self._size *= 2
        self._tree: list[Optional[Line]] = [None] * (4 * max(self._size, 1))
        self._has_line = False

    @property
    def x_min(self) -> int:
        return self._x_min

    @property
    def x_max(self) -> int:
        return self._x_max

    def add_line(self, slope: int, intercept: int) -> None:
        self._add_line(Line(slope, intercept), self._x_min, self._x_max, 1)
        self._has_line = True

    def _add_line(self, new: Line, lo: int, hi: int, node: int) -> None:
        cur = self._tree[node]
        if cur is None:
            self._tree[node] = new
            return

        if lo == hi:
            if new.eval_at(lo) > cur.eval_at(lo):
                self._tree[node] = new
            return

        mid = (lo + hi) >> 1

        if new.eval_at(mid) > cur.eval_at(mid):
            self._tree[node], new = new, cur
            cur = self._tree[node]

        if new.slope > cur.slope:
            self._add_line(new, mid + 1, hi, node * 2 + 1)
        elif new.slope < cur.slope:
            self._add_line(new, lo, mid, node * 2)

    def query(self, x: int) -> Optional[int]:
        if x < self._x_min or x > self._x_max:
            raise ValueError(
                f"x ({x}) is outside domain "
                f"[{self._x_min}, {self._x_max}]"
            )
        if not self._has_line:
            return None
        return self._query(x, self._x_min, self._x_max, 1)

    def _query(self, x: int, lo: int, hi: int, node: int) -> int:
        best = self._tree[node]
        result = best.eval_at(x)
        if lo == hi:
            return result
        mid = (lo + hi) >> 1
        if x <= mid:
            child_node = node * 2
        else:
            child_node = node * 2 + 1
        if self._tree[child_node] is None:
            return result
        if x <= mid:
            child = self._query(x, lo, mid, child_node)
        else:
            child = self._query(x, mid + 1, hi, child_node)
        return result if result >= child else child

    def query_line(self, x: int) -> Optional[Line]:
        if x < self._x_min or x > self._x_max:
            raise ValueError(
                f"x ({x}) is outside domain "
                f"[{self._x_min}, {self._x_max}]"
            )
        if not self._has_line:
            return None
        return self._query_line(x, self._x_min, self._x_max, 1)

    def _query_line(self, x: int, lo: int, hi: int, node: int) -> Line:
        best = self._tree[node]
        if lo == hi:
            return best
        mid = (lo + hi) >> 1
        if x <= mid:
            child_node = node * 2
        else:
            child_node = node * 2 + 1
        if self._tree[child_node] is None:
            return best
        if x <= mid:
            child = self._query_line(x, lo, mid, child_node)
        else:
            child = self._query_line(x, mid + 1, hi, child_node)
        if best.eval_at(x) >= child.eval_at(x):
            return best
        return child

    def __len__(self) -> int:
        return self._x_max - self._x_min + 1

    def is_empty(self) -> bool:
        return not self._has_line
