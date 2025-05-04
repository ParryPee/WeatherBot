# Singapore Weather Telegram Bot

A Telegram bot that provides weather forecasts for Singapore regions using data from the Singapore government data API.

## Features

- 24-hour weather forecast for Singapore
- Regional forecasts (North, South, East, West, Central)
- "Feels like" temperature using heat index calculation based on nearest weather station
- General weather overview
- Emoji weather indicators
- Heat index calculations
- Formatted timestamps and validity periods

## Requirements

- Python 3.8+
- Telegram Bot Token (obtained from [BotFather](https://t.me/botfather))
- Internet connection to access Singapore's data.gov.sg API

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sg-weather-bot.git
   cd sg-weather-bot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. Install the dependencies:
   ```bash
   pip install python-telegram-bot requests beautifulsoup4
   ```

5. Set up the environment variable for your Telegram Bot Token:
   - On Windows:
     ```bash
     set TOKEN=your_telegram_bot_token
     ```
   - On macOS/Linux:
     ```bash
     export TOKEN=your_telegram_bot_token
     ```

## Usage

1. Start the bot:
   ```bash
   python bot.py
   ```

2. Open Telegram and find your bot by the username you set when creating it with BotFather.

3. Start a conversation with the bot by sending the `/start` command.

4. Use the buttons or commands to get weather forecasts:
   - `/start` - Show the main menu
   - `/help` - Display help information
   - `/forecast24` - Get the 24-hour forecast for a region
   - `/feelslike` - Get the current "feels like" temperature based on your location

## Project Structure

- `bot.py` - Main bot file containing the Telegram bot implementation
- `weather_grabber.py` - Classes for fetching and processing weather data
- `src/` - Source files:
  - `__init__.py` - Package initialization
  - `parser.py` - Data parsing utilities
  - `requester.py` - HTTP request handling
  - `scraper.py` - Web scraping framework

## Weather Data

The bot fetches data from Singapore's official weather APIs:
- 24-hour forecast: https://api.data.gov.sg/v1/environment/24-hour-weather-forecast
- Relative humidity: https://api-open.data.gov.sg/v2/real-time/api/relative-humidity
- Air temperature: https://api-open.data.gov.sg/v2/real-time/api/air-temperature

## Weather Emojis

The bot uses the following emojis to represent weather conditions:

- Thundery Showers: ⛈️
- Cloudy: ☁️
- Partly Cloudy (Day): 🌤️
- Partly Cloudy (Night): 🌃
- Fair (Day): 🌞
- Fair (Night): 🌙
- Light Rain: 🌦️
- Moderate Rain: 🌧️
- Heavy Rain: 🌧️
- Showers: 🌦️
- Hazy: 😶‍🌫️
- Windy: 💨

## Heat Index

The bot calculates the heat index based on temperature and humidity, providing a "feels like" temperature that accounts for how the human body perceives the combination of heat and humidity.

### Heat Index Calculation

The heat index is calculated using the polynomial regression equation that accounts for:
- Air temperature
- Relative humidity
- The combined effect of temperature and humidity on thermal comfort

For the "feels like" feature, the bot:
1. Retrieves the user's current location (requires location permission)
2. Finds the nearest weather station based on Haversine distance calculation
3. Gets real-time temperature and humidity readings from that station
4. Calculates the heat index to determine the "feels like" temperature
5. Presents this information to the user with the name of the nearest station

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Acknowledgements

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Framework for building Telegram bots
- [data.gov.sg](https://data.gov.sg) - Singapore's open data portal providing weather API
