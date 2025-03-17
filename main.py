from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
from flask import Flask
import threading

# Token de tu bot de Telegram
TELEGRAM_BOT_TOKEN = '7872010028:AAGial5BjOzxa_Bx_tZw00uzqvcmEYqOFxU'

# URL de la API para obtener el valor del dólar según el BCV
API_URL = "https://pydolarve.org/api/v1/dollar?page=bcv&monitor=usd&format_date=default&rounded_price=true"

# Configuración del servidor Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "¡El bot de Telegram está activo! �"

# Función para obtener el valor actual del dólar según el BCV
def get_dollar_price():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Lanza una excepción si la solicitud no fue exitosa
        data = response.json()

        # Verifica si la respuesta contiene el campo 'price'
        if 'price' in data:
            return data['price']
        else:
            print("Estructura de la respuesta inesperada:", data)  # Depuración
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la solicitud a la API: {e}")  # Depuración
        return None

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        '¡Hola! 👋 Soy un bot que te ayuda con cálculos de dólares. 💵\n\n'
        'Envíame un monto en dólares (que ya incluye el 16% de IVA) usando el comando /C <monto>.'
    )

# Comando /C
async def C(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Obtener el monto del mensaje
        amount_with_iva = float(update.message.text.split()[1])

        # Obtener el valor actual del dólar según el BCV
        dollar_price = get_dollar_price()
        if dollar_price is None:
            await update.message.reply_text("❌ No se pudo obtener el valor del dólar. Intenta más tarde.")
            return

        # Calcular el monto sin IVA (el monto con IVA es el 116% del monto sin IVA)
        amount_without_iva = amount_with_iva / 1.16

        # Calcular el IVA (16% del monto sin IVA)
        iva = amount_without_iva * 0.16

        # Convertir ambos montos a bolívares (multiplicando por el valor del dólar)
        price_without_iva_bs = amount_without_iva * dollar_price
        price_with_iva_bs = amount_with_iva * dollar_price
        iva_bs = iva * dollar_price

        # Responder al usuario con los cálculos en el formato solicitado
        response_message = (
            "💵 **Monto ingresado (con IVA):** "
            f"${amount_with_iva:.2f}\n\n"
            "📉 **Precio en Bs (sin IVA):** "
            f"{price_without_iva_bs:.2f}bs\n"
            "🧾 **IVA:** "
            f"{iva_bs:.2f}bs\n"
            "📈 **Precio en Bs (con IVA):** "
            f"{price_with_iva_bs:.2f}bs\n\n"
            "🏦 **Tasa del dólar BCV:** "
            f"{dollar_price:.2f}bs"
        )
        await update.message.reply_text(response_message, parse_mode="Markdown")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Por favor, envía un monto válido. Ejemplo: /C 100")

# Comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "ℹ️ **Puedes interactuar conmigo usando los siguientes comandos:**\n\n"
        "👉 /start - Iniciar el bot\n"
        "👉 /C <monto> - Calcular el monto sin IVA y convertirlo a bolívares\n"
        "👉 /help - Mostrar esta ayuda"
    )

# Función para iniciar el bot de Telegram
def run_bot():
    # Crea la aplicación y pasa el token de tu bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Registra los comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("C", C))
    application.add_handler(CommandHandler("help", help_command))

    # Inicia el bot
    application.run_polling()

# Función para iniciar el servidor Flask
def run_flask():
    app.run(host='0.0.0.0', port=10000)

if __name__ == "__main__":
    # Inicia el servidor Flask en un hilo separado
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Inicia el bot de Telegram
    run_bot()
