import methods
from register import check, check_data_decorator
from database import Database
import globals
from telegram import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import os
from dotenv import load_dotenv

db = Database("db-evos.db")

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))


@check_data_decorator
def message_handler(update, context):
    message = update.message.text
    user = update.message.from_user
    state = context.user_data.get("state", 0)
    db_user = db.get_user_by_chat_id(user.id)

    if state == 0:
        check(update, context)
        return None

    elif state == 1:
        # Til tanlanmagan bo‘lsa
        if not db_user["lang_id"]:
            if message == globals.BTN_LANG_UZ:
                db.update_user_data(user.id, "lang_id", 1)
            elif message == globals.BTN_LANG_RU:
                db.update_user_data(user.id, "lang_id", 2)
            elif message == globals.BTN_LANG_EN:
                db.update_user_data(user.id, "lang_id", 3)
            else:
                return update.message.reply_text(globals.TEXT_LANG_WARNING)
            check(update, context)
            return None

        # Ism kiritilmagan bo‘lsa
        elif not db_user["first_name"]:
            db.update_user_data(user.id, "first_name", message)
            buttons = [
                [KeyboardButton(text=globals.BTN_SEND_CONTACT[db_user['lang_id']], request_contact=True)]
            ]
            update.message.reply_text(
                text=globals.TEXT_ENTER_CONTACT[db_user['lang_id']],
                reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            )
            return None

        # Telefon raqam kiritilmagan bo‘lsa
        elif not db_user["phone_number"]:
            db.update_user_data(user.id, "phone_number", message)
            check(update, context)
            return None

        else:
            check(update, context)
            return None

    elif state == 2:
        # 🛍 Buyurtma berish
        if message == globals.BTN_ORDER[db_user['lang_id']]:
            categories = db.get_categories_by_parent()
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])

            carts = context.user_data.get("carts", {})
            if carts:
                text = f"{globals.AT_KORZINKA[db_user['lang_id']]}:\n\n"
                lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
                total_price = 0
                for cart_id, amount in carts.items():
                    product = db.get_product_for_cart(int(cart_id))
                    text += f"{amount}x {product[f'cat_name_{lang_code}']}\n"
                    total_price += product['price'] * amount

                text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price:,} so'm"
                buttons.append([InlineKeyboardButton(text=globals.BTN_KORZINKA[db_user['lang_id']], callback_data="cart")])
            else:
                text = globals.TEXT_ORDER[db_user['lang_id']]

            update.message.reply_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return None

        # 📦 Mening buyurtmalarim
        elif message == globals.BTN_MY_ORDERS[db_user['lang_id']]:
            orders = db.get_user_active_orders(db_user["id"])

            if not orders:
                return update.message.reply_text(globals.NO_ZAKAZ[db_user['lang_id']])

            lang_id = db_user["lang_id"]
            first_name = db_user.get("first_name", "")
            phone = db_user.get("phone_number", "")

            status_texts = {
                "pending": {1: "🕓 Kutilmoqda", 2: "🕓 Ожидается", 3: "🕓 Pending"},
                "accepted": {1: "✅ Qabul qilindi", 2: "✅ Принято", 3: "✅ Accepted"},
                "cooking": {1: "🍳 Tayyorlanyapti", 2: "🍳 Готовится", 3: "🍳 Cooking"},
                "delivering": {1: "🚗 Yetkazilmoqda", 2: "🚗 Доставляется", 3: "🚗 Delivering"},
                "delivered": {1: "📦 Yetkazildi", 2: "📦 Доставлено", 3: "📦 Delivered"},
                "cancelled": {1: "❌ Bekor qilindi", 2: "❌ Отменено", 3: "❌ Cancelled"},
                "ready": {1: "🍽 Tayyor", 2: "🍽 Готов", 3: "🍽 Ready"}
            }

            text = (
                f"📋 <b>Ma'lumotlarim:</b>\n"
                f"👤 <b>Ism:</b> {first_name}\n"
                f"📞 <b>Telefon:</b> {phone}\n\n"
                f"📦 <b>Buyurtmalar ro‘yxati:</b>\n\n"
            )

            seen_orders = set()
            for order in orders:
                order_id = order["id"]
                if order_id in seen_orders:
                    continue
                seen_orders.add(order_id)

                order_products = db.get_order_products(order_id)
                total_price = 0
                order_lines = ""
                for op in order_products:
                    if op["amount"] <= 0:
                        continue
                    name = (
                        op["product_name_uz"] if lang_id == 1 else
                        op["product_name_ru"] if lang_id == 2 else
                        op["product_name_en"]
                    )
                    total_price += op["product_price"] * op["amount"]
                    order_lines += f"🍽 {name} — {op['amount']} × {op['product_price']:,} so'm\n"

                status = status_texts.get(order["status"], {}).get(lang_id, "❔ Noma’lum")
                order_time = order.get("created_at", "—")

                text += (
                    f"🆔 <b>Buyurtma #{order_id}</b>\n"
                    f"📅 <b>Sana:</b> {order_time}\n"
                    f"{order_lines}"
                    f"💰 <b>Jami:</b> {total_price:,} so'm\n"
                    f"📋 <b>Holati:</b> {status}\n\n"
                )

            update.message.reply_text(text, parse_mode='HTML')

        # ℹ️ Biz haqimizda
        elif message == globals.BTN_ABOUT_US[db_user['lang_id']]:
            update.message.reply_text(
                text=globals.ABOUT_COMPANY[db_user['lang_id']],
                parse_mode="HTML"
            )
            return None

        # 🏠 Zal haqida
        elif message == globals.ZAL[db_user['lang_id']]:
            update.message.reply_text(
                text=globals.ZAL_MATNI[db_user['lang_id']],
                parse_mode="HTML"
            )
            return None

        # ⚙️ Sozlamalar
        elif message == globals.BTN_SETTINGS[db_user['lang_id']]:
            buttons = [
                [KeyboardButton(text=globals.BTN_LANG_UZ),
                 KeyboardButton(text=globals.BTN_LANG_RU),
                 KeyboardButton(text=globals.BTN_LANG_EN)]
            ]
            update.message.reply_text(
                text=globals.CHOOSE_LANG,
                reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            )
            context.user_data["state"] = globals.STATES["settings"]
            return None

        # ✍️ Fikr bildirish
        elif message == globals.BTN_COMMENTS[db_user['lang_id']]:
            update.message.reply_text(globals.YOZING[db_user['lang_id']])
            context.user_data["state"] = "feedback"
            return None
        return None

    # 📝 Fikrlarni admin'ga yuborish
    elif state == "feedback":
        text = update.message.text
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"<b>Yangi fikr:</b>\n\n"
                f"👤 <b>Ism:</b> {db_user['first_name']}\n"
                f"📞 <b>Telefon:</b> {db_user['phone_number']}\n\n"
                f"💬 <b>Fikr:</b> {text}"
            ),
            parse_mode='HTML'
        )

        update.message.reply_text(globals.RAHMAT[db_user['lang_id']])
        db.create_suggestion(chat_id=update.message.chat_id, message=text)
        context.user_data["state"] = globals.STATES["admin_site"]
        return None

    # ⚙️ Til sozlamalari
    elif state == 3:
        if message == globals.BTN_LANG_UZ:
            db.update_user_data(db_user['chat_id'], "lang_id", 1)
        elif message == globals.BTN_LANG_RU:
            db.update_user_data(db_user['chat_id'], "lang_id", 2)
        elif message == globals.BTN_LANG_EN:
            db.update_user_data(db_user['chat_id'], "lang_id", 3)
        else:
            return update.message.reply_text(globals.TEXT_LANG_WARNING)

        context.user_data["state"] = globals.STATES["reg"]
        check(update, context)
        return None

    else:
        update.message.reply_text("Assalomu alaykum!")
        return None