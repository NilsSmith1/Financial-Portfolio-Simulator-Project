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

def insertDataToSqlite(df):
    
    if df.empty:
        return "Error: DataFrame is empty. No data to insert."
    
    try: 
        
        #connect to db
        conn = sqlite3.connect('dbFDDSecurities.db')
        
        # create cursor object
        c = conn.cursor()
        
        # Check if 't_price_data' table exists, if not create it
        c.execute('''
                CREATE TABLE IF NOT EXISTS t_price_data (
                price_date TEXT,
                ticker TEXT,
                price_open REAL,
                price_high REAL,
                price_low REAL,
                price_adj_close REAL
            )
        ''')
        
        # Insert the data from the dataframe into the table
        # Or replace existing data if ticker+date already exist in db
        
        df.tosql('t_price', conn, if_exists='replace', index=False)
        
        # Commit changes
        conn.commit()
        
        # Close connection
        conn.close()
        
        return "Data inserted successfully."
    except Exception as e:
        return f"Error inserting data into database: {e}"
    
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
dfYfPriceData.rename(columns={'Date': 'Price Date', 'Open': 'Price Open', 'High': 'Price High', 'Low': 'Price Low', 'Adj Close': 'Price Adj Close'}, inplace=True)

# Insert a new column called 'Ticker' with the value of string ticker
dfYfPriceData.insert(0, 'Ticker', strTicker.upper())

# Reorder columns so date is first, then ticker, open, high, low, adj close
dfYfPriceData = dfYfPriceData[['Price Date', 'Ticker', 'Price Open', 'Price High', 'Price Low', 'Price Adj Close']]

#%% Insert Data into DB
result = insertDataToSqlite(dfYfPriceData)



#%% Time to mess around and try to incorporate a monte carlo

#Simulation

def discountFactor(years, r):
    return(1/(1+r)^years)
    
def payoffFunction(stateOfWorld):
    

#Risk neutral probability measure
def P()

def blackScholesModel():
    #Assume that stock price follows the function of a Brownian motion
    
    #Make an estimation for todays price of an asset
    
    #Compute discount factor
    
    dfYfPriceData
    
    
    
    derivativeValue 


#n is number of simulations
n = 10
s=0

for i in range(n):
    # run the simulation for the ith time, and produce result ri
    r=1
    s = s+1

SimulationAverage = s/n
print(SimulationAverage)



# %%
