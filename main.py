# This is a python script that will run a monte carlo simulation on a financial portfolio to determine
# the expected return and risk of the portfolio. 


# https://www.youtube.com/watch?v=DINIzZ4EO6I
# https://en.wikipedia.org/wiki/Monte_Carlo_methods_in_finance
# https://www.investopedia.com/articles/investing/112514/monte-carlo-simulation-basics.asp
# https://en.wikipedia.org/wiki/Cholesky_decomposition
# https://en.wikipedia.org/wiki/Brownian_motion
# https://www.investopedia.com/ask/answers/062215/how-do-i-calculate-my-portfolios-investment-returns-and-performance.asp
# 


#%% Packages to Import
from numpy import sqrt
from numpy import log
from numpy import exp
import numpy as np
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
import yfinance as yf
import numpy as np
#Simulation

#def discountFactor(years, inflationRate):
    #return(1/(1+inflationRate)**years)

#def payoffFunction(stateOfWorld):
    #pass

# A given asset's price can be modelled as a geometric Brownian motion
# ds/s = (expected return) *dt + (std returns)*(random variable) *sqrt(dt)
# random variable = N(0,1) where N is a standard normal distribution


#def forecastedInflationRate(basCPI, annualRate, years):
    
    #def projectYear(currentCPI, remainingYears, history):
        #if remainingYears == 0:
            #return history
        
        #nextCPI = currentCPI * (1 + annualRate)
        #return projectYear(nextCPI, remainingYears - 1, history + [nextCPI])
    
    #return projectYear(basCPI, years, [])



def estimateParameters(prices: pd.Dataframe):
    # calculate the log returns of prices
    logReturns = np.log(prices / prices.shift(1)).dropna()
    
    # calculate the mean and standard deviation of the log returns (market open 252 days a year)
    meanLogReturn = logReturns.mean().values * 252
    stdLogReturn = logReturns.std().values * np.sqrt(252)
    covLogReturn = logReturns.cov().values * 252

    return meanLogReturn, stdLogReturn, covLogReturn



# Currently does not allow for rebalancing of the portfolio, but can be added in the future.
def simulationPortfolioReturn(prices, weights, years, numSimulations, initialInvestment, stepsPerYear, seed=None):
    # A given asset's price can be modelled as a geometric Brownian motion
    # ds/s = (expected return) *dt + (std returns)*(random variable) *sqrt(dt)
    # random variable = N(0,1) where N is a standard normal distribution
    
    # mean return and standard deviation of log returns
    meanLogReturn, stdLogReturn, covLogReturn = estimateParameters(prices)
    
    #calculate change in time
    dt = 1/stepsPerYear
    
    nSteps = int(years * stepsPerYear)
    nAssets = len(prices.columns)
    
    
    #generate the random variable
    randomVariable = np.random.normal(0, 1, (years * stepsPerYear, numSimulations))
    shocks = randomVariable @ np.linalg.cholesky(covLogReturn).T * np.sqrt(dt)
    
    #weights
    weights = np.array(weights)
    
    # Cholesky factor
    L = np.linalg.cholesky(covLogReturn)
    drift = (meanLogReturn - 0.5 * stdLogReturn ** 2) * dt
    
    # Asset price paths
    logGrowth = np.cumsum(drift + shocks, axis=0)
    assetGrowth = np.exp(logGrowth)
    
    # Buy and hold strategy
    pathValues = (assetGrowth * (weights * initialInvestment).reshape(-1, 1)).sum(axis=0)
    
    return pathValues
    
    
    
    
# Create a basic mock portfolio
dtStartDate = '2010-01-01'
dtEndDate = '2020-12-31'
tickers = ['VOO', 'AAPL', 'MSFT', 'GOOGL', 'AMZN']
prices = yf.download(tickers, start=dtStartDate, end=dtEndDate)['Adj Close']   
prices = prices.dropna()  # Drop rows with NaN values
    
simulationResults = simulationPortfolioReturn(prices, [1], 10, 1000, 10000, 252)
  







# %%
