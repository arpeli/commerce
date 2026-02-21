class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, item):
        self.heap.append(item)
        self._bubble_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return root

    def _bubble_up(self, i):
        parent = (i - 1) // 2
        if i > 0 and self.heap[i] < self.heap[parent]:
            self.heap[i], self.heap[parent] = self.heap[parent], self.heap[i]
            self._bubble_up(parent)

    def _sift_down(self, i):
        smallest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
            smallest = left
        if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
            smallest = right
        if smallest != i:
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            self._sift_down(smallest)

    def heap_sort(self, items, key=None):
        """Returns items sorted ascending by key using (key_value, index, item) tuples."""
        temp_heap = MinHeap()
        for idx, item in enumerate(items):
            k = key(item) if key else item
            temp_heap.push((k, idx, item))
        result = []
        while temp_heap.heap:
            result.append(temp_heap.pop()[2])
        return result

    def __len__(self):
        return len(self.heap)


class MaxHeap:
    def __init__(self):
        self.heap = []

    def push(self, item):
        self.heap.append(item)
        self._bubble_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return root

    def _bubble_up(self, i):
        parent = (i - 1) // 2
        if i > 0 and self.heap[i] > self.heap[parent]:
            self.heap[i], self.heap[parent] = self.heap[parent], self.heap[i]
            self._bubble_up(parent)

    def _sift_down(self, i):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < len(self.heap) and self.heap[left] > self.heap[largest]:
            largest = left
        if right < len(self.heap) and self.heap[right] > self.heap[largest]:
            largest = right
        if largest != i:
            self.heap[i], self.heap[largest] = self.heap[largest], self.heap[i]
            self._sift_down(largest)

    def heap_sort(self, items, key=None):
        """Returns items sorted descending by key using (key_value, index, item) tuples."""
        temp_heap = MaxHeap()
        for idx, item in enumerate(items):
            k = key(item) if key else item
            temp_heap.push((k, idx, item))
        result = []
        while temp_heap.heap:
            result.append(temp_heap.pop()[2])
        return result

    def __len__(self):
        return len(self.heap)


def heap_sort_products(products, key='price', reverse=False):
    """Sort list of product dicts/objects using heap sort.

    Works with both dicts (product['price']) and objects (product.price).
    If reverse=False, sort ascending (MinHeap); if reverse=True, sort descending (MaxHeap).
    Uses (key_value, index, item) tuples to handle equal keys without comparison errors.
    """
    def get_key(p):
        return p[key] if isinstance(p, dict) else getattr(p, key)

    items = list(products)
    if reverse:
        h = MaxHeap()
        for idx, item in enumerate(items):
            h.push((get_key(item), idx, item))
        result = []
        while h.heap:
            result.append(h.pop()[2])
        return result
    else:
        h = MinHeap()
        for idx, item in enumerate(items):
            h.push((get_key(item), idx, item))
        result = []
        while h.heap:
            result.append(h.pop()[2])
        return result
