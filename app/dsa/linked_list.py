class CartNode:
    def __init__(self, product_id, quantity, price, name='', image_url=''):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
        self.name = name
        self.image_url = image_url
        self.prev = None
        self.next = None


class CartLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def _find(self, product_id):
        current = self.head
        while current:
            if current.product_id == product_id:
                return current
            current = current.next
        return None

    def append(self, product_id, quantity, price, name='', image_url=''):
        """Add to tail, or update quantity if product_id already exists."""
        existing = self._find(product_id)
        if existing:
            existing.quantity += quantity
            return
        node = CartNode(product_id, quantity, price, name, image_url)
        if self.tail is None:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.size += 1

    def remove(self, product_id):
        """Find and remove node with product_id."""
        node = self._find(product_id)
        if not node:
            return
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        self.size -= 1

    def update_quantity(self, product_id, quantity):
        """Find node and update quantity; if quantity <= 0 remove it."""
        if quantity <= 0:
            self.remove(product_id)
            return
        node = self._find(product_id)
        if node:
            node.quantity = quantity

    def total(self):
        """Sum of price * quantity for all nodes."""
        total = 0.0
        current = self.head
        while current:
            total += current.price * current.quantity
            current = current.next
        return total

    def to_list(self):
        """Return list of dicts with product_id, quantity, price, name, image_url, subtotal."""
        result = []
        current = self.head
        while current:
            result.append({
                'product_id': current.product_id,
                'quantity': current.quantity,
                'price': current.price,
                'name': current.name,
                'image_url': current.image_url,
                'subtotal': current.price * current.quantity,
            })
            current = current.next
        return result

    def __len__(self):
        return self.size
