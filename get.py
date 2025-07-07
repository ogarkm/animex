
import requests

response = requests.get(input('Enter URL to fetch HTML: '))
with open('output.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
