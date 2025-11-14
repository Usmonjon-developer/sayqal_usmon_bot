import logging
import os
import django
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

import methods
from database import Database
from register import check
from messages import message_handler
from inlines import inline_handler
import globals

# Django sozlamalarini yuklash
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Ma'lumotlar bazasi
db = Database("db-evos.db")

# Logger sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token va admin ID
load_dotenv()
TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ---------------- HANDLERLAR ----------------

def start_handler(update, context):
    """Boshlanish komandasi"""
    context.user_data["carts"] = {}
    check(update, context)
    logger.info(f"{update.effective_user.full_name} botdan foydalanishni boshladi!")


def order_status_handler(update, context):
    """Buyurtma holatini admin tomonidan o‘zgartirish"""
    query = update.callback_query
    data = query.data
    query.answer()

    order_id = int(data.split("_")[-1])
    status = data.split("_")[0]  # accept, cooking, delivering, delivered, cancel

    # Tugmalarni o‘chirib tashlash
    query.edit_reply_markup(reply_markup=None)

    if status == "cooking":
        query.message.reply_text("⏱ Buyurtma necha daqiqada tayyor bo‘lishini kiriting (masalan: 15):")
        context.user_data["waiting_for_time"] = order_id
        return

    # DBda statusni yangilash
    db.update_order_status(order_id, status)
    query.message.reply_text(f"✅ Buyurtma holati: {status.upper()}")

def contact_handler(update, context):
    """Foydalanuvchi kontakt yuborganda"""
    message = update.message.contact.phone_number
    user = update.message.from_user

    db.update_user_data(user.id, "phone_number", message)
    check(update, context)

    logger.info(f"{update.effective_user.full_name} botga kontaktini kiritdi: {message}")


def location_handler(update, context):
    """Buyurtmani yakunlash uchun joylashuvni qayta ishlash"""
    db_user = db.get_user_by_chat_id(update.message.from_user.id)
    location = update.message.location
    payment_type = context.user_data.get("payment_type", None)
    carts = context.user_data.get("carts", {})

    if not carts:
        update.message.reply_text("❌ Savatcha bo‘sh, buyurtma berish uchun mahsulot tanlang.")
        return

    # 🛒 Buyurtmani yaratish
    order_id = db.create_order(db_user['id'], carts, payment_type, location)
    lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]

    total_price = 0
    text = "📥 <b>Buyurtma:</b>\n"

    for idx, (cart, val) in enumerate(carts.items(), start=1):
        product = db.get_product_for_cart(int(cart))
        product_type = product.get("type", "").lower()
        product_name = product[f'name_{lang_code}']
        val_str = str(int(val)) if float(val).is_integer() else str(val)
        amount_str = f"{val_str} {product_type}" if product_type else f"{val_str}x"

        text += f"{idx}) {amount_str} × {product_name}\n"
        total_price += product['price'] * val

    text += f"\n<b>Jami:</b> {total_price} so'm"

    # To‘lov turi
    if payment_type == 1:
        payment_name = "Naqd pul"
    elif payment_type == 2:
        payment_name = "Karta"
    else:
        payment_name = "Noma’lum"

    # 🔘 Admin uchun tugmalar
    buttons = [
        [
            InlineKeyboardButton("✅ Qabul qilish", callback_data=f"accept_order_{order_id}"),
            InlineKeyboardButton("🍳 Tayyorlanyapti", callback_data=f"cooking_order_{order_id}")
        ],
        [
            InlineKeyboardButton("🚗 Yetkazilmoqda", callback_data=f"delivering_order_{order_id}"),
            InlineKeyboardButton("📦 Yetkazildi", callback_data=f"delivered_order_{order_id}")
        ],
        [
            InlineKeyboardButton("❌ Bekor qilish", callback_data=f"cancel_order_{order_id}")
        ]
    ]

    admin_text = (
        f"🆕 <b>Yangi buyurtma:</b>\n\n"
        f"👤 <b>Ism-familiya:</b> {db_user['first_name']}\n"
        f"👤 <b>Username:</b> @{update.effective_user.username or 'yo‘q'}\n"
        f"📞 <b>Telefon raqam:</b> {db_user['phone_number']}\n\n"
        f"📥 <b>To'lov turi:</b> {payment_name}\n\n"
        f"{text}\n\n"
        f"🆔 <b>Buyurtma ID:</b> {order_id}"
    )

    # 📨 Admin xabar
    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    # 📍 Joylashuv yuborish
    context.bot.send_location(
        chat_id=ADMIN_ID,
        latitude=float(location.latitude),
        longitude=float(location.longitude)
    )

    # 🔄 Statusni “pending” deb belgilash
    db.update_order_status(order_id, "pending")

    # ✅ Foydalanuvchiga tasdiq
    update.message.reply_text(globals.BOGLANISH[db_user["lang_id"]], parse_mode="HTML")
    methods.send_main_menu(context, update.message.from_user.id, db_user['lang_id'])

    context.user_data["carts"] = {}

    logger.info(f"{update.effective_user.full_name} buyurtma berdi: {text}")

def cook_time_handler(update, context):
    user_id = update.message.from_user.id
    text = update.message.text.strip().lower()

    cook_times = context.bot_data.get("cook_times", {})
    if user_id not in cook_times:
        return  # admin hozir cooking rejimda emas

    order_id = cook_times[user_id]["order_id"]
    user_chat_id = cook_times[user_id]["user_chat_id"]

    # --- Tahlil qilish ---
    if "h" in text or "soat" in text:
        # Soat kiritilgan
        time_str = text.replace("h", " soat").strip()
        user_msg = f"🍽 Buyurtmangiz taxminan {time_str}da tayyor bo‘ladi!"
    else:
        # Daqiqa kiritilgan (faqat raqam bo‘lsa)
        try:
            minutes = int(text)
            time_str = f"{minutes} min"
            user_msg = f"🍽 Buyurtmangiz taxminan {minutes} daqiqada tayyor bo‘ladi!"
        except ValueError:
            # Noto‘g‘ri formatda yozilgan bo‘lsa
            update.message.reply_text("❌ Iltimos, vaqtni to‘g‘ri kiriting (masalan: 30 yoki 1h)")
            return

    # Foydalanuvchiga yuborish
    context.bot.send_message(
        chat_id=user_chat_id,
        text=user_msg
    )

    # Admin uchun tasdiq
    update.message.reply_text(f"✅ Buyurtma #{order_id} uchun vaqt ({time_str}) yuborildi.")

    # Ma’lumotni tozalash
    del context.bot_data["cook_times"][user_id]

# ---------------- MAIN FUNKSIYA ----------------

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(MessageHandler(Filters.contact, contact_handler))
    dispatcher.add_handler(MessageHandler(Filters.location, location_handler))
    dispatcher.add_handler(CallbackQueryHandler(inline_handler))

    # 🔥 Admin “1h” yoki “30” deganda ishlaydigan maxsus handler
    dispatcher.add_handler(
        MessageHandler(
            Filters.text & Filters.regex(r'^\d+\s*(h|soat|m|min)?$') & Filters.user(user_id=ADMIN_ID),
            cook_time_handler
        )
    )

    # ⚠️ Bu eng oxirida turishi shart
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()