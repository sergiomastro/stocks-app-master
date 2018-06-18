import csv
import json
import os
import pdb
import requests
import datetime
from IPython import embed

def parse_response(response_text):
    if isinstance(response_text, str):
        response_text = json.loads(response_text)

    results = []
    time_series_daily = response_text["Time Series (Daily)"]
    for trading_date in time_series_daily:
        prices = time_series_daily[trading_date]
        result = {
            "date": trading_date,
            "open": prices["1. open"],
            "high": prices["2. high"],
            "low": prices["3. low"],
            "close": prices["4. close"],
            "volume": prices["5. volume"]
        }
        results.append(result)
    return results

def write_prices_to_file(prices=[], filename="data/prices.csv"):
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for d in prices:
            row = {
                "timestamp": d["date"],
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"]
            }
            writer.writerow(row)

output = """
    -----------------------------------
    ROBO STOCK ADVISOR
    -----------------------------------
    """

execute_time = datetime.datetime.now()


if __name__ == '__main__':


    symbol_error = "I'm sorry. The entry does not appear to be a valid stock symbol. Please try again."
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."


    symbol = input("Please enter a stock symbol:  ")

    try:
        float(symbol)
        quit("I'm sorry. The entry does not appear to be a valid stock symbol. Please try again.")
    except ValueError as e:
        pass

    request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"

    print("Issuing a request")
    response = requests.get(request_url)

    if "Error Message" in response.text:
        print(symbol_error)
        quit("Stopping the program.")

    daily_prices = parse_response(response.text)

    write_prices_to_file(prices=daily_prices, filename="data/prices.csv")

    data_date = daily_prices[0]["date"]
    format_str = "%Y-%m-%d"
    refresh_date = datetime.datetime.strptime(data_date, format_str)

    high_prices = []
    for p in daily_prices:
        high_prices.append(float(p["high"]))

    avg_high_price = max(high_prices)

    low_prices = []
    for p in daily_prices:
        low_prices.append(float(p["low"]))

    avg_low_price = min(low_prices)

    latest_closing_price = daily_prices[0]["close"] #> '361.4500'
    latest_closing_price = float(latest_closing_price)
    latest_closing_price_usd = "${0:,.2f}".format(latest_closing_price)

    recommendation = ""

    if latest_closing_price >=  avg_high_price:
        recommendation = "SELL: The current stock price is at or exceeds the recent high price."

    elif latest_closing_price <= avg_low_price:
        recommendation = "BUY: The current stock price is at or less than the recent low price."

    else:
        recommendation = "HOLD: The current stock price is between its recent high and low price."


    print(output)
    print(execute_time.strftime("Run Date: %I:%M %p on %B %d, %Y "))
    print("Stock Symbol: " + symbol.upper())
#    print(daily_prices[0]["date"])
    print(refresh_date.strftime("Latest Data From: %B %d, %Y"))
#    print("Data Refresh Date: ")
    print("Latest Closing Price: " + latest_closing_price_usd)
#    print(avg_high_price)
    print("Recent High Price (from past 100 days): " + "${0:,.2f}".format(avg_high_price))
    print("Recent Low Price (from past 100 days): " + "${0:,.2f}".format(avg_low_price))
    print("Recommendation: " + recommendation)
