import requests

query = '''
query ($malId: Int) {
  Media(idMal: $malId, type: ANIME) {
    id
    bannerImage
    coverImage {
      extraLarge
      large
      medium
    }
  }
}
'''
variables = {'malId': 52299}  # Example MAL ID for One Piece
response = requests.post(
    'https://graphql.anilist.co',
    json={'query': query, 'variables': variables}
)
print(response.json())
