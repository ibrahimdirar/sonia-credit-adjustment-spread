# %%
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# %%
libor_all_tenors = pd.read_csv('libor-rates.csv', usecols=['Tenor', 'Value', 'Date'],                                 parse_dates=['Date'], dayfirst = True)
libor_all_tenors


# %%
sns.lineplot(data=libor_all_tenors, x="Date", y="Value", hue="Tenor")


# %%
libor_wide = libor_all_tenors.pivot_table(index="Date",columns="Tenor",values="Value")
libor_wide


# %%
# Source https://www.bankofengland.co.uk/boeapps/database/fromshowcolumns.asp?Travel=NIxSUx&FromSeries=1&ToSeries=50&DAT=RNG&FD=1&FM=Jan&FY=2011&TD=18&TM=Mar&TY=2021&FNY=&CSVF=TT&html.x=223&html.y=22&C=5JK&Filter=N
sonia = pd.read_csv('sonia.csv', parse_dates=['Date'], dayfirst=True)
sonia


# %%
sonia.sort_values(by='Date', inplace=True)
sonia_rolling_averages = sonia.copy()
sonia_rolling_averages['Sonia 7 Day Average'] = sonia_rolling_averages['Sonia Overnight Rate'].rolling(7).mean()
sonia_rolling_averages['Sonia 30 Day Average'] = sonia_rolling_averages['Sonia Overnight Rate'].rolling(30).mean()
sonia_rolling_averages['Sonia 60 Day Average'] = sonia_rolling_averages['Sonia Overnight Rate'].rolling(60).mean()
sonia_rolling_averages['Sonia 90 Day Average'] = sonia_rolling_averages['Sonia Overnight Rate'].rolling(90).mean()
sonia_rolling_averages['Sonia 180 Day Average'] = sonia_rolling_averages['Sonia Overnight Rate'].rolling(180).mean()
sonia_rolling_averages['Sonia 360 Day Average'] = sonia_rolling_averages['Sonia Overnight Rate'].rolling(360).mean()
sonia_rolling_averages


# %%
sns.lineplot(data=sonia_rolling_averages.set_index('Date'))


# %%
interest_rates = libor_wide.merge(sonia_rolling_averages, how = 'inner', on = 'Date').set_index('Date')
interest_rates


# %%
sonia_libor_differential = interest_rates.copy()

for column in sonia_libor_differential:
    if column == 'Overnight':
        sonia_libor_differential[column] -= sonia_libor_differential['Sonia Overnight Rate']
        sonia_libor_differential.drop(columns='Sonia Overnight Rate', inplace=True)
    elif column == '1 Week':
        sonia_libor_differential[column] -= sonia_libor_differential['Sonia 7 Day Average']
        sonia_libor_differential.drop(columns='Sonia 7 Day Average', inplace=True)
    elif column == '1 Month':
        sonia_libor_differential[column] -= sonia_libor_differential['Sonia 30 Day Average']
        sonia_libor_differential.drop(columns='Sonia 30 Day Average', inplace=True)
    elif column == '2 Month':                        
        sonia_libor_differential[column] -= sonia_libor_differential['Sonia 60 Day Average']
        sonia_libor_differential.drop(columns='Sonia 60 Day Average', inplace=True)
    elif column == '3 Month':                      
        sonia_libor_differential[column] -= sonia_libor_differential['Sonia 90 Day Average']
        sonia_libor_differential.drop(columns='Sonia 90 Day Average', inplace=True)
    elif column == '6 Month':                      
        sonia_libor_differential[column] -= sonia_libor_differential['Sonia 180 Day Average']
        sonia_libor_differential.drop(columns='Sonia 180 Day Average', inplace=True)
    elif column == '1 Year':                      
        sonia_libor_differential[column] -= sonia_libor_differential['Sonia 360 Day Average']
        sonia_libor_differential.drop(columns='Sonia 360 Day Average', inplace=True)                    
    
five_year_adjustment_spreads = sonia_libor_differential[sonia_libor_differential.index > np.datetime64('2014-03-16')]
five_year_adjustment_spreads


# %%
five_year_adjustment_spreads.describe()


# %%
five_year_adjustment_spread = pd.DataFrame(five_year_adjustment_spreads.median(), index=['Overnight', '1 Week', '1 Month', '2 Month', '3 Month', '6 Month', '1 Year'])
five_year_adjustment_spread.columns = ['Adjustment Spread']
five_year_adjustment_spread

# %%
# five_year_sonia = sonia_libor_differential[sonia_libor_differential.index > np.datetime64('2014-03-16')]
# five_year_sonia = sonia_libor_differential[sonia_libor_differential.index > np.datetime64('2014-03-16')]
synthetic_libor = sonia.copy()
synthetic_libor.drop(columns = 'Sonia Overnight Rate', inplace=True)
synthetic_libor['Overnight'] = sonia_rolling_averages['Sonia Overnight Rate'] + five_year_adjustment_spread.loc['Overnight','Adjustment Spread']
synthetic_libor['1 Week'] = sonia_rolling_averages['Sonia 7 Day Average'] + five_year_adjustment_spread.loc['1 Week','Adjustment Spread']
synthetic_libor['1 Month'] = sonia_rolling_averages['Sonia 30 Day Average'] + five_year_adjustment_spread.loc['1 Month','Adjustment Spread']
synthetic_libor['2 Month'] = sonia_rolling_averages['Sonia 60 Day Average'] + five_year_adjustment_spread.loc['2 Month','Adjustment Spread']
synthetic_libor['3 Month'] = sonia_rolling_averages['Sonia 90 Day Average'] + five_year_adjustment_spread.loc['3 Month','Adjustment Spread']
synthetic_libor['6 Month'] = sonia_rolling_averages['Sonia 180 Day Average'] + five_year_adjustment_spread.loc['6 Month','Adjustment Spread']
synthetic_libor['1 Year'] = sonia_rolling_averages['Sonia 360 Day Average'] + five_year_adjustment_spread.loc['1 Year','Adjustment Spread']
synthetic_libor.set_index('Date', inplace=True)
synthetic_libor = synthetic_libor[synthetic_libor.index > np.datetime64('2014-03-16')]

# %%
for column in synthetic_libor:
    plt.figure()
    sns.lineplot(data=synthetic_libor[column])
    sns.lineplot(data=libor_wide[column])

# %%
