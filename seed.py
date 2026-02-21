"""Seed the database with sample data for demo purposes."""
from app import create_app, db
from app.models import User, Store, Product

app = create_app()

with app.app_context():
    db.create_all()

    # Create demo admin/store owner
    if not User.query.filter_by(email='admin@demo.com').first():
        admin = User(name='Demo Admin', email='admin@demo.com', is_store_owner=True)
        admin.set_password('demo1234')
        db.session.add(admin)
        db.session.flush()

        # Create a demo store
        store = Store(
            name='Tech Haven',
            slug='tech-haven',
            description='Your one-stop shop for the latest tech gadgets and accessories.',
            owner_id=admin.id,
        )
        db.session.add(store)
        db.session.flush()

        # Create sample products
        products = [
            Product(
                name='Organic Honey 500g',
                description='Pure organic honey from the highlands of Kenya.',
                price=850.00,
                stock=50,
                category='Food',
                image_url='https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=400',
                store_id=store.id,
            ),
            Product(
                name='Handwoven Kikoy Scarf',
                description='Beautiful handwoven Kikoy scarf in vibrant colors.',
                price=1200.00,
                stock=30,
                category='Fashion',
                image_url='https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=400',
                store_id=store.id,
            ),
            Product(
                name='Maasai Beaded Bracelet',
                description='Authentic Maasai beaded bracelet, handmade by artisans.',
                price=450.00,
                stock=100,
                category='Jewellery',
                image_url='https://images.unsplash.com/photo-1573408301185-9519f94816b5?w=400',
                store_id=store.id,
            ),
            Product(
                name='Kenyan Coffee Blend 250g',
                description='Premium Kenyan AA coffee, medium roast.',
                price=600.00,
                stock=75,
                category='Beverages',
                image_url='https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400',
                store_id=store.id,
            ),
            Product(
                name='Sisal Woven Basket',
                description='Eco-friendly sisal basket, perfect for storage or gifting.',
                price=750.00,
                stock=40,
                category='Home & Living',
                image_url='https://images.unsplash.com/photo-1555529669-2269763671c0?w=400',
                store_id=store.id,
            ),
            Product(
                name='Wireless Earbuds',
                description='High-quality wireless earbuds with 24hr battery life.',
                price=3500.00,
                stock=20,
                category='Electronics',
                image_url='https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400',
                store_id=store.id,
            ),
        ]
        for p in products:
            db.session.add(p)

        db.session.commit()
        print('✅ Database seeded successfully!')
        print('   Admin login: admin@demo.com / demo1234')
    else:
        print('ℹ️  Database already seeded.')
