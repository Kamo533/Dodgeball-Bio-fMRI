
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn import tree

col_names = ['Game', 'Precision', 'Pick-up time', 'Throw time', 'Ball hold', 'Throw distance', 'Throw angle', 'Rotation change', 'Opponent observation', 'Approach', 'Retreat', 'Aggressive movements', 'Defensive movements', 'Hiding', 'Court half favor', 'Middle court favor', 'Agent distance', 'Game duration', 'label']
# load dataset
data = pd.read_csv("PlaystyleData.csv", header=None, names=col_names)
print(data.head())

# split dataset in features and target variable
feature_cols = ['Precision', 'Pick-up time', 'Throw time', 'Ball hold', 'Throw distance', 'Rotation change', 'Opponent observation', 'Approach', 'Retreat', 'Aggressive movements', 'Defensive movements', 'Hiding', 'Court half favor', 'Middle court favor', 'Agent distance']
X = data[feature_cols] # Features
y = data.label # Target variable

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1) # 70% training and 30% test

# Create Decision Tree classifer object
clf = DecisionTreeClassifier()

# Train Decision Tree Classifer
clf = clf.fit(X_train,y_train)

# Predict the response for test dataset
y_pred = clf.predict(X_test)

# Model Accuracy, how often is the classifier correct?
print("Accuracy:", metrics.accuracy_score(y_test, y_pred))

text_representation = tree.export_text(clf)
print(text_representation)




# Game,Precision,Pick-up time,Throw time,Ball hold,Throw distance,Throw angle,Rotation change,Opponent observation,Approach,Retreat,Aggressive movements,Defensive movements,Hiding,Court half favor,Middle court favor,Agent distance,Game duration,Label
