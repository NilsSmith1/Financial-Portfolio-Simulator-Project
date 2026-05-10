#%% Packages to Import
import yfinance as yf
import pandas as pd
import sqlite3
#%% Global Variables
strTicker = 'voo'
dtStartDate = '2010-01-01'
dtEndDate = '2020-12-31'

#%% Functions
def getHistoricalData(ticker, startDate, endDate):
    try: 
        ticker = yf.Ticker(ticker)
        df = ticker.history(start=startDate, end=endDate, auto_adjust=False)
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

#%% YF Data
print(f"Fetching historical data for {strTicker} from {dtStartDate} to {dtEndDate}...")
df = getHistoricalData(strTicker, dtStartDate, dtEndDate)
if df is not None:
    print(f"Data fetched successfully for {strTicker}.")
    print(df)
#%% Clean YF Data


#%% Insert Data into DB