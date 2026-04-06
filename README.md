# ShopKenya

A fully-featured e-commerce web application built with Flask, SQLAlchemy, and Tailwind CSS. Includes custom Data Structures and Algorithms (DSA) modules.

---

## Features

- **Multi-store marketplace** — any user can register as a store owner and create a storefront
- **Product catalog** with categories, images, and stock tracking
- **Shopping cart** — session-based for guests, database-backed for logged-in users
- **Checkout & orders** — order creation with item-level records
- **M-Pesa STK push integration** — real Safaricom Daraja API support (sandbox + live)
- **Admin dashboard** — stats, product management (add/edit/deactivate), order tracking
- **Product search** — prefix-based search powered by a custom BST
- **Beautiful UI** — Tailwind CSS with gradients, responsive grid, hover effects

### DSA Modules Used

| Module | Data Structure | Used In |
|--------|---------------|---------|
| `app/dsa/heap.py` | MinHeap / MaxHeap | Sort featured products by price on homepage and storefront |
| `app/dsa/queue.py` | OrderQueue (deque) | Pending order queue in admin dashboard |
| `app/dsa/bst.py` | Binary Search Tree | Product search with prefix matching |
| `app/dsa/linked_list.py` | Doubly Linked List | Cart representation and total calculation |
| `app/dsa/sorting.py` | QuickSort (Lomuto) | Sort products by name/price/date in admin and storefront |

---

## Project Structure

```
flask-demo/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── dsa/
│   │   ├── heap.py
│   │   ├── queue.py
│   │   ├── bst.py
│   │   ├── linked_list.py
│   │   └── sorting.py
│   ├── blueprints/
│   │   ├── auth.py
│   │   ├── store.py
│   │   ├── admin.py
│   │   └── payment.py
│   ├── templates/
│   └── static/
├── config.py
├── requirements.txt
├── run.py
└── seed.py
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-org/flask-demo.git
cd flask-demo
```

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Seed the database

```bash
python seed.py
```

### 4. Run the application

```bash
python run.py
```

Visit [http://localhost:5000](http://localhost:5000).

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Store Owner / Admin | admin@demo.com | demo1234 |

---

## M-Pesa Setup

Set these environment variables for live M-Pesa integration:

```env
MPESA_CONSUMER_KEY=your_consumer_key
MPESA_CONSUMER_SECRET=your_consumer_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your_passkey
MPESA_CALLBACK_URL=https://yourdomain.com/payment/callback
```

Sign up at [developer.safaricom.co.ke](https://developer.safaricom.co.ke/). Without credentials, the app runs in demo mode.

---

## DSA Concepts

- **MinHeap/MaxHeap** — heap sort for product price ordering
- **OrderQueue** — FIFO queue for pending order processing
- **ProductBST** — binary search tree for prefix product search
- **CartLinkedList** — doubly linked list for cart management
- **QuickSort** — Lomuto partition sort for product listings
