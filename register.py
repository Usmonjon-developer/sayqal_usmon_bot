from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from database import Database
import globals
import methods

db = Database("db-evos.db")


def check(update, context):
    user = update.message.from_user
    db_user = db.get_user_by_chat_id(user.id)

    # Agar user bazada yo'q bo‘lsa — yangi user yaratish
    if not db_user:
        db.create_user(user.id)
        buttons = [
            [
                KeyboardButton(text=globals.BTN_LANG_UZ),
                KeyboardButton(text=globals.BTN_LANG_RU),
                KeyboardButton(text=globals.BTN_LANG_EN),
            ]
        ]
        update.message.reply_text(text=globals.WELCOME_TEXT)
        update.message.reply_text(
            text=globals.CHOOSE_LANG,
            reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        )
        context.user_data["state"] = globals.STATES["reg"]
        return

    # Agar til hali tanlanmagan bo‘lsa
    if not db_user["lang_id"]:
        buttons = [
            [
                KeyboardButton(text=globals.BTN_LANG_UZ),
                KeyboardButton(text=globals.BTN_LANG_RU),
                KeyboardButton(text=globals.BTN_LANG_EN),
            ]
        ]
        update.message.reply_text(
            text=globals.CHOOSE_LANG,
            reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        )
        context.user_data["state"] = globals.STATES["reg"]

    # Agar ism hali kiritilmagan bo‘lsa
    elif not db_user["first_name"]:
        update.message.reply_text(
            text=globals.TEXT_ENTER_FIRST_NAME[db_user["lang_id"]],
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data["state"] = globals.STATES["reg"]

    # Agar telefon hali kiritilmagan bo‘lsa
    elif not db_user["phone_number"]:
        buttons = [
            [KeyboardButton(text=globals.BTN_SEND_CONTACT[db_user["lang_id"]], request_contact=True)]
        ]
        update.message.reply_text(
            text=globals.TEXT_ENTER_CONTACT[db_user["lang_id"]],
            reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True),
        )
        context.user_data["state"] = globals.STATES["reg"]

    # Aks holda — asosiy menyuga o‘tkazish
    else:
        methods.send_main_menu(context, user.id, db_user["lang_id"])
        context.user_data["state"] = globals.STATES["admin_site"]



def check_data_decorator(func):
    def inner(update, context):
        user = update.message.from_user
        db_user = db.get_user_by_chat_id(user.id)
        state = context.user_data.get("state", 0)
        text = update.message.text

        # Faqat ro‘yxatdan o‘tish paytida tekshirish
        if state == globals.STATES["reg"]:
            # Til tanlash
            if not db_user["lang_id"]:
                if text not in [
                    globals.BTN_LANG_UZ,
                    globals.BTN_LANG_RU,
                    globals.BTN_LANG_EN,
                ]:
                    update.message.reply_text(globals.TEXT_LANG_WARNING)
                    return False

            # Ism tekshiruvi
            elif not db_user["first_name"]:
                if not text.isalpha():  # faqat harflar bo‘lishi kerak
                    update.message.reply_text(globals.TEXT_ENTER_FIRST_NAME[db_user["lang_id"]])
                    return False

            # Telefon tekshiruvi
            elif not db_user["phone_number"]:
                if not update.message.contact:
                    update.message.reply_text(globals.TEXT_ENTER_CONTACT[db_user["lang_id"]])
                    return False

            return func(update, context)

        # Agar ro‘yxatdan o‘tgan bo‘lsa
        else:
            if not db_user or not db_user["lang_id"] or not db_user["first_name"] or not db_user["phone_number"]:
                return check(update, context)
            else:
                return func(update, context)

    return inner