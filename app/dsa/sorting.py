def quick_sort(arr, key=None, reverse=False):
    """In-place quicksort using Lomuto partition. Returns the sorted list."""
    if not arr:
        return arr

    def get_key(item):
        if key:
            return key(item)
        return item

    def partition(lo, hi):
        pivot = get_key(arr[hi])
        i = lo - 1
        for j in range(lo, hi):
            val = get_key(arr[j])
            cond = val <= pivot if not reverse else val >= pivot
            if cond:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
        return i + 1

    def _quick_sort(lo, hi):
        if lo < hi:
            p = partition(lo, hi)
            _quick_sort(lo, p - 1)
            _quick_sort(p + 1, hi)

    _quick_sort(0, len(arr) - 1)
    return arr


def _get_attr(item, attr):
    """Return attribute from ORM object or dict."""
    return getattr(item, attr) if hasattr(item, attr) else item[attr]


def sort_products_by_price(products):
    return quick_sort(list(products), key=lambda p: _get_attr(p, 'price'))


def sort_products_by_name(products):
    return quick_sort(list(products), key=lambda p: _get_attr(p, 'name').lower())


def sort_products_by_newest(products):
    return quick_sort(list(products), key=lambda p: _get_attr(p, 'created_at'), reverse=True)
