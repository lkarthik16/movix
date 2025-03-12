// Fetch suggestions for autocomplete
function fetchSuggestions() {
    const query = document.getElementById('movieName').value;
    if (query.length > 2) {
        fetch(`/autocomplete/?q=${query}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Autocomplete data:', data); // Debugging
                const suggestions = document.getElementById('suggestions');
                suggestions.innerHTML = data.map(item => `
                    <div class="p-2 hover:bg-gray-700 cursor-pointer flex items-center">
                        <img src="${item.image}" alt="${item.title}" class="w-10 h-10 mr-2">
                        <div>
                            <p>${item.title}</p>
                            <p class="text-sm text-gray-400">${item.year}</p>
                        </div>
                    </div>
                `).join('');

                // Add click event listeners to suggestions
                suggestions.querySelectorAll('div').forEach(item => {
                    item.addEventListener('click', () => {
                        const movieTitle = item.querySelector('p').innerText;
                        document.getElementById('movieName').value = movieTitle;
                        suggestions.innerHTML = ''; // Clear suggestions
                        fetchMovieInfo(); // Fetch movie details
                    });
                });
            })
            .catch(error => {
                console.error('Error fetching suggestions:', error);
            });
    } else {
        document.getElementById('suggestions').innerHTML = '';
    }
}

// Fetch movie details
function fetchMovieInfo() {
    const movieName = document.getElementById('movieName').value;
    if (!movieName) {
        alert('Please enter a movie name.');
        return;
    }

    console.log('Fetching movie info for:', movieName); // Debugging

    fetch(`/search/?q=${movieName}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Movie data received:', data); // Debugging
            if (data.error) {
                alert(data.error);
            } else {
                document.getElementById('movieInfo').classList.remove('hidden');
                document.getElementById('movieImage').src = data.image_url;
                document.getElementById('movieTitle').innerText = data.title;
                document.getElementById('movieYear').innerText = data.year;
                document.getElementById('movieCast').innerText = data.cast.map(actor => actor.name).join(', ');
                document.getElementById('moviePlot').innerText = data.plot;
                document.getElementById('movieRating').innerText = data.ratings.rating;
                document.getElementById('imdbLink').href = data.imdb_url;
            }
        })
        .catch(error => {
            console.error('Error fetching movie info:', error);
            alert('Failed to fetch movie details. Please try again.');
        });
}