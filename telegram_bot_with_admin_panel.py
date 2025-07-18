PK     *H�Z�᳭�  �     bot.pyimport logging
import random
import smtplib
import string
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# Config
TOKEN = "7699490123:AAE7jD59d0jYgfbLa0ixP3EfXEXtjPuhbGQ"
SMTP_EMAIL = "freelancingzone.office@gmail.com"
SMTP_PASSWORD = "apes mcdm wxhl xvbe"
ADMIN_USER_ID = 7352578881
REFERRAL_LINK_TEMPLATE = "https://t.me/yourbot?start={}"  # Change 'yourbot' to actual bot username

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Database Setup
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    email TEXT UNIQUE,
    code TEXT,
    verified INTEGER DEFAULT 0,
    referred_by INTEGER
)''')
conn.commit()

# States
EMAIL, VERIFY, MAIN_MENU = range(3)

# Helper: Send verification code
def send_verification_email(email, code):
    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = email
    msg['Subject'] = "Your Verification Code"

    body = f"Your code is: {code}"
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, email, msg.as_string())

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    telegram_id = user.id

    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user_data = cursor.fetchone()

    if user_data and user_data[4] == 1:
        await update.message.reply_text("You are already registered and verified!", reply_markup=main_menu_keyboard())
        return MAIN_MENU
    else:
        await update.message.reply_text("Welcome! Please enter your email address:")
        return EMAIL

# Email input
async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    telegram_id = update.message.from_user.id

    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        await update.message.reply_text("This email is already registered.")
        return ConversationHandler.END

    code = ''.join(random.choices(string.digits, k=6))
    send_verification_email(email, code)

    context.user_data['email'] = email
    context.user_data['code'] = code

    cursor.execute("INSERT OR REPLACE INTO users (telegram_id, email, code) VALUES (?, ?, ?)", (telegram_id, email, code))
    conn.commit()

    await update.message.reply_text(f"A 6-digit code has been sent to {email}. Please enter it:")
    return VERIFY

# Code verify
async def verify_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entered_code = update.message.text
    telegram_id = update.message.from_user.id

    cursor.execute("SELECT code FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cursor.fetchone()
    if row and entered_code == row[0]:
        cursor.execute("UPDATE users SET verified = 1 WHERE telegram_id = ?", (telegram_id,))
        conn.commit()
        await update.message.reply_text("✅ Verification successful!

🔗 Here's your work bot link: https://t.me/your_work_bot", reply_markup=main_menu_keyboard())
        return MAIN_MENU
    else:
        await update.message.reply_text("❌ Invalid code. Please try again.")
        return VERIFY

# Menu handler
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Main menu:", reply_markup=main_menu_keyboard())
    return MAIN_MENU

# Logout handler
async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    cursor.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    await update.message.reply_text("You have been logged out. /start to register again.")
    return ConversationHandler.END

# Main menu keyboard
def main_menu_keyboard():
    keyboard = [["Refer", "Logout"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Refer handler
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    link = REFERRAL_LINK_TEMPLATE.format(telegram_id)
    await update.message.reply_text(f"🔗 Your referral link:
{link}")

# Bot setup
app = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        VERIFY: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_code)],
        MAIN_MENU: [
            MessageHandler(filters.Regex("^(Refer)$"), refer),
            MessageHandler(filters.Regex("^(Logout)$"), logout),
            MessageHandler(filters.TEXT & ~filters.COMMAND, menu),
        ],
    },
    fallbacks=[CommandHandler("start", start)],
)

app.add_handler(conv_handler)

if __name__ == "__main__":
    app.run_polling()PK     mJ�Z�nm       admin_panel.pyfrom flask import Flask, render_template
app = Flask(__name__)

users = {
    "7352578881": "freelancingzone.office@gmail.com"
}

@app.route("/")
def index():
    return render_template("admin.html", users=users)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)PK     mJ�Z�}o&   &      requirements.txtpython-telegram-bot==20.3
Flask==2.3.2PK     *H�Z2�V�   �      render.yamlservices:
  - type: web
    name: telegram-admin-panel
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python admin_panel.py"
    plan: free
    envVars:
      - key: PORT
        value: 10000PK     mJ�Z�奈@  @     main.pyfrom telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import smtplib
import random
import string

TOKEN = "YOUR_BOT_TOKEN"
VERIFICATION_CODES = {}
REGISTERED_USERS = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Please enter your email address to register.")

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if email in REGISTERED_USERS.values():
        await update.message.reply_text("This email is already registered.")
        return
    code = ''.join(random.choices(string.digits, k=6))
    VERIFICATION_CODES[update.message.chat_id] = {"email": email, "code": code}
    send_email(email, code)
    await update.message.reply_text("Verification code sent to your email. Please reply with the code.")

async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    user_data = VERIFICATION_CODES.get(update.message.chat_id)
    if user_data and user_input == user_data["code"]:
        REGISTERED_USERS[update.message.chat_id] = user_data["email"]
        await update.message.reply_text("Registration successful!")
    else:
        await update.message.reply_text("Invalid code. Try again.")

def send_email(to_email, code):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("freelancingzone.office@gmail.com", "apes mcdm wxhl xvbe")
    subject = "Your Verification Code"
    message = f"Your code is {code}"
    server.sendmail("freelancingzone.office@gmail.com", to_email, f"Subject: {subject}\n\n{message}")
    server.quit()

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))
    app.run_polling()

if __name__ == "__main__":
    main()PK     mJ�Z#�,!  !     templates/admin.html<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Admin Panel</title>
</head>
<body>
  <h1>Registered Users</h1>
  <ul>
    {% for user_id, email in users.items() %}
      <li><strong>{{ user_id }}</strong>: {{ email }}</li>
    {% endfor %}
  </ul>
</body>
</html>PK     *H�Z�᳭�  �             ��    bot.pyPK     mJ�Z�nm               ���  admin_panel.pyPK     mJ�Z�}o&   &              ��"  requirements.txtPK     *H�Z2�V�   �              ��v  render.yamlPK     mJ�Z�奈@  @             ���  main.pyPK     mJ�Z#�,!  !             ���  templates/admin.htmlPK      ^  >!    