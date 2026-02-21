class BSTNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class ProductBST:
    def __init__(self):
        self.root = None

    def insert(self, key, value):
        """key is product name (lowercase), value is product object/dict."""
        self.root = self._insert(self.root, key, value)

    def _insert(self, node, key, value):
        if node is None:
            return BSTNode(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value
        return node

    def search(self, key):
        """Exact search; returns value or None."""
        return self._search(self.root, key)

    def _search(self, node, key):
        if node is None:
            return None
        if key == node.key:
            return node.value
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)

    def search_prefix(self, prefix):
        """Returns all products where key starts with prefix (lowercase)."""
        results = []
        self._search_prefix(self.root, prefix.lower(), results)
        return results

    def _search_prefix(self, node, prefix, results):
        if node is None:
            return
        if node.key.startswith(prefix):
            results.append(node.value)
        # Traverse left if prefix could appear there
        if node.key >= prefix:
            self._search_prefix(node.left, prefix, results)
        # Traverse right if prefix could appear there
        if node.key <= prefix or node.key[:len(prefix)] <= prefix:
            self._search_prefix(node.right, prefix, results)

    def inorder(self):
        """Returns list of values in sorted key order."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.value)
        self._inorder(node.right, result)
