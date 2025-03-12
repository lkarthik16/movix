import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings

def home(request):
    """
    Renders the home page.
    """
    return render(request, 'movixapp/index.html')

def search_movie(request):
    if request.method == 'GET':
        movie_name = request.GET.get('q', '')
        print(f"Searching for movie: {movie_name}")  # Debugging
        
        # Fetch data from IMDb API
        url = "https://imdb8.p.rapidapi.com/auto-complete"
        querystring = {"q": movie_name}
        headers = {
            "x-rapidapi-key": settings.IMDB_API_KEY,
            "x-rapidapi-host": "imdb8.p.rapidapi.com"
        }
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            data = response.json()
            print("API response:", data)  # Debugging
            
            if data and 'd' in data and data['d']:  # Check if data is not empty
                # Use the first result from the autocomplete response
                movie_data = data['d'][0]
                print("Movie data:", movie_data)  # Debugging
                
                # Extract IMDb ID (tconst)
                id_field = movie_data.get('id', '')
                print("ID field:", id_field)  # Debugging
                
                # Handle cases where the ID field is not in the expected format
                if id_field.startswith('/title/') and id_field.endswith('/'):
                    tconst = id_field.split('/')[2]  # Extract IMDb ID
                else:
                    # If the ID is not in the expected format, use it as-is
                    tconst = id_field
                
                print("IMDb ID (tconst):", tconst)  # Debugging
                
                # Fetch additional details
                cast = get_cast(tconst)
                plot = get_plot(tconst)
                ratings = get_ratings(tconst)
                print("Cast:", cast)  # Debugging
                print("Plot:", plot)  # Debugging
                print("Ratings:", ratings)  # Debugging
                
                # Combine all data (without runtime)
                movie_info = {
                    'title': movie_data.get('l', ''),  # Use 'l' for title
                    'year': movie_data.get('y', ''),   # Use 'y' for year
                    'image_url': movie_data.get('i', {}).get('imageUrl', ''),  # Use 'i' for image
                    'imdb_url': f"https://www.imdb.com/title/{tconst}/",
                    'cast': cast,
                    'plot': plot,
                    'ratings': ratings
                }
                
                return JsonResponse(movie_info)
            else:
                print("No movie data found in API response")  # Debugging
                return JsonResponse({'error': 'Movie not found'}, status=404)
        except requests.RequestException as e:
            print("API request failed:", e)  # Debugging
            return JsonResponse({'error': str(e)}, status=500)

def autocomplete(request):
    """
    Fetches autocomplete suggestions from the IMDb API based on the search query.
    """
    if request.method == 'GET':
        query = request.GET.get('q', '')
        url = "https://imdb8.p.rapidapi.com/auto-complete"
        querystring = {"q": query}
        headers = {
            "x-rapidapi-key": settings.IMDB_API_KEY,
            "x-rapidapi-host": "imdb8.p.rapidapi.com"
        }
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            data = response.json()
            
            # Handle the API response (which is a list)
            suggestions = []
            for item in data['d']:  # Iterate directly over the list
                suggestion = {
                    'title': item.get('l', ''),  # Movie title
                    'year': item.get('y', ''),   # Release year
                    'image': item.get('i', {}).get('imageUrl', '')  # Image URL
                }
                suggestions.append(suggestion)
            
            return JsonResponse(suggestions, safe=False)
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

# Helper functions for additional details
def get_cast(tconst):
    """
    Fetches the top cast members for a given IMDb ID (tconst).
    """
    url = "https://imdb8.p.rapidapi.com/title/get-top-cast"
    querystring = {"tconst": tconst}
    headers = {
        "x-rapidapi-key": settings.IMDB_API_KEY,
        "x-rapidapi-host": "imdb8.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        cast_ids = response.json()[:5]  # Limit to 5 cast members
        
        cast = []
        for cast_id in cast_ids:
            nconst = cast_id.split('/')[2]
            url = "https://imdb8.p.rapidapi.com/actors/get-bio"
            querystring = {"nconst": nconst}
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            cast_data = response.json()
            cast.append({
                'name': cast_data.get('name', ''),
                'image_url': cast_data.get('image', {}).get('url', '')
            })
        
        return cast
    except requests.RequestException:
        return []

def get_plot(tconst):
    """
    Fetches the plot summary for a given IMDb ID (tconst).
    """
    url = "https://imdb8.p.rapidapi.com/title/get-plots"
    querystring = {"tconst": tconst}
    headers = {
        "x-rapidapi-key": settings.IMDB_API_KEY,
        "x-rapidapi-host": "imdb8.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        return data.get('plots', [{}])[0].get('text', 'Plot not available')
    except requests.RequestException:
        return 'Plot not available'

def get_ratings(tconst):
    """
    Fetches the ratings for a given IMDb ID (tconst).
    """
    url = "https://imdb8.p.rapidapi.com/title/get-ratings"
    querystring = {"tconst": tconst}
    headers = {
        "x-rapidapi-key": settings.IMDB_API_KEY,
        "x-rapidapi-host": "imdb8.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {'rating': 'N/A'}