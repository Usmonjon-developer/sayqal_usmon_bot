import logging

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler

import methods
from database import Database
from register import check
from dotenv import load_dotenv
from messages import message_handler
from inlines import inline_handler
import globals
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

db = Database("db-evos.db")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))


def start_handler(update, context):
    check(update, context)
    logger.info(f"{update.effective_user.full_name} botdan foydalanishni boshladi!")


def contact_handler(update, context):
    message = update.message.contact.phone_number
    user = update.message.from_user
    db.update_user_data(user.id, "phone_number",message)
    check(update,context)
    logger.info(f"{update.effective_user.full_name} botga kontaktini kiritdi: {message}")

def location_handler(update, context):
    db_user = db.get_user_by_chat_id(update.message.from_user.id)
    location = update.message.location
    payment_type = context.user_data.get("payment_type", None)
    db.create_order(db_user['id'], context.user_data.get("carts", {}), payment_type, location)

    if context.user_data.get("carts", {}):
        carts = context.user_data.get("carts")
        text = "\n"
        lang_code = globals.LANGUAGE_CODE[1]
        total_price = 0
        for cart, val in carts.items():
            product = db.get_product_for_cart(int(cart))
            text += f"{val}x {product[f'name_{lang_code}']}\n"
            total_price += product['price'] * val

        text += f"\n{globals.ALL[1]}: {total_price} {globals.SUM[1]}"

    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"<b>Yangi buyurtma:</b>\n\n"
             f"👤 <b>Ism-familiya:</b> {db_user['first_name']}\n"
             f"👤 <b>Username:</b> @{update.effective_user.username or 'yo‘q'}\n"
             f"📞 <b>Telefon raqam:</b> {db_user['phone_number']} \n\n"
             f"<i>Agar to'lov turi 1 bo'lsa, buyurtma naqd pul orqali to'lanadi, agar 2 bo'lsa buyurtma karta orqali to'lanadi!</i>\n\n"
             f"📥 <b>To'lov turi:</b> {payment_type}\n\n"
             f"📥 <b>Buyurtma:</b> \n"
             f"{text}",
        parse_mode='HTML'
    )


    context.bot.send_location(
        chat_id=ADMIN_ID,
        latitude=float(location.latitude),
        longitude=float(location.longitude)
    )
    methods.send_main_menu(context, update.message.from_user.id, db_user['lang_id'])
    logger.info(f"{update.effective_user.full_name} botdan zakaz qildi: {text}")

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    dispatcher.add_handler(MessageHandler(Filters.contact, contact_handler))
    dispatcher.add_handler(CallbackQueryHandler(inline_handler))
    dispatcher.add_handler(MessageHandler(Filters.location, location_handler))


    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()