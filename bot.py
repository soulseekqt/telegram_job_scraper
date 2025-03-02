import os
import csv
import io
import math
import asyncio
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from jobspy import scrape_jobs
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the /start command is issued."""
    welcome_text = (
        "👋 Welcome to JobsBot!\n\n"
        "🔍 Send me a job search query in the format:\n"
        "<search_term>, <location>\n\n"
        "Example: \"legal counsel, Berlin\"\n\n"
        "I'll find recent job listings and send you a CSV file!"
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages containing job search requests."""
    user_input = update.message.text
    try:
        if ',' not in user_input:
            raise ValueError("Please use the format: <search_term>, <location>")

        search_term, location = [part.strip() for part in user_input.split(',', 1)]

        processing_msg = await update.message.reply_text(
            f"🔍 Searching for '{search_term}' positions in {location}...\n"
            "This may take a minute ⏳"
        )

        jobs = await asyncio.to_thread(
            scrape_jobs,
            site_name=["indeed", "linkedin", "glassdoor", "google"],
            search_term=search_term,
            location=location,
            results_wanted=50,  # Store more jobs for pagination
            hours_old=72,
            country_indeed='Germany',
            google_search_term=f"{search_term} jobs near {location}, Germany"
        )

        if len(jobs) == 0:
            await processing_msg.edit_text("❌ No jobs found matching your criteria.")
            return

        # Rearrange columns
        jobs = jobs[["title", "company", "location", "date_posted", "job_url", "job_url_direct"]]

        # Save jobs to CSV
        csv_buffer = io.StringIO()
        jobs.to_csv(csv_buffer, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
        csv_buffer.seek(0)
        csv_file = io.BytesIO(csv_buffer.getvalue().encode())

        context.user_data["jobs"] = jobs.to_dict("records")
        context.user_data["search_term"] = search_term
        context.user_data["location"] = location
        context.user_data["page"] = 0

        await send_job_results(update, context, page=0, csv_file=csv_file)

        await processing_msg.delete()

    except Exception as e:
        error_msg = f"⚠️ Error: {str(e)}"
        await update.message.reply_text(error_msg)


async def send_job_results(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int, csv_file=None):
    """Send a paginated list of job results with navigation buttons and attach CSV."""
    jobs = context.user_data.get("jobs", [])
    search_term = context.user_data.get("search_term", "Unknown")
    location = context.user_data.get("location", "Unknown")

    jobs_per_page = 5
    total_pages = math.ceil(len(jobs) / jobs_per_page)
    start_idx = page * jobs_per_page
    end_idx = start_idx + jobs_per_page
    job_subset = jobs[start_idx:end_idx]

    # Format job listings
    job_messages = []
    for row in job_subset:
        job_title = row.get("title", "No Title")
        company = row.get("company", "Unknown Company")
        job_location = row.get("location", "Unknown Location")
        date_posted = row.get("date_posted", "Unknown Date")
        job_url = row.get("job_url", "#")

        job_text = f"📌 <b><a href='{job_url}'>{job_title}</a></b>\n🏢 {company} | 📍 {job_location} | 📅 {date_posted}"
        job_messages.append(job_text)

    final_message = (
        f"✅ <b>Job Results ({page + 1}/{total_pages})</b>\n"
        f"🔍 <b>{search_term}</b> in {location}\n\n"
        + "\n\n".join(job_messages)
    )

    # Create navigation buttons
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"prev_{page-1}"))
    if end_idx < len(jobs):
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"next_{page+1}"))

    keyboard = InlineKeyboardMarkup([buttons]) if buttons else None

    # Send message
    if update.callback_query:
        await update.callback_query.message.edit_text(final_message, parse_mode="HTML", reply_markup=keyboard)
        await update.callback_query.answer()
    else:
        message = await update.message.reply_text(final_message, parse_mode="HTML", reply_markup=keyboard)

        # Attach CSV file
        if csv_file:
            csv_file.seek(0)
            await update.message.reply_document(
                document=InputFile(csv_file, filename=f"jobs_{search_term.replace(' ', '_')}_{location}.csv"),
                caption="📄 Download all job listings in CSV format."
            )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination button clicks."""
    query = update.callback_query
    if not query:
        return

    _, page_str = query.data.split("_")
    page = int(page_str)

    context.user_data["page"] = page

    await send_job_results(update, context, page)


def main():
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot is running...")
    application.run_polling()


if __name__ == '__main__':
    main()
