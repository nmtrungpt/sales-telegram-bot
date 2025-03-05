import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

class SalesBot:
    def __init__(self, telegram_token, google_sheet_key):
        # Cấu hình Google Sheet từ biến môi trường
        try:
            credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
            credentials_dict = json.loads(credentials_json)
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
            client = gspread.authorize(creds)
            self.sheet = client.open_by_key(google_sheet_key).sheet1
        except Exception as e:
            print(f"Lỗi khi tải thông tin xác thực Google Sheets: {e}")
            self.sheet = None  # Xử lý khi không thể kết nối Google Sheets

        # Telegram Bot Token
        self.telegram_token = telegram_token

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🛍️ Bot Quản Lý Doanh Thu 🛍️\n\n"
            "Nhập thông tin bán hàng theo định dạng:\n"
            "Tên Sản Phẩm, Số Lượng, Đơn Giá, Tổng Tiền\n\n"
            "VD: Áo Thun, 10, 50000, 500000"
        )

    async def add_sale(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.sheet is None:  # Kiểm tra kết nối Google Sheets
            await update.message.reply_text("❌ Lỗi: Không thể kết nối Google Sheets.")
            return

        try:
            sale_data = update.message.text.split(',')

            if len(sale_data) < 4:
                await update.message.reply_text("❌ Sai định dạng. Vui lòng thử lại!")
                return

            product_name = sale_data[0].strip()
            quantity = sale_data[1].strip()
            unit_price = sale_data[2].strip()
            total_revenue = sale_data[3].strip()

            current_date = datetime.now().strftime("%d/%m/%Y")

            row_data = [
                current_date,
                product_name,
                quantity,
                unit_price,
                total_revenue
            ]

            self.sheet.append_row(row_data)

            await update.message.reply_text(
                f"✅ Đã lưu dữ liệu:\n"
                f"Sản phẩm: {product_name}\n"
                f"Số lượng: {quantity}\n"
                f"Tổng tiền: {total_revenue} VND"
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Lỗi: {str(e)}")

    def run(self):
        app = Application.builder().token(self.telegram_token).build()

        app.add_handler(CommandHandler('start', self.start))
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.add_sale
        ))

        print("Bot đang chạy...")
        return app

# Khởi động bot
def main():
    bot_token = '7188961280:AAFQSROsjF3IrTz9Olr5RjqGX7hf7sCl6Dg'
    sheet_key = '1RGckiwZe7jOSKP28zSfJYWDsh58ZjrJ0VEdmk77KfCI'

    sales_bot = SalesBot(bot_token, sheet_key)
    app = sales_bot.run()
    app.run_polling()

if __name__ == '__main__':
    main()