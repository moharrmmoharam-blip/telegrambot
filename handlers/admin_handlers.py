from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import OWNER_ID
from menus import show_admins_menu


class AdminHandlers:

    def __init__(self, db):
        self.db = db

    # ==================================================
    # SHOW ADMINS
    # ==================================================

    async def show_admins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        query = update.callback_query
        await query.answer()

        admins = self.db.get_admins()

        if not admins:
            await query.edit_message_text(
                "❌ لا يوجد مشرفين",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 رجوع", callback_data="back_admins")]
                ])
            )
            return

        text = "👨‍💼 المشرفين:\n\n"
        keyboard = []

        for admin in admins:
            admin_id, username, role, active, added = admin

            status = "✅ نشط" if active == 1 else "⛔ معطل"
            owner_tag = "👑" if admin_id == OWNER_ID else ""

            text += f"{owner_tag} {admin_id} — {role}\n"
            text += f"{status}\n"
            text += f"{added}\n\n"

            # لا يمكن حذف المالك
            if admin_id != OWNER_ID:
                keyboard.append([
                    InlineKeyboardButton(
                        "🗑 حذف",
                        callback_data=f"delete_admin_{admin_id}"
                    )
                ])

        keyboard.append(
            [InlineKeyboardButton("🔙 رجوع", callback_data="back_admins")]
        )

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ==================================================
    # DELETE ADMIN (OWNER ONLY)
    # ==================================================

    async def delete_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE, admin_id: int):

        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id

        # 🔒 المالك فقط
        if user_id != OWNER_ID:
            await query.answer("❌ هذه العملية للمالك فقط", show_alert=True)
            return

        # حماية المالك
        if admin_id == OWNER_ID:
            await query.answer("❌ لا يمكن حذف المالك", show_alert=True)
            return

        self.db.delete_admin(admin_id)
        await self.show_admins(update, context)
