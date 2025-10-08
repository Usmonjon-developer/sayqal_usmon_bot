from datetime import datetime
import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cur = self.conn.cursor()

    # ------------------- USER METHODS -------------------

    def create_user(self, chat_id):
        """Yangi foydalanuvchi yaratish"""
        self.cur.execute("""INSERT INTO user(chat_id) VALUES (?)""", (chat_id,))
        self.conn.commit()

    def update_user_data(self, chat_id, key, value):
        """Foydalanuvchi ma'lumotini yangilash"""
        self.cur.execute(f"""UPDATE user SET {key} = ? WHERE chat_id = ?""", (value, chat_id))
        self.conn.commit()

    def get_user_by_chat_id(self, chat_id):
        """Chat ID orqali foydalanuvchini olish"""
        self.cur.execute("""SELECT * FROM user WHERE chat_id = ?""", (chat_id,))
        user = dict_fetchone(self.cur)
        return user

    # ------------------- CATEGORY METHODS -------------------

    def get_categories_by_parent(self, parent_id=None):
        """Ota kategoriyaga qarab ichki kategoriyalarni olish"""
        if parent_id:
            self.cur.execute("""SELECT * FROM category WHERE parent_id = ?""", (parent_id,))
        else:
            self.cur.execute("""SELECT * FROM category WHERE parent_id IS NULL""")
        return dict_fetchall(self.cur)

    def get_category_parent(self, category_id):
        """Kategoriya ota ID sini olish"""
        self.cur.execute("""SELECT parent_id FROM category WHERE id = ?""", (category_id,))
        return dict_fetchone(self.cur)

    # ------------------- PRODUCT METHODS -------------------

    def get_products_by_category(self, category_id):
        """Kategoriya bo‘yicha mahsulotlarni olish"""
        self.cur.execute("""SELECT * FROM product WHERE category_id = ?""", (category_id,))
        return dict_fetchall(self.cur)

    def get_product_by_id(self, product_id):
        """Mahsulotni ID bo‘yicha olish"""
        self.cur.execute("""SELECT * FROM product WHERE id = ?""", (product_id,))
        return dict_fetchone(self.cur)

    def get_product_for_cart(self, product_id):
        """Savatchaga qo‘shish uchun mahsulotni kategoriya bilan olish"""
        self.cur.execute(
            """
            SELECT 
                product.*, 
                category.name_uz AS cat_name_uz, 
                category.name_ru AS cat_name_ru,
                category.name_en AS cat_name_en
            FROM product 
            INNER JOIN category ON product.category_id = category.id 
            WHERE product.id = ?
            """,
            (product_id,)
        )
        return dict_fetchone(self.cur)

    # ------------------- ORDER METHODS -------------------

    def create_order(self, user_id, products, payment_type, location):
        """Yangi buyurtma yaratish"""
        self.cur.execute(
            """
            INSERT INTO "order"(user_id, status, payment_type, longitude, latitude, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, 1, payment_type, location.longitude, location.latitude, datetime.now())
        )
        self.conn.commit()

        # Oxirgi buyurtma ID sini olish
        self.cur.execute("""SELECT MAX(id) AS last_order FROM "order" WHERE user_id = ?""", (user_id,))
        last_order = dict_fetchone(self.cur)['last_order']

        # Buyurtmaga mahsulotlarni qo‘shish
        for key, val in products.items():
            self.cur.execute(
                """INSERT INTO "order_product"(product_id, order_id, amount, created_at)
                   VALUES (?, ?, ?, ?)""",
                (int(key), last_order, int(val), datetime.now())
            )
        self.conn.commit()

    def get_user_orders(self, user_id):
        """Foydalanuvchining faol buyurtmalarini olish"""
        self.cur.execute("""SELECT * FROM "order" WHERE user_id = ? AND status = 1""", (user_id,))
        return dict_fetchall(self.cur)

    def get_order_products(self, order_id):
        """Buyurtmaga tegishli mahsulotlarni olish"""
        self.cur.execute(
            """
            SELECT order_product.*, 
                   product.name_uz AS product_name_uz, 
                   product.name_ru AS product_name_ru, 
                   product.price AS product_price 
            FROM order_product 
            INNER JOIN product ON order_product.product_id = product.id
            WHERE order_id = ?
            """,
            (order_id,)
        )
        return dict_fetchall(self.cur)

    # ------------------- SUGGESTION METHODS -------------------

    def create_suggestion(self, chat_id, message):
        """Foydalanuvchidan taklif yoki fikr olish"""
        try:
            self.cur.execute(
                "INSERT INTO suggestion(chat_id, message, created_at) VALUES (?, ?, ?)",
                (chat_id, message, datetime.now())
            )
            self.conn.commit()
            print("✅ Suggestion yozildi:", f"chat_id - {chat_id},", f"message - {message}")
        except Exception as e:
            print("❌ Xato:", e)


# ------------------- HELPERS -------------------

def dict_fetchall(cursor):
    """Natijani list of dict sifatida qaytaradi"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def dict_fetchone(cursor):
    """Bitta natijani dict sifatida qaytaradi"""
    row = cursor.fetchone()
    if row is None:
        return False
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))