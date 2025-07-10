import requests
response = requests.get('https://www.crunchyroll.com/series/GRDV0019R/jujutsu-kaisen')
with open('in.html', 'w', encoding='utf-8') as file:
    file.write(response.text)