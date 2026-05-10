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

dfYfPriceData = getHistoricalData(strTicker, dtStartDate, dtEndDate)


#%% Clean YF Data
print(dfYfPriceData.info())

# Remove non essential columns from data frame
dfYfPriceData = dfYfPriceData.drop(columns=['Dividends', 'Stock Splits', 'Close', 'Capital Gains', 'Volume'])

# Change the format of the index date column using strftime to yyyy-mm-dd
dfYfPriceData.index = dfYfPriceData.index.strftime('%Y-%m-%d')
dfYfPriceData.reset_index(inplace=True)

# Rename columns (current: to be)
dfYfPriceData.rename(columns={'Date': 'price_date'}, inplace=True)

#%% Insert Data into DB