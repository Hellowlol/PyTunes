from bs4 import BeautifulSoup
import urllib2
from imdb import IMDb

def Top250(page=0, limit=30):
    top250 = []
    response = urllib2.urlopen('http://akas.imdb.com/chart/top')
    html = response.read()


    soup = BeautifulSoup(html)
    table = soup.find("tbody", "lister-list")

    for row in table.find_all('tr'):
        movie = {}
        #if row.find('td', {'class' : 'titleColumn'}):
        movie['title'] = (row.find('td', {'class' : 'titleColumn'})).a.string
        movie['rank'] = row.find('span', {'name' : 'ir'}).string.strip('.')
        movie['year'] = row.find('span', {'name' : 'rd'}).string.strip('(').strip(')')
        movie['thumb'] = row.find('img')['src'].split('_V1')[0] + 'jpg'
        movie['release_date'] = row.find('span', {'name' : 'rd'})['data-value']
        movie['rating'] = row.find('strong', {'name' : 'nv'}).string
        movie['votes'] = row.find('strong', {'name' : 'nv'})['data-value']
        movie['imdbid'] = row.find('div', {'class' : 'rating rating-list'})['id'].split('|')[0]
        top250.append(movie)

    return top250[page*limit:((page+1)*limit)-1]


