from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import methods
from database import Database
import globals
import os
from django.conf import settings
from dotenv import load_dotenv
import requests

db = Database("db-evos.db")

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID"))
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def inline_handler(update, context):
    query = update.callback_query
    data_sp = str(query.data).split("_")
    db_user = db.get_user_by_chat_id(query.message.chat_id)

    if not db_user:
        query.message.reply_text("❌ Siz ro'yxatdan o'tmagansiz. Iltimos, /start tugmasini bosing.")
        return

    if data_sp[0] == "category":
        if data_sp[1] == "product":
            if data_sp[2] == "back":
                query.message.delete()
                products = db.get_products_by_category(category_id=int(data_sp[3]))
                buttons = methods.send_product_buttons(products=products, lang_id=db_user["lang_id"])
                clicked_btn = db.get_category_parent(int(data_sp[3]))
                if clicked_btn and clicked_btn['parent_id']:
                    buttons.append([InlineKeyboardButton(
                        text="Back", callback_data=f"category_back_{clicked_btn['parent_id']}"
                    )])
                else:
                    buttons.append([InlineKeyboardButton(
                        text="Back", callback_data=f"category_back"
                    )])
                query.message.reply_text(
                    text=globals.TEXT_ORDER[db_user['lang_id']],
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=buttons,
                    )
                )
            else:
                if len(data_sp) == 4:
                    query.message.delete()
                    carts = context.user_data.get("carts", {})
                    try:
                        quantity = float(data_sp[3])
                    except ValueError:
                        quantity = 1
                    carts[f"{data_sp[2]}"] = carts.get(f"{data_sp[2]}", 0) + quantity
                    context.user_data["carts"] = carts

                    categories = db.get_categories_by_parent()
                    buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])
                    text = f"{globals.AT_KORZINKA[db_user['lang_id']]}:\n\n"
                    lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
                    total_price = 0
                    for cart, val in carts.items():
                        product = db.get_product_for_cart(int(cart))
                        product_type = (product.get("type") or "").lower()
                        if float(val).is_integer():
                            amount_str = f"{int(val)} {product_type} ×"
                        else:
                            amount_str = f"{val} {product_type} ×"
                        text += f"{amount_str} {product[f'name_{lang_code}']}\n"
                        total_price += product['price'] * val
                    text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price}"
                    buttons.append([InlineKeyboardButton(text=f"{globals.BTN_KORZINKA[db_user['lang_id']]}", callback_data="cart")])
                    query.message.reply_text(
                        text=text,
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=buttons,
                        )
                    )
                else:
                    product = db.get_product_by_id(int(data_sp[2]))
                    query.message.delete()
                    caption = f"{globals.TEXT_PRODUCT_PRICE[db_user['lang_id']]} " + str(product["price"]) + \
                              f"\n{globals.TEXT_PRODUCT_DESC[db_user['lang_id']]}" + \
                              product[f"description_{globals.LANGUAGE_CODE[db_user['lang_id']]}"]
                    if product.get("type") == "kg":
                        buttons = []
                        temp_row = []
                        for i in range(1, 10):
                            weight = round(i * 0.1, 1)
                            temp_row.append(
                                InlineKeyboardButton(
                                    text=f"{weight} kg",
                                    callback_data=f"category_product_{data_sp[2]}_{weight}"
                                )
                            )
                            if len(temp_row) == 3:
                                buttons.append(temp_row)
                                temp_row = []
                        if temp_row:
                            buttons.append(temp_row)
                        temp_row = []
                        for i in range(1, 10):
                            weight = i
                            temp_row.append(
                                InlineKeyboardButton(
                                    text=f"{weight} kg",
                                    callback_data=f"category_product_{data_sp[2]}_{weight}"
                                )
                            )
                            if len(temp_row) == 3:
                                buttons.append(temp_row)
                                temp_row = []
                        if temp_row:
                            buttons.append(temp_row)
                    elif product["type"] == "l":
                        buttons = []
                        temp_row = []
                        for i in range(1, 10):
                            liter = round(i * 0.1, 1)
                            temp_row.append(
                                InlineKeyboardButton(
                                    text=f"{liter} l",
                                    callback_data=f"category_product_{data_sp[2]}_{liter}"
                                )
                            )
                            if len(temp_row) == 3:
                                buttons.append(temp_row)
                                temp_row = []
                        if temp_row:
                            buttons.append(temp_row)
                        temp_row = []
                        for i in range(1, 5):
                            liter = i
                            temp_row.append(
                                InlineKeyboardButton(
                                    text=f"{liter} l",
                                    callback_data=f"category_product_{data_sp[2]}_{liter}"
                                )
                            )
                            if len(temp_row) == 3:
                                buttons.append(temp_row)
                                temp_row = []
                        if temp_row:
                            buttons.append(temp_row)
                    else:
                        buttons = [
                            [
                                InlineKeyboardButton(text="1️⃣", callback_data=f"category_product_{data_sp[2]}_{1}"),
                                InlineKeyboardButton(text="2️⃣", callback_data=f"category_product_{data_sp[2]}_{2}"),
                                InlineKeyboardButton(text="3️⃣", callback_data=f"category_product_{data_sp[2]}_{3}"),
                            ],
                            [
                                InlineKeyboardButton(text="4️⃣", callback_data=f"category_product_{data_sp[2]}_{4}"),
                                InlineKeyboardButton(text="5️⃣", callback_data=f"category_product_{data_sp[2]}_{5}"),
                                InlineKeyboardButton(text="6️⃣", callback_data=f"category_product_{data_sp[2]}_{6}"),
                            ],
                            [
                                InlineKeyboardButton(text="7️⃣", callback_data=f"category_product_{data_sp[2]}_{7}"),
                                InlineKeyboardButton(text="8️⃣", callback_data=f"category_product_{data_sp[2]}_{8}"),
                                InlineKeyboardButton(text="9️⃣", callback_data=f"category_product_{data_sp[2]}_{9}"),
                            ],
                            [InlineKeyboardButton(text="Back", callback_data=f"category_product_back_{product['category_id']}")]
                        ]
                    image_path = os.path.join(settings.MEDIA_ROOT, str(product['image']))
                    if os.path.exists(image_path):
                        query.message.reply_photo(
                            photo=open(image_path, "rb"),
                            caption=caption,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                        )
                    else:
                        query.message.reply_text("❌ Mahsulot rasmi topilmadi.")
        elif data_sp[1] == "back":
            if len(data_sp) == 3:
                parent_id = int(data_sp[2])
            else:
                parent_id = None
            categories = db.get_categories_by_parent(parent_id=parent_id)
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])
            if parent_id:
                clicked_btn = db.get_category_parent(parent_id)
                if clicked_btn and clicked_btn['parent_id']:
                    buttons.append([InlineKeyboardButton(
                        text="Back", callback_data=f"category_back_{clicked_btn['parent_id']}"
                    )])
                else:
                    buttons.append([InlineKeyboardButton(
                        text="Back", callback_data=f"category_back"
                    )])
            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )
        else:
            categories = db.get_categories_by_parent(parent_id=int(data_sp[1]))
            if categories:
                buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])
            else:
                products = db.get_products_by_category(category_id=int(data_sp[1]))
                buttons = methods.send_product_buttons(products=products, lang_id=db_user["lang_id"])
            clicked_btn = db.get_category_parent(int(data_sp[1]))
            if clicked_btn and clicked_btn['parent_id']:
                buttons.append([InlineKeyboardButton(
                    text="Back", callback_data=f"category_back_{clicked_btn['parent_id']}"
                )])
            else:
                buttons.append([InlineKeyboardButton(
                    text="Back", callback_data=f"category_back"
                )])
            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )

    elif data_sp[0] == "cart" and len(data_sp) > 1 and data_sp[1] == "edit":
        carts = context.user_data.get("carts", {})
        if not carts:
            query.message.reply_text("🛒 Savatchangiz bo‘sh!")
            return
        lang_code = globals.LANGUAGE_CODE[db_user["lang_id"]]
        text = "✏️ <b>Savatchani tahrirlash:</b>\n\n"
        buttons = []
        for cart_id, qty in carts.items():
            product = db.get_product_for_cart(int(cart_id))
            name = product[f"name_{lang_code}"]
            measure = product.get("type", "")  # masalan: 'kg', 'l', 'dona' va hokazo
            # Agar 'type' bo‘lsa, chiqsin, bo‘lmasa chiqmasin
            if measure:
                text += f"• {name} — {qty} {measure}\n"
            else:
                text += f"• {name} — {qty}x\n"
            buttons.append([
                InlineKeyboardButton(
                    text=f"❌ {name}",
                    callback_data=f"cart_remove_{cart_id}"
                )
            ])
        buttons.append([InlineKeyboardButton(text="⬅️ Ortga", callback_data="cart_back")])
        try:
            query.message.edit_text(
                text=text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            if "Message is not modified" not in str(e):
                print("⚠️ Inline edit_text xato:", e)

        # Mahsulotni o‘chirish uchun yangi shart
    elif data_sp[0] == "cart" and len(data_sp) > 1 and data_sp[1] == "remove":
        product_id = int(data_sp[2])
        carts = context.user_data.get("carts", {})

        if str(product_id) in carts:
            del carts[str(product_id)]
            context.user_data["carts"] = carts
            query.answer("🗑 Mahsulot savatchadan o‘chirildi.")

        # Agar savatcha bo‘sh bo‘lib qolsa
        if not carts:
            # Foydalanuvchining tilini aniqlaymiz
            lang_id = db_user["lang_id"]
            # Kategoriyalarni qayta olib chiqamiz
            categories = db.get_categories_by_parent()
            buttons = methods.send_category_buttons(categories=categories, lang_id=lang_id)

            # Xabarni o‘zgartiramiz
            query.message.edit_text(
                text=globals.TEXT_ORDER[lang_id],
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )
            return

        lang_code = globals.LANGUAGE_CODE[db_user["lang_id"]]
        text = "✏️ <b>Savatchani tahrirlash:</b>\n\n"
        buttons = []
        for cart_id, qty in carts.items():
            product = db.get_product_for_cart(int(cart_id))
            name = product[f"name_{lang_code}"]
            text += f"• {name} — {qty}x\n"
            buttons.append([
                InlineKeyboardButton(text=f"❌ {name}", callback_data=f"cart_remove_{cart_id}")
            ])

        buttons.append([InlineKeyboardButton(text="⬅️ Ortga", callback_data="cart_back")])

        query.message.edit_text(
            text=text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data_sp[0] == "cart":
        if len(data_sp) == 2 and data_sp[1] == "clear":
            context.user_data.pop("carts", None)
            categories = db.get_categories_by_parent()
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])
            text = globals.TEXT_ORDER[db_user['lang_id']]
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons,
                )
            )
        elif len(data_sp) == 2 and data_sp[1] == "back":
            categories = db.get_categories_by_parent()
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])
            if context.user_data.get("carts", {}):
                carts = context.user_data.get("carts")
                text = f"{globals.AT_KORZINKA[db_user['lang_id']]}:\n\n"
                lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]
                total_price = 0
                for cart, val in carts.items():
                    product = db.get_product_for_cart(int(cart))
                    product_type = product.get("type", "").lower()
                    if float(val).is_integer():
                        amount_str = f"{int(val)} {product_type} ×"
                    else:
                        amount_str = f"{val} {product_type} ×"
                    text += f"{amount_str} {product[f'name_{lang_code}']}\n"
                    total_price += product['price'] * val
                text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price}"
                context.user_data.get('cart_text', text)
                buttons.append([InlineKeyboardButton(text=globals.BTN_KORZINKA[db_user['lang_id']], callback_data="cart")])
            else:
                text = globals.TEXT_ORDER[db_user['lang_id']]
            query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons,
                )
            )
        else:
            buttons = [
                [
                    InlineKeyboardButton(text=f"{globals.GO_ZAKAZ[db_user['lang_id']]}", callback_data="order"),
                    InlineKeyboardButton(text=f"{globals.CLEAR_SAVAT[db_user['lang_id']]}", callback_data="cart_clear")
                ],
                [
                    InlineKeyboardButton(text=f"{globals.SAVATNI_TAHRIRLASH[db_user['lang_id']]}", callback_data="cart_edit")
                ],
                [InlineKeyboardButton(text=f"{globals.BACK[db_user['lang_id']]}", callback_data="cart_back")],
            ]
            try:
                query.message.edit_reply_markup(
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=buttons
                    )
                )
            except Exception as e:
                if "Message is not modified" not in str(e):
                    print("⚠️ Inline edit xato:", e)

    elif data_sp[0] == "order":
        if len(data_sp) > 1 and data_sp[1] == "payment":
            context.user_data['payment_type'] = int(data_sp[2])
            query.message.delete()
            query.message.reply_text(
                text=globals.SEND_LOCATION[db_user["lang_id"]],
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton(text=globals.SEND_LOCATION[db_user["lang_id"]], request_location=True)]],
                    resize_keyboard=True
                )
            )
        else:
            query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(text=f"{globals.PY_TYPE1[db_user['lang_id']]}", callback_data="order_payment_1"),
                        InlineKeyboardButton(text=f"{globals.PY_TYPE2[db_user['lang_id']]}", callback_data="order_payment_2"),
                    ]]
                )
            )

    elif data_sp[0] in ["accept", "cancel", "cooking", "delivering", "delivered"] and data_sp[1] == "order":
        order_id = int(data_sp[-1])
        order = db.get_order_by_id(order_id)
        if not order:
            query.answer("❌ Buyurtma topilmadi.", show_alert=True)
            return

        user = db.get_user_by_id(order['user_id'])
        lang_id = db_user["lang_id"]

        status_texts_admin = {
            "accept": "✅ Qabul qilindi",
            "cooking": "🍳 Tayyorlanyapti",
            "delivering": "🚗 Yetkazilmoqda",
            "delivered": "📦 Yetkazildi",
            "cancel": "❌ Bekor qilindi"
        }

        status_texts_user = {
            "accept": "✅ Buyurtmangiz qabul qilindi!",
            "cooking": "🍳 Buyurtmangiz tayyorlanyapti!",
            "delivering": "",
            "delivered": "📦 Buyurtmangiz yetkazildi!",
            "cancel": "❌ Buyurtmangiz bekor qilindi."
        }

        status_map = {
            "accept": "accepted",
            "cooking": "cooking",
            "delivering": "delivering",
            "delivered": "delivered",
            "cancel": "cancelled"
        }

        db.update_order_status(order_id, status_map[data_sp[0]])

        # 🚗 Agar status "delivering" bo'lsa — foydalanuvchiga ETA yuborish
        if data_sp[0] == "delivering":
            try:
                # Restoran koordinatalari (Buxoro, Gazli shoh ko'chasi 121)
                origin = "39.773563,64.400672"
                # Foydalanuvchi joylashuvi DBda saqlangan
                user_lat = order["latitude"]
                user_lng = order["longitude"]
                dest = f"{user_lat},{user_lng}"

                r = requests.get(
                    "https://maps.googleapis.com/maps/api/directions/json",
                    params={
                        "origin": origin,
                        "destination": dest,
                        "mode": "driving",
                        "departure_time": "now",
                        "key": GOOGLE_API_KEY
                    }
                )
                data = r.json()
                eta = data["routes"][0]["legs"][0]["duration_in_traffic"]["text"]

                # Foydalanuvchiga ETA yuborish
                context.bot.send_message(
                    chat_id=user["chat_id"],
                    text=f"🚗 Buyurtmangiz yo‘lda! Taxminiy yetkazish vaqti: {eta}"
                )

            except Exception as e:
                print("ETA hisoblashda xato:", e)
                context.bot.send_message(
                    chat_id=user["chat_id"],
                    text="🚗 Buyurtmangiz yo‘lda! Yetkazish vaqti aniqlanmoqda..."
                )


        # -------------- AGAR "cooking" bo‘lsa vaqt so‘rash --------------
        if data_sp[0] == "cooking":
            query.answer()

            # Tugmalar: vaqt yozish yoki "Allaqachon tayyor ✅"
            buttons = [
                [InlineKeyboardButton("✅ Allaqachon tayyor", callback_data=f"ready_now_{order_id}")]
            ]

            context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"⏰ Buyurtma #{order_id} necha daqiqada tayyor bo‘ladi? (masalan: 30 yoki 1h)",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

            # Admin yozadigan vaqtni vaqtinchalik saqlaymiz
            if "cook_times" not in context.bot_data:
                context.bot_data["cook_times"] = {}
            context.bot_data["cook_times"][query.from_user.id] = {
                "order_id": order_id,
                "user_chat_id": user["chat_id"]
            }
            return
        # ---------------------------------------------------------------

        if user:
            context.bot.send_message(
                chat_id=user['chat_id'],
                text=status_texts_user[data_sp[0]]
            )
    # 🔽 Allaqachon tayyor tugmasi uchun alohida shart
    elif query.data.startswith("ready_now_"):
        query.answer()  # callback'ni javobsiz qoldirmaslik uchun
        # oxirgi qismidan order_id olamiz
        order_id = int(query.data.split("_")[-1])
        order = db.get_order_by_id(order_id)
        if not order:
            query.answer("❌ Buyurtma topilmadi.", show_alert=True)
            return
        user = db.get_user_by_id(order["user_id"])
        # Foydalanuvchiga xabar
        context.bot.send_message(
            chat_id=user["chat_id"],
            text="🍽 Buyurtmangiz allaqachon tayyor!"
        )
        # Admin uchun tasdiq (inline xabarni o'zgartirish)
        try:
            query.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        query.message.reply_text(f"✅ Buyurtma #{order_id} allaqachon tayyor deb belgilandi.")
        # DB holatini yangilash (agar kerak bo'lsa)
        try:
            db.update_order_status(order_id, "ready")
        except Exception:
            pass
        return