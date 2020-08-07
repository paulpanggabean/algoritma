from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__) #don't change this code

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    table = soup.find('table', attrs={'class':'centerText newsTable2'})
    tr = table.find_all('tr')

    temp = [] #initiating a tuple

    for i in range(1, len(tr)):
        row = table.find_all('tr')[i]
    
        #get tanggal
        tanggal = row.find_all('td')[0].text
        tanggal = tanggal.strip().replace('\xa0','/').replace('/','-').replace('Juli','07').replace('Agustus','08') #for removing the excess whitespace

        #get ask
        ask = row.find_all('td')[1].text
        ask = ask.strip().replace(',','.') #for removing the excess whitespace

        #get bid
        bid = row.find_all('td')[2].text
        bid = bid.strip().replace(',','.') #for removing the excess whitespace

        temp.append((tanggal,ask,bid))  #append the needed information 
    
        temp = temp[::-1] #remove the header

    df = pd.DataFrame(temp, columns = ('tanggal','ask','bid')) #creating the dataframe
   #data wranggling -  try to change the data type to right data type
    df['tanggal'] = pd.to_datetime(df['tanggal'], dayfirst=True)
    df[['ask','bid']] = df[['ask','bid']].apply(lambda x: x.astype('float64'))
   #end of data wranggling

    return df

@app.route("/")
def index():
    df = scrap('https://news.mifx.com/kurs-valuta-asing?kurs=JPY') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.pivot_table(index='tanggal',values=['ask', 'bid'],aggfunc='max').head().plot(kind='line')
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
