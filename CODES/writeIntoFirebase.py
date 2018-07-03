#TO WRITE THE PRODUCT LIST 'productsList.csv' INTO FIREBASE REALTIME DATABSE

#sudo pip3 install apyori
#sudo pip3 install requests==1.1.0
#sudo pip3 install python-firebase
#sudo pip3 install requests --upgrade

from firebase.firebase import FirebaseApplication
from firebase.firebase import FirebaseAuthentication
import pandas as pd
auth = FirebaseAuthentication('<FIREBASE AUTH>', '<GMAIL USERID>')
app = FirebaseApplication('<LINK TO FIREBASE APP>', authentication=auth)

inputCSV = pd.read_csv('./productsList.csv',header=None)

numberOfRows = inputCSV.shape[0]
numberOfCols = inputCSV.shape[1]
headings = ['name','category','cost','quantity','garbage']
productDetails = {}
for i in range(numberOfRows):
    key = '/product/'+inputCSV.iloc[i,0]    
    for j in range(1,6):
        if(j == 3 or j == 4):
            productDetails[headings[j-1]] = int(inputCSV.iloc[i,j])
        else:
            productDetails[headings[j-1]] = str(inputCSV.iloc[i,j])
    print(key,productDetails)
    app.put('', key, productDetails)
