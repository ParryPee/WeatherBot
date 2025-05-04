import os
import sys
import logging
from datetime import datetime
from weather_grabber import WeatherGrabber24, RHGrabber, AirTempGrabber
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup,ReplyKeyboardRemove
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
LOCATION_PROVIDED = 1

class WeatherBot:
    def __init__(self,token):
        self.token = token
        self.weather_24 = WeatherGrabber24()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        inline_keyboard = [
            [
         InlineKeyboardButton("24-Hour Weather Forecast", callback_data='forecast24')
            ],
            [
         InlineKeyboardButton("How hot now?", callback_data="feelslike")
            ],
            [
                
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
        elif query.data == "feelslike":
            await query.edit_message_text(text="Press the button below to provide me with your location.")
            keyboard = [
                [KeyboardButton(text="Use current location",request_location = True)],
                [KeyboardButton(text="Cancel")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True,one_time_keyboard=True)
            await query.message.reply_text("Press the button below to provide me with your location.",reply_markup=reply_markup)
            return LOCATION_PROVIDED
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Use /forecast24 to get the 24-hour forecast. \n\n /feelslike to check what temperature it feels like now.")
    
    async def feelslike(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Press the button below to provide me with your location.")
        keyboard = [
            [KeyboardButton(text="Use current location",request_location = True)],
            [KeyboardButton(text="Cancel")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True,one_time_keyboard=True)
        await update.message.reply_text("Press the button below to provide me with your location.",reply_markup=reply_markup)
        return LOCATION_PROVIDED
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
    def get_nearest_station(self,stations,latitude,longitude):
        import math
        def calculate_dist(lat1,long1,lat2,long2):
            R = 6371
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(long1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(long2)
            dlon = lon2_rad - lon1_rad
            dlat = lat2_rad - lat1_rad
            
            # Haversine formula
            a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c  # Distance in kilometers

            return distance
        best_station = None
        shortest_dist = float("inf")
        for station in stations:
            stat_lat = station.get("location").get("latitude")
            stat_long = station.get("location").get("longitude")
            distance = calculate_dist(latitude,longitude,stat_lat,stat_long)
            if distance < shortest_dist:
                best_station = station
                shortest_dist = distance
        return best_station
            
        
    
    async def feels_like(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        location = update.message.location
        latitude = location.latitude
        longitude = location.longitude
        try:
            message = ""
            #Get Relative Humidity
            rh_grabber = RHGrabber()
            rh_api_url = "https://api-open.data.gov.sg/v2/real-time/api/relative-humidity"
            rh_res = rh_grabber.scrape(rh_api_url)
            #Get Air temperature
            airtemp_grabber = AirTempGrabber()
            airtemp_url = "https://api-open.data.gov.sg/v2/real-time/api/air-temperature"
            airtemp_res = airtemp_grabber.scrape(airtemp_url)
            location = update.message.location
            latitude = location.latitude
            longitude = location.longitude
            
            stations = rh_res.get('stations')
            nearest_station = self.get_nearest_station(stations,latitude,longitude)
            
            nearest_station_id = nearest_station.get("id")
            nearest_station_rh = [item for item in rh_res.get("readings")[0].get("data") if item.get("stationId") == nearest_station_id]
            nearest_station_rh = nearest_station_rh[0]
            rh_now = nearest_station_rh.get("value")
            
            nearest_AT = [item for item in airtemp_res.get("readings")[0].get("data") if item.get("stationId") == nearest_station_id]
            nearest_AT = nearest_AT[0]
            at_now = nearest_AT.get("value")
            
            feels_like = round(self.calculate_heat_index(at_now,rh_now),2)
            
            message = f"Nearest Station: {nearest_station.get('name')}\n\nAir Temperature: {at_now}°C\nRelative Humidity: {rh_now}%\n\nFeels Like: {feels_like}°C"
            
            
            await update.message.reply_text(text=message,reply_markup=ReplyKeyboardRemove())
        
        except Exception as e:
            logger.error(f"Error in feels_like: {e}")
            await update.message.reply_text(text="Sorry, an error occured please try again later.")
        return ConversationHandler.END
        
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
                message = f"General Weather Forecast:\n\n{WEATHER_EMOJI.get(forecast, '')} {forecast}\n\nTemperature: {general_temperature_low}°C - {general_temperature_high}°C\nHumidity: {general_humidity_low}% - {general_humidity_high}%\n\nMedian Heat Index: {heat_index}°C \n\nValidity: {validity}\nUpdated at: {updated_time}\n\n"
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
                message = f"{region.capitalize()} Weather Forecast:\n\n{WEATHER_EMOJI.get(forecast, '')} {forecast}\n\nTemperature: {general_temperature_low}°C - {general_temperature_high}°C\nHumidity: {general_humidity_low}% - {general_humidity_high}%\n\nMedian Heat Index: {heat_index}°C \n\nValidity: {validity}\nUpdated at: {updated_time}\n\n"
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
    async def unknown_command(self,update: Update, context):
        await update.message.reply_text(
            "Sorry, I don't recognize that command. Please use the buttons or try /help to see available commands."
        )
    async def cancel_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.message.text == "Cancel":
            await update.message.reply_text("Location request canceled.", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        else:
            await update.message.reply_text("Please use the buttons or send /start to restart.",reply_markup=ReplyKeyboardRemove())
            return LOCATION_PROVIDED
    def run(self):
        application = Application.builder().token(self.token).build()
        
        
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('forecast24', self.forecast24), 
                          CallbackQueryHandler(self.button_handler,pattern='^(forecast24|help|feelslike)$'),
                          CommandHandler("feelslike",self.feelslike)
                          ],

            states={
                REGION_SELECTED: [
                    CallbackQueryHandler(self.region_selected)
                ],
                LOCATION_PROVIDED : [
                    MessageHandler(filters.LOCATION, self.feels_like),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.cancel_location)

                ]
            },
            fallbacks=[CommandHandler('start', self.start)]
        )
        application.add_handler(conversation_handler)
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('help', self.help))

        
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
        