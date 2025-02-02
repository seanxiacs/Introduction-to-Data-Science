# -*- coding: utf-8 -*-
"""cse351_hw2_xia_sean_113181409.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EWC-Iltho_b1dM0MHWkwmRN1I_sTfzfb

<h1> CSE351 HW2 </h1>

# <h1> Data </h1>
The goal of this homework is to develop a method to predict the electricity usage based on the weather conditions. We provide the following two datasets for this task:

1. Weather: Weather data for one year with daily weather conditions
2. Energy Usage: Energy usage history for one year (in kW) with 30-minute intervals. The energy usage of specific devices like AC, Fridge, washer, etc. are also given.

You will need to submit your code (programs/source files) in three different formats (.ipynb, .pdf and .py). Make sure that you properly document your program (code) with proper comments highlighting the exact sequence of operations which are required to arrive at the resulting tables and figures. The submission instructions are provided at the end of the assignment.
"""

from google.colab import files
uploaded = files.upload()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from wordcloud import WordCloud
import csv
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error
from sklearn.metrics import f1_score
import datetime

"""<h1> 1. </h1>
1. Examine the data, parse the time fields wherever necessary. Take the sum of the energy usage (Use [kW]) to get per day usage and merge it with weather data (10 Points).
"""

energydf = pd.read_csv('energy_data.csv')
energydf.describe()

energydf.head()

#Clean data, find outliers, and analyze.
sns.heatmap(energydf.isnull())

#The fact that the 'gen [kW]' column has a mean of 0.0 and all the other statistics are 0 indicates that no households included generated their own electricity. 
#In additon, 'use [kW]' and 'Grid [kW]' would logically have to be the same since nobody generated their own electricity.
#We can confirm that these columns are identical using a function in pandas.
energydf['use [kW]'].equals(energydf['Grid [kW]'])

#energydf = energydf.groupby(energydf.index.date)['y'].sum().reset_index() from https://python.tutorialink.com/pandas-dataframe-sum-up-rows-by-date-and-keep-only-one-row-per-day-without-timestamp/ doesn't seem to work.
#energydf.groupby([energydf.dt.year, energydf.dt.month, energydf.dt.day])['y'].sum() This does not seem to work :(
#We will remove everything but the use since that is the only column that concerns us
energydf = energydf.filter(['Date & Time', 'use [kW]'])
energydf.head()

#energydf.groupby([energydf.dt.year, energydf.dt.month, energydf.dt.day])['y'].sum() Still errors
#energydf.groupby(pd.to_datetime(df.time).dt.date).agg({'Date & Time': 'sum', 'x':'first', 'y':'first'}).reset_index() 
#energydf.dtypes

#Wait let me try something cool that someone told me to do
#energydf['Date & Time'] = pd.to_datetime(energydf['Date & Time'])#.dt.date

#energydf
#energydf.groupby(pd.to_datetime(energydf.time).dt.date).agg({'use [kW]': 'sum'}).reset_index() 
#energydf.groupby('Date & Time').sum()

#energydf.head()

#Rename the column name to 'time' so we can perform a merge later
#energydf.rename(columns={'Date & Time': "time", "use [kW]": "use [kW]"}) Does not seem to work
#energydf.columns = ['time', 'use [kW]']
energydf = energydf.rename(columns={'Date & Time': "time", "use [kW]": "use [kW]"})

energydf

#energydf.dtypes
#energydf = energydf.groupby('Date & Time').sum()
#energydf.head()
#energydf = energydf.groupby('time').sum()
#energydf = energydf.groupby(energydf['time'].dt.date).sum()
energydf['time'] = pd.to_datetime(energydf['time'])
#energydf.info()
energydf = energydf.groupby(pd.Grouper(key="time", freq="1D")).sum()

energydf
#energydf

weatherdf = pd.read_csv('weather_data.csv')
weatherdf.describe()

weatherdf.head()

sns.heatmap(weatherdf.isnull())

#pd.to_datetime(energydf['Date & Time'], unit='s') Instead of converting from 'Date & Time' in energydf to UNIX time I will just convert 'time' from weatherdf to date and time since it does not give error.
weatherdf['time'] = pd.to_datetime(weatherdf['time'], unit='s')

weatherdf.head()

weatherdf['time'] = pd.to_datetime(weatherdf['time'])#.dt.date
weatherdf = weatherdf.groupby(pd.Grouper(key="time", freq="1D")).mean()

#weatherdf = weatherdf.groupby('time',as_index=False).mean()

weatherdf

result = pd.merge(energydf, weatherdf, on="time")

result

result = result.reset_index()

result

"""<h1> 2. </h1>
2. Split the data obtained from step 1, into training and testing sets. The aim is to predict the usage for each day in the month of December using the weather data, so split accordingly. The usage as per devices should be dropped, only the “use [kW]” column is to be used for prediction from the dataset (5 points).
"""

#test = energydf.loc[energydf['time'].dt.month == 12]
#train = energydf.loc[energydf['time'].dt.month != 12]
#result.reset_index() need to reset index before and set result equal to that result
train = result.loc[result['time'].dt.month != 12]
test = result.loc[result['time'].dt.month == 12]

train

test

"""<h1> 3. </h1>
3. Linear Regression - Predicting Energy Usage:

Set up a simple linear regression model to train, and then predict energy usage for each day in the month of December using features from weather data (Note that you need to drop the “use [kW]” column in the test set first). How well/badly does the model work? (Evaluate the correctness of your predictions based on the original “use [kW]” column). Calculate the Root mean squared error
of your model. 

Finally generate a csv dump of the predicted values. Format of csv: Two columns, first should be the date and second should be the predicted value. (20 points)
"""

linReg = LinearRegression()
#linReg.fit(train.columns != 'use [kW]', train.columns == 'use [kW]')
linReg.fit(train.drop(['use [kW]', 'time'], axis = 1), train['use [kW]'])

#linReg.predict(train.loc[:, train.columns != 'use [kW]'])
linPredictedUsage = linReg.predict(test.drop(['use [kW]', 'time'], axis = 1))

linPredictedUsage

mean_squared_error(test['use [kW]'], linPredictedUsage, squared=False)

linArraytoConvert = {'date':test['time'], 'predicted value':linPredictedUsage}

linPredictedDataframe = pd.DataFrame(linArraytoConvert)

linPredictedDataframe.head()

linPredictedDataframe.to_csv('cse351_hw2_xia_sean_113181409_linear_regression.csv', index=False)

"""<h1> 4. </h1>
4. Logistic Regression - Temperature classification:

Using only weather data we want to classify if the temperature is high or low. Let's assume temperature greater than or equal to 35 is ‘high’ and below 35 is ‘low’. Set up a logistic regression model to classify the temperature for each day in the month of December. Calculate the F1 score for the model.

Finally generate a csv dump of the classification (1 for high, 0 for low)

Format: Two columns, first should be the date and second should be the classification (1/0).

(20 points)
"""

logTrain = train.copy()
#logTrain['temperature'] = pd.where(train['education'] < 35, 0, data['education'])
#logTrain.loc[logTrain["temperature"] < 35.0, "temperature"] = 0
logTrain['temperature'] = [1 if x >= 35 else 0 for x in logTrain['temperature']]

logTrain

logTest = test.copy()
#logTrain['temperature'] = pd.where(train['education'] < 35, 0, data['education'])
#logTrain.loc[logTrain["temperature"] < 35.0, "temperature"] = 0
logTest['temperature'] = [1 if x >= 35 else 0 for x in logTest['temperature']]

logTest

logTrain['temperature'].value_counts()

sns.countplot(x='temperature', data = logTrain, palette='hls')
#plt.show()
#plt.showfig('count_plot')

count_low = len(logTrain[logTrain['temperature'] == 0])
count_high = len(logTrain[logTrain['temperature'] == 1])
pct_low = count_low / (count_low + count_high)
print("Percentage of low temperature", pct_low * 100)
pct_high = count_high/(count_low+count_high)
print("percentage of high temperature", pct_high * 100)
#This is a little imbalanced but I cannot justify balancing since I am not good at data science.

logTrain.groupby('temperature').mean()

logReg = LogisticRegression(max_iter = 200)

#linReg.fit(train.columns != 'use [kW]', train.columns == 'use [kW]')
logReg.fit(logTrain.drop(['temperature', 'time'], axis = 1), logTrain['temperature'])

#linReg.predict(train.loc[:, train.columns != 'use [kW]'])
logPredictedUsage = logReg.predict(logTest.drop(['temperature', 'time'], axis = 1))

logPredictedUsage

f1_score(logTest['temperature'], logPredictedUsage)

logArraytoConvert = {'date':logTest['time'], 'predicted value':logPredictedUsage}

logPredictedDataframe = pd.DataFrame(logArraytoConvert)

logPredictedDataframe.head()

logPredictedDataframe.to_csv('cse351_hw2_xia_sean_113181409_logistic_regression.csv', index=False)

"""<h1> 5. </h1>
5. Energy usage data Analysis:
We want to analyze how different devices are being used in different times of the day.

- Is the washer being used only during the day?

- During what time of the day is AC used most?

There are a number of questions that can be asked.

For simplicity, let’s divide a day in two parts:

- Day: 6AM - 7PM

- Night: 7PM - 6AM

Analyze the usage of any two devices of your choice during the ‘day’ and ‘night’. Plot these trends. Explain your findings. (10 points)
"""

newEnergydf = pd.read_csv('energy_data.csv')
newEnergydf.describe()

newEnergydf.head()

#energydf['time'] = pd.to_datetime(energydf['time'])
newEnergydf = newEnergydf.rename(columns={'Date & Time': "time"})
newEnergydf['time'] = pd.to_datetime(newEnergydf['time'])

newEnergydf.head()

day_start = datetime.time(6, 0)
day_end = datetime.time(19, 0)

newEnergydf['time'] = ['day' if (x.time() > day_start and x.time() < day_end) else 'night' for x in newEnergydf['time']]

newEnergydf.head()

newEnergydf

#indexedByTimeNewEnergydf = newEnergydf.copy()
#indexedByTimeNewEnergydf = indexedByTimeNewEnergydf.set_index('time')
#newEnergydf['time'] = [1 if x >= 35 else 0 for x in logTest['time']]
#logTest['temperature'] = [1 if x >= 35 else 0 for x in logTest['temperature']]

#day_start = datetime.time(6, 0)
#time_close = datetime.time(19, 0)

#is_open = False

#if time_now >= time_open and time_now <= time_close:
#    is_open = True

#return is_open

#(indexedByTimeNewEnergydf.between_time('06:00:00', '19:00:00'))

#indexedByTimeNewEnergydf.reset_index();

newEnergydf['time'].value_counts()

"""<h1> Finding One: </h1>

Finding One: From this comparison of usage of first floor lights energy usage [kW] between the day and night, we can see that more energy [kW] is used on the lights during the night than during the day. The most likely reason is that the sun is out during the day which means that most people have less need to turn on the lights during the day as opposed to the night where people turn on the lights to see when the sun is not out.
"""

#sns.countplot(x='time', data = logTrain, palette='hls')
#sns.barplot(x = newEnergydf["time"], hue = "Academy", data= newEnergydf)
#sns.catplot(x='time',
#            y='use [kW]',
#            data=newEnergydf,
#            kind='bar');

#ax = sns.barplot(x="day", y="total_bill", hue="sex", data=tips)
#graph = sns.barplot(class)

sns.catplot(x='time', y='First Floor lights [kW]', data=newEnergydf, kind='bar');

# display
#plt.show()

"""<h1> Finding Two: </h1>

Finding Two: From this comparison of usage of AC energy usage [kW] between the day and night, we can see that more energy [kW] is used on the night than the day. This finding was quite surprising. I honestly thought that it would be the opposite way around where AC energy usage would be higher during the day because the sun is out warming up the air. Some possible explanations of this finding are that people are generally more active outside during the day so they have no need to turn on the AC because they are not home, or they find that sleeping when the temperature is hot and causing them to sweat is more difficult than simply chilling in the house generally resulting in them turning the AC on for the night but dealing with the heat during the day.
"""

#Home Office (R) [kW]
sns.catplot(x='time', y='AC [kW]', data=newEnergydf, kind='bar');

"""<h1> 6. </h1>
6. Visual Appeal and Layout - For all the tasks above, please include an explanation wherever asked and make sure that your procedure is documented (suitable comments) as good as you can.

Don’t forget to label all plots and include legends wherever necessary as this is key to making good visualizations! Ensure that the plots are visible enough by playing with size parameters. Be sure to use appropriate color schemes wherever possible to maximize the ease of understandability.

Everything must be laid out in a python notebook (.ipynb). (5 Point)
"""