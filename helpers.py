import os
import requests
import urllib.parse

from cs50 import SQL
from flask import redirect, render_template, request, session
from functools import wraps
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pytz

db = SQL("sqlite:///finance.db")

def timecheck(ticker):

    #timecheck checks to see if we've updated in that time of day because we only update three times a week
    current_date = datetime.now(pytz.timezone("America/New_York")).strftime('%Y-%m-%d')
    current_time = datetime.now(pytz.timezone("America/New_York"))
    current_minute = str(current_time.minute)
    if (len(current_minute) < 2):
        current_minute = str(0) + current_minute
    hour_min = int(str(current_time.hour) + current_minute)

    #adjust time ints to check
    time_to_display = str(current_time.hour) + ":" + current_minute
    if (current_time.minute < 10):
        current_minute = str(0) + str(current_time.minute)
        hour_min = int(str(current_time.hour) + current_minute)
        time_to_display = str(current_time.hour) + ":" + current_minute

    #get the latest quote for that ticker
    quote =  db.execute("SELECT date, time, ticker, price, change FROM prices WHERE ticker = :ticker", ticker = ticker)[0]

    #if there is no quote, we need to update it in our prices database
    if len(quote) == 0:
        ticker_quote = lookup(ticker)
        price = ticker_quote["price"]
        change = ticker_quote["change"]
        profile = company_profile(ticker)
        industry = ""
        if profile is not None:
            industry = profile["industry"]
        else:
            industry = "misc."
        db.execute("UPDATE prices SET date = :date, time = :time, price = :price, industry = :industry, change = :change WHERE ticker = :ticker", date = current_date, time = hour_min, price = price, industry = industry, change = change, ticker = ticker)

    #check the time of days to update accordingly
    first_check = (quote["date"] < current_date)
    second_check = (quote["date"] == current_date and hour_min >= 930 and hour_min < 1230 and quote["time"] < 930)
    first_third_check = (quote["date"] == current_date and hour_min < 1530 and hour_min >= 1230 and quote["time"] < 1230)
    second_third_check = (quote["date"] == current_date and hour_min >= 1530 and hour_min < 1630 and quote["time"] < 1530)
    third_third_check = (quote["date"] == current_date and hour_min >= 1630 and quote["time"] < 1630)

    return (first_check or second_check or first_third_check or second_third_check or third_third_check)

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""
    # Contact API
    try:
        api_key = os.environ.get("API_KEY_IEX")
        url = f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"],
            "change": quote["changePercent"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def news_lookup(symbol):
    """Look up quote for symbol."""

    today = date.today()
    today_sixmonths = today + relativedelta(months=- 6)
    d1 = today.strftime("%Y-%m-%d")
    d2 = today_sixmonths.strftime("%Y-%m-%d")

    api_input = "&from=" + d2 + "&to=" + d1 + "&"
    # Contact API
    try:
        api_key = os.environ.get("API_KEY_FINNHUB")
        url = f"https://finnhub.io/api/v1/company-news?symbol={urllib.parse.quote_plus(symbol)}{api_input}token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        news = response.json()
        return_news = []
        return_news.clear()
        i = 0
        for new in news:
            return_news.append({"datetime": datetime.utcfromtimestamp(new["datetime"]).strftime('%m-%d-%Y'),"headline": new["headline"],"source": new["source"],"summary": new["summary"],"url": new["url"], "image": new["image"]})
        return return_news
    except (KeyError, TypeError, ValueError):
        return None

def company_profile(symbol):
    # Contact API
    try:
        api_key = os.environ.get("API_KEY_FINNHUB")
        url = f"https://finnhub.io/api/v1/stock/profile2?symbol={urllib.parse.quote_plus(symbol)}&token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        profile = response.json()
        return {
            "name": profile["ticker"],
            "industry": profile["finnhubIndustry"],
            "exchange": profile["exchange"],
            "url": profile["weburl"],
            "logo": profile["logo"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
