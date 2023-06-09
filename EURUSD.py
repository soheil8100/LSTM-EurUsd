
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import *
from tensorflow.keras.callbacks import EarlyStopping

from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.model_selection import train_test_split
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error

from sklearn import metrics
from io import BytesIO
from datetime import datetime


"""# Data Preprocessing"""

def Data_preprocessing(DataBaseName, nLastRow):

  df33 = pd.read_csv( DataBaseName, header= None, encoding='utf-16')
  
  nLen1 = len(df33)
  stock_data = df33[df33.index > (nLen1 - nLastRow)]
  X_feat =stock_data.iloc[:,1:5]
  X_feat.index = stock_data[0].values
  print("Index hast" + X_feat.index)
  return X_feat

"""# Train and Test Sets for Stock Price Prediction"""

def lstm_split(data, nRowsBack , n_steps):
  X,y = [], []
  print(len(data))
  for i in range(len(data) - n_steps + 1 - nRowsBack):
    X.append(data[i:i + n_steps, :-1])
    y.append(data[i + n_steps-1, -1])
  return np.array(X),np.array(y)
    
"""# Split it into training and testing sets"""

def Train_test_set_func(df_values, n_steps, nRowsBack):
  


  #n_steps = 10
  X1, y1 = lstm_split(df_values.values, nRowsBack , n_steps=n_steps)
  train_split = 0.8
  split_idx = int(np.ceil(len(X1) * train_split))
  date_index = df_values.index

  X_train, X_test = X1[:split_idx], X1[split_idx:]
  y_train, y_test = y1[:split_idx], y1[split_idx:]
  x_train_date, x_test_date = date_index[:split_idx], date_index[split_idx:-n_steps+1]
  
  return X_train, X_test,y_train, y_test, x_train_date, x_test_date

"""# Building the LSTM model

# Second Performance Evaluation on Test Set
"""

def Bulding_Lstm_Layer_2S(X_train,nmNode, Layer_s):
#from tensorflow.keras.optimizers import Adam
  lstm = Sequential()

  if Layer_s > 1:
    lstm.add(LSTM(nmNode, input_shape = (X_train.shape[1], X_train.shape[2]), activation='relu', return_sequences= True ))
    lstm.add(LSTM(nmNode, activation='relu'))
  else:
    
    lstm.add(LSTM(nmNode, input_shape = (X_train.shape[1], X_train.shape[2]), activation='relu', return_sequences= False ))
    #lstm.add(Dropout(0.9))


  lstm.add(Dense(1))
  lstm.compile(loss = 'mean_squared_error', optimizer = 'adam')
  #lstm.compile(loss = 'mean_squared_error',  optimizer=Adam(learning_rate=0.001))
  lstm.summary()

  history = lstm.fit(X_train,y_train,
                   epochs = 100, batch_size = 4,
                   verbose = 2, shuffle = False)
  y_pred = lstm.predict(X_test) #Predicting the Test set results With n=2

  rmse = mean_squared_error(y_test, y_pred, squared= False)
  mape = mean_absolute_percentage_error(y_test, y_pred)

  return y_pred, rmse ,mape

"""# search in Database for find best prediction"""

n_Canedl = [4,6] 
nodeLstm_s = 32
nlayer_s = 2
nSearchBackInDB = 1 
nLastRowInDatabase = 1000 
databaseNamn ='EURUSDM15.csv'


df = Data_preprocessing(databaseNamn, nLastRowInDatabase)
df_info = pd.DataFrame({'Candel':[],
                        'RMSE':[],
                        'MAPE':[],
                        'Predict':[],
                        'Actual':[],
                        'Date':[]
                        })
                 
for idb in range(nSearchBackInDB):
 # print ('DataSet Length:', len(df),'------ n:', i_inCandel, '---------- LSTM Layer:', nlayer_s, '----- Back in DB:', nSearchBackInDB)
  

  for i_inCandel in n_Canedl:
    print ('DataSet Length:', len(df),'------ n:', i_inCandel, '---------- LSTM Layer:', nlayer_s, '----- Back in DB:', idb)
    X_train, X_test, y_train, y_test, x_train_date, x_test_date = Train_test_set_func(df, i_inCandel, idb)

    if nlayer_s > 1:
      y_pred, rmse, mape = Bulding_Lstm_Layer_2S(X_train, nodeLstm_s,nlayer_s)
    else:
      y_pred, rmse, mape = Bulding_Lstm_Layer_2S(X_train, nodeLstm_s,nlayer_s)

    print(np.concatenate((y_pred.reshape(len(y_pred),1), y_test.reshape(len(y_test),1)),1))
    print('RMSE: {:.5f} '.format(rmse))
    print('MAPE: {:.5f}'.format(mape))
    Info_LSTM_node = 'RMSE: {:.5f} '.format(rmse),'--', 'MAPE: {:.5f}'.format(mape)
    df_info = df_info.append({'Candel':str(i_inCandel),
                            'RMSE':str('{:.5f}'.format(rmse)),
                            'MAPE':str('{:.5f}'.format(mape)),
                            'Predict':str(y_pred[len(y_pred)-1])[1:8],
                            'Actual':str(y_test[len(y_test)-1])[0:8],
                            'Date':x_test_date[len(x_test_date)-1-idb]
                            },ignore_index=True)

#print('df_info\n',df_info)
#test_soheil(x_test_date)
print('Database:',databaseNamn)

print (df_info)


now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)