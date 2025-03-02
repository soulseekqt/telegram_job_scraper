# Telegram Jobs Bot

JobsBot is a Telegram bot that helps users search for job listings using the [JobSpy](https://github.com/tcapelle/jobspy) job scraper library. Users can send a search query in the format `<search_term>, <location>`, and the bot will retrieve relevant job postings from multiple job platforms (Indeed, LinkedIn, Glassdoor, Google) and provide the results in both chat messages and a downloadable CSV file.

## Features
- 🔍 Search for jobs from various sources using JobSpy.
- 📄 Receive job listings as a paginated message in Telegram.
- 📂 Download job listings as a CSV file.
- 🔄 Navigate job results using inline buttons.

## Setup and Installation
### Prerequisites
- Python 3.8 or later
- A Telegram bot token (obtain from [BotFather](https://t.me/BotFather) on Telegram)
- Pip and virtual environment tools installed

### Installation Steps
1. **Clone the repository**
   ```sh
   git clone https://github.com/soulseekqt/telegram_job_scraper.git
   cd telegram_job_scraper
   ```

2. **Create and activate a virtual environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project directory and add your Telegram bot token:
   ```ini
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

5. **Run the bot**
   ```sh
   python bot.py
   ```

## Usage
1. **Start the bot** by sending the `/start` command.
2. **Search for jobs** by sending a message in the format:
   ```
   legal counsel, Berlin
   ```
3. The bot will fetch job listings and send them as a formatted message with pagination buttons.
4. **Download the CSV file** by clicking the provided file link.
5. **Navigate results** using the ⬅️ `Previous` and `Next ➡️` buttons.

## Deployment
To deploy JobsBot on a server, consider using:
- **Docker**: Create a `Dockerfile` and deploy the bot inside a container.
- **PM2**: Use `pm2` for process management.
- **Cloud Services**: Deploy on AWS Lambda, Google Cloud Functions, or a VPS.

## License
This project is licensed under the MIT License.

## Contributing
Pull requests and issues are welcome! Feel free to improve the bot and suggest new features.

## Author
Jacky Lui (https://github.com/soulseekqt/)

