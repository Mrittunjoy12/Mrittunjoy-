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
    app.run_polling()PK     *H�Z��@�\  \     admin_panel.pyfrom flask import Flask, request, render_template_string, redirect
import sqlite3

app = Flask(__name__)

ADMIN_PASSWORD = "tagarA11"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            return redirect("/dashboard")
    return '''
        <form method="post">
            <input name="password" type="password" placeholder="Admin Password">
            <button type="submit">Login</button>
        </form>
    '''

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id, email, verified FROM users")
    rows = cursor.fetchall()
    conn.close()

    html = "<h2>Registered Users</h2><table border=1><tr><th>Telegram ID</th><th>Email</th><th>Verified</th></tr>"
    for row in rows:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{'✅' if row[2] else '❌'}</td></tr>"
    html += "</table>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)PK     *H�Z�}o&   &      requirements.txtpython-telegram-bot==20.3
Flask==2.3.2PK     *H�Z2�V�   �      render.yamlservices:
  - type: web
    name: telegram-admin-panel
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python admin_panel.py"
    plan: free
    envVars:
      - key: PORT
        value: 10000PK     *H�Z�᳭�  �             ��    bot.pyPK     *H�Z��@�\  \             ���  admin_panel.pyPK     *H�Z�}o&   &              ��g  requirements.txtPK     *H�Z2�V�   �              ���  render.yamlPK      �   �    