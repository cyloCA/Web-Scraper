import requests
from requests import get        #Send HTTP requests to get HTML files
from bs4 import BeautifulSoup   #Parse HTML files
import pandas as pd             #Clean data and insert into dataframe
import numpy as np

from time import sleep
from random import randint

#Make sure we get back english translated titles
headers = {"Accept-Language": "en-US, en;q=0.5"}

#Lists containing data that we want extracted
titles = []
years = []
duration = []
ratings = []
metascores = []
votes = []
grossTotal = []

#Page numbers to get all 1000 movies out
#Arrange(start, stop, step size) there are 50 movies per page
pages = np.arange(1, 1001, 50)

#Iterate through all the pages till we reach the last movie #1000
for currentPage in pages:

    #Add the str(currentPage) to iterate over a number of data
    #on the same page and scrape everything back in English
    currentPage = requests.get("https://www.imdb.com/search/title/?groups=top_1000&start=" + str(currentPage) + "&ref_=adv_nxt", headers=headers)
    
    #Parse data from the requests sent back from URL into text format
    #of the entire page rather than a long string
    readData = BeautifulSoup(currentPage.text, "html.parser")

    #Data is contained in a specified div class, parse the data only from
    #the class specified attribute
    movieDiv = readData.find_all('div', class_='lister-item mode-advanced')

    #Control crawl rate of sent requests in a range of seconds
    sleep(randint(2,10))

    #Extract each item by getting data from each class attribute
    for data in movieDiv:

        #Movie titles are contained within a h3 tag and a nested a tag extract
        #data in text format and store to titles list
        movieTitles = data.h3.a.text
        titles.append(movieTitles)
        
        #Movie year is in a span tag within the h3 tag
        #Identify the span class attribute
        movieYear = data.h3.find('span', class_='lister-item-year').text
        years.append(movieYear)

        #Movie duration in a span tag within a p tag
        #Error check to make sure all movies have a duration if not put a '-' instead
        #but still grab the data
        movieDuration = data.p.find('span', class_='runtime').text if data.find('span', class_='runtime') else '-'
        duration.append(movieDuration)

        #Movie rating within a strong tag but the rating shows up as a decimal
        #therefore we must convert to a float
        movieRating = float(data.strong.text)
        ratings.append(movieRating)

        #Movie metascore within a span tag
        movieMetascore = data.find('span', class_='metascore').text if data.find('span', class_='metascore') else '-'
        metascores.append(movieMetascore)
        print(metascores)

        #Movie votes are in a span tag named 'nv' within the p tag
        #but gross total is also in the same span tag name therefore we must index and point
        #at the first and second data in the list accordingly
        nv = data.find_all('span', attrs={'name': 'nv'})
        movieVote = nv[0].text
        votes.append(movieVote)

        #First movie in the list does not have a total so we have to create a case to put '-'
        #otherwise we get an error
        movieTotal = nv[1].text if len(nv) > 1 else '-'
        grossTotal.append(movieTotal)

#Clean up data and put into DataFrame
movies = pd.DataFrame({
    'Movie': titles,
    'Year': years,
    'Duration': duration,
    'Rating': ratings,
    'Metascore': metascores,
    'Votes': votes,
    'Gross Total (Millions)': grossTotal,
})

#Cleaning data with Pandas correcting datatypes
#Parse only the digits for year and not the brackets and display as an integer
movies['Year'] = movies['Year'].str.extract('(\d+)').astype(int)

#Duration as an integer extract all digits
movies['Duration'] = movies['Duration'].str.extract('(\d+)').astype(int)

#Metscore as an integer extract all digits
#Change all data in column as a float and change all movies without a metascore
#from '-' to NaN
movies['Metascore'] = movies['Metascore'].str.extract('(\d+)')
movies['Metascore'] = pd.to_numeric(movies['Metascore'], errors='coerce')

#Votes as an integer without the comma
movies['Votes'] = movies['Votes'].str.replace(',', '').astype(int)

#Get rid of the $ and M sign from the total
#Movies without a total will get a NaN
movies['Gross Total (Millions)'] = movies['Gross Total (Millions)'].map(lambda x: x.lstrip('$').rstrip('M'))
movies['Gross Total (Millions)'] = pd.to_numeric(movies['Gross Total (Millions)'], errors='coerce')

#Check data
print(movies)

#Check datatypes
print(movies.dtypes)

#Check to see if we are missing data and where we are missing data (NaN cases)
print(movies.isnull().sum())

#Export data to CSV file you created
movies.to_csv('movies.csv')
