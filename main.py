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
import matplotlib.pyplot as plt

#%% Portfolio Simulation Functions


def estimateParameters(prices: pd.DataFrame):
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
    
    L = np.linalg.cholesky(covLogReturn)
    
    #generate the random variable
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal((nSteps, numSimulations, nAssets))
    shocks = (Z @ L.T) * np.sqrt(dt)

    
    #weights
    weights = np.array(weights)

    drift = (meanLogReturn - 0.5 * stdLogReturn ** 2) * dt
    
    # Asset price paths
    logGrowth = np.cumsum(drift + shocks, axis=0)
    assetGrowth = np.exp(logGrowth)
    
    # Buy and hold strategy
    allocations = weights * initialInvestment    
    pathValues = (assetGrowth * allocations).sum(axis=2) 
    
    start = np.full((1, numSimulations), initialInvestment, dtype=float)
    return np.vstack([start, pathValues])
    
    
def simulationPortfolioReturnYearByYearAverage(prices, weights, years, numSimulations, initialInvestment, stepsPerYear, seed=None):
    # A given asset's price can be modelled as a geometric Brownian motion
    # ds/s = (expected return) *dt + (std returns)*(random variable) *sqrt(dt)
    # random variable = N(0,1) where N is a standard normal distribution
    
    # mean return and standard deviation of log returns
    meanLogReturn, stdLogReturn, covLogReturn = estimateParameters(prices)
    
    #calculate change in time
    dt = 1/stepsPerYear
    
    nSteps = int(years * stepsPerYear)
    nAssets = len(prices.columns)
    
    L = np.linalg.cholesky(covLogReturn)
    
    #generate the random variable
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal((nSteps, numSimulations, nAssets))
    shocks = (Z @ L.T) * np.sqrt(dt)

    
    #weights
    weights = np.array(weights)

    drift = (meanLogReturn - 0.5 * stdLogReturn ** 2) * dt
    
    # Asset price paths
    logGrowth = np.cumsum(drift + shocks, axis=0)
    assetGrowth = np.exp(logGrowth)
    
    # Buy and hold strategy
    allocations = weights * initialInvestment    
    pathValues = (assetGrowth * allocations).sum(axis=2) 
    
    start = np.full((1, numSimulations), initialInvestment, dtype=float)
    
    yearByYearAverageReturns = []
    
    for year in range(years):
        yearEndIndex = (year + 1) * stepsPerYear
        yearEndValues = pathValues[yearEndIndex - 1]
        yearByYearAverageReturns.append(np.mean(yearEndValues))
        
    return yearByYearAverageReturns
           
    
# Create a basic mock portfolio
dtStartDate = '2010-01-01'
dtEndDate = '2020-12-31'
tickers = ['VOO']
data = yf.download(tickers, start=dtStartDate, end=dtEndDate, auto_adjust=True)
prices = data.xs('Close', axis=1, level='Price')
prices = prices.dropna()  # Drop rows with NaN values
prices = prices[tickers] #make sure order of columns is same as tickers list
    
    
# Run the simulation with the mock portfolio
simulationYears = 10
simulationResults = simulationPortfolioReturn(prices, [1], simulationYears, 1000, 10000, 252)
  
# Average return and standard deviation of the simulation results

averageReturn = np.mean(simulationResults)
#print(f"Average return after {simulationYears} years: ${averageReturn:.2f}")

#plt.boxplot(simulationResults)
#plt.title(f"Distribution of Forecasted Portfolio Valuation After {simulationYears} Years") 

#plt.show()

simulationResultsYearly = simulationPortfolioReturnYearByYearAverage(prices, [1], simulationYears, 1000, 10000, 252)
print(f"Year by year average returns: {simulationResultsYearly}")

x = np.arange(1, simulationYears + 1)
y = simulationResultsYearly
coefficients = np.polyfit(x, y, 2)
polynomial = np.poly1d(coefficients)
x_line = np.linspace(x.min(), x.max(), 100)
plt.plot(x_line, polynomial(x_line), color="purple")
plt.scatter(x, y)
plt.xlabel("years")
plt.ylabel("average portfolio value (USD)")
plt.title(f"Year by Year Average Returns After {simulationYears} Years")





plt.show()

# %%
