import os
import sys
import logging
from datetime import datetime
from weather_grabber import WeatherGrabber24, WeatherGrabber2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler,MessageHandler, filters

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
WEATHER_EMOJI = {
    "Thundery Showers": "⛈️",
    "Cloudy": "☁️",
    "Partly Cloudy (Day)": "🌤️",
    "Partly Cloudy (Night)": "🌃",
    "Fair (Day)": "🌞",
    "Fair (Night)": "🌙",
    "Light Rain": "🌦️",
    "Moderate Rain": "🌧️",
    "Heavy Rain": "🌧️",
    "Showers": "🌦️",
    "Hazy": "😶‍🌫️",
    "Windy": "💨"
}

REGION_SELECTED = 0

class WeatherBot:
    def __init__(self,token):
        self.token = token
        self.weather_24 = WeatherGrabber24()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        inline_keyboard = [
            [
         InlineKeyboardButton("24-Hour Weather Forecast", callback_data='forecast24'),
         InlineKeyboardButton("Help", callback_data='help')   
            ]
        ]
        user = update.effective_user
        reply_markup = InlineKeyboardMarkup(inline_keyboard)
        await update.message.reply_text(f"Hello {user.first_name}! Welcome to the Weather Bot! Choose an option below:", reply_markup=reply_markup)
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        if query.data == "forecast24":
            keyboard = [
                [InlineKeyboardButton("General", callback_data='general')],
                [InlineKeyboardButton("North", callback_data='north'),
                InlineKeyboardButton("South", callback_data='south')],
                [InlineKeyboardButton("East", callback_data='east'),
                InlineKeyboardButton("West", callback_data='west')],
                [InlineKeyboardButton("Central", callback_data='central')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text('Please choose a region:', reply_markup=reply_markup)
            return REGION_SELECTED
        elif query.data == "help":
            await query.edit_message_text(text="Use /forecast24 to get the 24-hour forecast.")
            return ConversationHandler.END

    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Use /forecast24 to get the 24-hour forecast.")
        
    async def forecast24(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("General", callback_data='general')],
            [InlineKeyboardButton("North", callback_data='north'),
             InlineKeyboardButton("South", callback_data='south')],
            [InlineKeyboardButton("East", callback_data='east'),
             InlineKeyboardButton("West", callback_data='west')],
            [InlineKeyboardButton("Central", callback_data='central')],

            
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('Please choose a region:', reply_markup=reply_markup)
        return REGION_SELECTED
    async def region_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        region = query.data
        
        try:
            api_url = "https://api.data.gov.sg/v1/environment/24-hour-weather-forecast"
            res = self.weather_24.scrape(api_url)
            if region == 'general':
                weather_data = res.get("general")
                validity = self.format_period(res.get("validity")) #Return format: 12 PM 3 May to 12 PM 4 May
                forecast = weather_data["forecast"] #Returns format: Thundery Showers
                general_temperature_low = weather_data.get("temperature").get("low")
                general_temperature_high = weather_data.get("temperature").get("high")
                general_humidity_low = weather_data.get("relative_humidity").get("low")
                general_humidity_high = weather_data.get("relative_humidity").get("high")
                updated_time = self.format_timestamp(res.get("timestamp")) #Return format: 4:10 PM, 3 May 2025
                heat_index = round(self.calculate_heat_index((general_temperature_high+general_temperature_low)/2, (general_humidity_high+general_humidity_low)/2),2) #Calculates heat index based on temp and humidity in degres celsius
                message = f"General Weather Forecast:\n\n{WEATHER_EMOJI.get(forecast, '')} {forecast}\n\nTemperature: {general_temperature_low}°C - {general_temperature_high}°C\nHumidity: {general_humidity_low}% - {general_humidity_high}%\n\nHeat Index: {heat_index}°C \n\nValidity: {validity}\nUpdated at: {updated_time}\n\n"
                await query.edit_message_text(text=message)
            else:
                weather_data = res.get("general")
                validity = self.format_period(res.get("validity")) #Return format: 12 PM 3 May to 12 PM 4 May
                forecast = res[region] #Returns format: Thundery Showers
                general_temperature_low = weather_data.get("temperature").get("low")
                general_temperature_high = weather_data.get("temperature").get("high")
                general_humidity_low = weather_data.get("relative_humidity").get("low")
                general_humidity_high = weather_data.get("relative_humidity").get("high")
                updated_time = self.format_timestamp(res.get("timestamp")) #Return format: 4:10 PM, 3 May 2025
                heat_index = round(self.calculate_heat_index((general_temperature_high+general_temperature_low)/2, (general_humidity_high+general_humidity_low)/2),2) #Calculates heat index based on temp and humidity in degres celsius
                message = f"{region.capitalize()} Weather Forecast:\n\n{WEATHER_EMOJI.get(forecast, '')} {forecast}\n\nTemperature: {general_temperature_low}°C - {general_temperature_high}°C\nHumidity: {general_humidity_low}% - {general_humidity_high}%\n\nHeat Index: {heat_index}°C \n\nValidity: {validity}\nUpdated at: {updated_time}\n\n"
                await query.edit_message_text(text=message)
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            await query.edit_message_text(text="Sorry, I couldn't fetch the weather data. Please try again later.")
        return ConversationHandler.END
    def format_period(self,valid_period):
        # Parse the timestamps
        start = datetime.fromisoformat(valid_period['start'])
        end = datetime.fromisoformat(valid_period['end'])

        # Format the dates
        start_formatted = f"{start.strftime('%#I %p %#d %b')}"
        end_formatted = f"{end.strftime('%#I %p %#d %b')}"
        
        return f"{start_formatted} to {end_formatted}"
    def format_timestamp(self,timestamp):
        # Parse the timestamp
        date = datetime.fromisoformat(timestamp)

        # Format to a more readable format
        # Example: "4:10 PM, 3 May 2025"
        formatted = date.strftime("%#I:%M %p, %#d %b %Y")
        
        return formatted
    def calculate_heat_index(self, temperature, humidity): #Calculates heat index based on temp and humidity in degres celsius
        c1 = -8.78469475556
        c2 = 1.61139411
        c3 = 2.33854883889
        c4 = -0.14611605
        c5 = -0.012308094
        c6 = -0.0164248277778
        c7 = 0.002211732
        c8 = 0.00072546
        c9 = -0.000003582
        heat_index = (c1 + (c2 * temperature) + (c3 * humidity) + (c4 * temperature * humidity) + (c5 * (temperature**2)) + (c6 * (humidity**2)) + (c7 * (temperature**2) * humidity) + (c8 * temperature * (humidity**2)) + (c9 * (temperature**2) * (humidity**2)))
        return heat_index
    async def unknown_command(self,update, context):
        await update.message.reply_text(
            "Sorry, I don't recognize that command. Please use the buttons or try /help to see available commands."
        )
    def run(self):
        application = Application.builder().token(self.token).build()
        
        
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('forecast24', self.forecast24), 
                          CallbackQueryHandler(self.button_handler,pattern='^(forecast24|help)$')],
            states={
                REGION_SELECTED: [
                    CallbackQueryHandler(self.region_selected)
                ]
            },
            fallbacks=[CommandHandler('start', self.start)]
        )
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('help', self.help))
        application.add_handler(conversation_handler)
        
        # Handle all text messages that aren't commands
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.unknown_command))
        application.add_handler(MessageHandler(filters.Command(), self.unknown_command))
        application.run_polling()
        
if __name__ == '__main__':
    TOKEN = os.getenv('TOKEN')
    if not TOKEN:
        logger.error("No token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
        sys.exit(1)
        
    weather_bot = WeatherBot(token=TOKEN)
    weather_bot.run()
        