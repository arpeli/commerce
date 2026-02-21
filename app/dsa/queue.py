from collections import deque


class OrderQueue:
    def __init__(self):
        self._queue = deque()

    def enqueue(self, order):
        self._queue.append(order)

    def dequeue(self):
        if self.is_empty():
            return None
        return self._queue.popleft()

    def peek(self):
        if self.is_empty():
            return None
        return self._queue[0]

    def is_empty(self):
        return len(self._queue) == 0

    def size(self):
        return len(self._queue)

    def to_list(self):
        return list(self._queue)
