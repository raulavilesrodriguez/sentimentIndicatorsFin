import os
from GoogleNews import GoogleNews
from textblob import TextBlob
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from openbb import obb


pd.options.plotting.backend="plotly"

obb.user.preferences.output_type = "dataframe"

def get_stock_data(symbol, start_date=None, end_date=None):
    data = obb.equity.price.historical(
        symbol,
        start_date=start_date,
        end_date=end_date,
        provider="yfinance",
    )
    data.reset_index(inplace=True)
    return data


def get_data(name):
    
    file_path = os.path.join("name.csv")
    
    return pd.read_csv(
        file_path,
        index_col="date"
    )

def sentiment_actif(actif, date_mesure):
  #date in format "mm/dd/yyyy"
  time.sleep(30)
  
  googlenews=GoogleNews()
  googlenews.set_time_range(date_mesure,date_mesure)
  googlenews.search(actif)
  news=googlenews.results()
  
  #calculo
  sentiment_score=[]
  for elt in news:
    text=TextBlob(elt['title'])
    sentiment_score.append(text.sentiment.polarity)
  
  neg_value=len(list(filter(lambda x: (x < 0), sentiment_score)))
  pos_value=len(list(filter(lambda x: (x >= 0), sentiment_score)))

  if pos_value>neg_value:
    pos_neg=1
  else:
    if pos_value==neg_value:
      pos_neg=0
    else:
      pos_neg=-1
  
  return (sum(sentiment_score)/len(sentiment_score),pos_neg)


def conversion_date(date_c):
  #from "YYY-MM-DD" to "MM-DD-YYY"
  return date_c.strftime("%m/%d/%Y")


def prix_actif_sentiment(actif, ticker, date_debut, date_fin):
  
  df= get_stock_data(ticker, date_debut, date_fin)
  
  df["Date_mesure"]=df.apply(lambda x: conversion_date(x["date"]),axis=1)
  
  df["sentiment_score_avg"]=df.apply(lambda x: sentiment_actif(actif, x["Date_mesure"])[0],axis=1)

  df["sentiment_score_maj"]=df.apply(lambda x: sentiment_actif(actif, x["Date_mesure"])[1],axis=1)
  
  file_path = os.path.join("btc.csv")
  df.to_csv(file_path, index=True)
  
  return df.set_index("date")


mydf=prix_actif_sentiment("bitcoin","BTC-USD","2022-10-01","2022-10-04")


print(mydf)
print(list(mydf.columns))

row=mydf.to_csv(index=False)

with open('sentiment_prix.csv','w') as fd:
    fd.write(row)


mydf2 = pd.read_csv('sentiment_prix.csv')
mydf2 = mydf2.set_index("date")
mydf2.drop("Date_mesure", axis=1, inplace=True)
print(mydf2)
print(mydf.dtypes)
## Correlation of price
mydf2.corr()



# PLOT Results
mydf.sort_index()
# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add traces
fig.add_trace(
    go.Scatter(x=mydf.index, y=mydf["close"], name="Price"),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=mydf.index, y=mydf["sentiment_score_avg"], name="Sentiment"),
    secondary_y=True,
)

# Add figure title
fig.update_layout(
    title_text="Price Stock vs Sentiment"
)

# Set x-axis title
fig.update_xaxes(title_text="Date")

# Set y-axes titles
fig.update_yaxes(title_text="Price", secondary_y=False)
fig.update_yaxes(title_text="Sentiment", secondary_y=True)

fig.show()


