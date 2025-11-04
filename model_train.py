import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import random  

data = []
for i in range(100):
    traffic = random.randint(10,100)
    aqi = traffic + random.randint(0,100)
    data.append([traffic, aqi])
df = pd.DataFrame(data, columns=['traffic_density','air_quality_index'])

# Label: 1 = poor, 0 = good
df['label'] = df['air_quality_index'] > 150

X = df[['traffic_density']]
y = df['label']

X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2)
model = RandomForestClassifier().fit(X_train,y_train)

print("Model accuracy:", model.score(X_test,y_test))
joblib.dump(model,'traffic_model.pkl')
