document.addEventListener('DOMContentLoaded', function() {
    const recorder = new AudioRecorder();
    const recordButton = document.getElementById('record-button');
    const recordingStatus = document.getElementById('recording-status');
    const resultsSection = document.getElementById('results-section');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultsList = document.getElementById('results-list');

    // Lyrics form submission
    document.getElementById('lyrics-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        console.log('Form submitted');

        const lyrics = document.getElementById('lyrics-input').value.trim();
        console.log('Lyrics:', lyrics);

        if (!lyrics) {
            resultsList.innerHTML = '<div class="alert alert-danger">Please enter some lyrics</div>';
            return;
        }

        resultsSection.classList.remove('d-none');
        loadingSpinner.classList.remove('d-none');
        resultsList.innerHTML = '';

        const formData = new FormData();
        formData.append('lyrics', lyrics);

        try {
            const response = await fetch('/match_lyrics', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            console.log('Response:', data);

            loadingSpinner.classList.add('d-none');

            if (data.error) {
                resultsList.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                return;
            }

            if (!data.matches || data.matches.length === 0) {
                resultsList.innerHTML = '<div class="alert alert-info">No matches found</div>';
                return;
            }

            const matchesHtml = data.matches.map(match => `
                <div class="col-md-6 mb-4">
                    <div class="card result-card h-100">
                        <div class="position-relative">
                            ${match.artwork_url ? 
                                `<img src="${match.artwork_url}" class="album-artwork" alt="${match.title} artwork">` :
                                `<div class="album-artwork bg-secondary d-flex align-items-center justify-content-center">
                                    <i class="fas fa-music fa-3x text-white"></i>
                                </div>`
                            }
                            <span class="match-confidence">${(match.confidence * 100).toFixed(1)}% Match</span>
                        </div>
                        <div class="card-body">
                            <h5 class="card-title">${match.title}</h5>
                            <h6 class="card-subtitle mb-2 text-muted">${match.artist}</h6>
                            ${match.album ? `<p class="card-text">Album: ${match.album}</p>` : ''}
                            ${match.release_year ? `<p class="card-text">Year: ${match.release_year}</p>` : ''}
                        </div>
                        <div class="card-footer bg-transparent">
                            <div class="streaming-links">
                                ${Object.entries(match.streaming_urls || {}).map(([platform, url]) => `
                                    <a href="${url}" target="_blank" title="Listen on ${platform}">
                                        <i class="fab fa-${platform.toLowerCase()}"></i>
                                    </a>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

            resultsList.innerHTML = `<div class="row">${matchesHtml}</div>`;
        } catch (error) {
            console.error('Error:', error);
            loadingSpinner.classList.add('d-none');
            resultsList.innerHTML = '<div class="alert alert-danger">An error occurred while processing your request</div>';
        }
    });

    // Audio recording
    recordButton.addEventListener('click', async function() {
        if (!recorder.isRecording) {
            try {
                await recorder.startRecording();
                recordButton.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
                recordButton.classList.replace('btn-outline-primary', 'btn-danger');
                recordButton.classList.add('recording');
                recordingStatus.textContent = 'Recording... (hum your melody)';
            } catch (error) {
                recordingStatus.textContent = 'Error: Could not access microphone';
            }
        } else {
            const audioBlob = await recorder.stopRecording();
            recordButton.innerHTML = '<i class="fas fa-microphone"></i> Start Recording';
            recordButton.classList.replace('btn-danger', 'btn-outline-primary');
            recordButton.classList.remove('recording');
            recordingStatus.textContent = 'Processing...';

            const formData = new FormData();
            formData.append('audio', audioBlob);
            await searchSong('melody', formData);
        }
    });

    async function searchSong(type, formData) {
        resultsSection.classList.remove('d-none');
        loadingSpinner.classList.remove('d-none');
        resultsList.innerHTML = '';

        try {
            const response = await fetch(`/match_${type}`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            loadingSpinner.classList.add('d-none');

            if (data.error) {
                resultsList.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                return;
            }

            if (data.matches.length === 0) {
                resultsList.innerHTML = '<div class="alert alert-info">No matches found</div>';
                return;
            }

            const matchesHtml = data.matches.map(match => `
                <div class="col-md-6 mb-4">
                    <div class="card result-card h-100">
                        <div class="position-relative">
                            ${match.artwork_url ? 
                                `<img src="${match.artwork_url}" class="album-artwork" alt="${match.title} artwork">` :
                                `<div class="album-artwork bg-secondary d-flex align-items-center justify-content-center">
                                    <i class="fas fa-music fa-3x text-white"></i>
                                </div>`
                            }
                            <span class="match-confidence">${(match.confidence * 100).toFixed(1)}% Match</span>
                        </div>
                        <div class="card-body">
                            <h5 class="card-title">${match.title}</h5>
                            <h6 class="card-subtitle mb-2 text-muted">${match.artist}</h6>
                            ${match.album ? `<p class="card-text">Album: ${match.album}</p>` : ''}
                            ${match.release_year ? `<p class="card-text">Year: ${match.release_year}</p>` : ''}
                        </div>
                        <div class="card-footer bg-transparent">
                            <div class="d-flex justify-content-between align-items-center">
                                <button class="btn btn-sm btn-outline-primary favorite-btn" 
                                        data-song-id="${match.id}"
                                        onclick="toggleFavorite(${match.id}, this)">
                                    <i class="fas fa-heart"></i> Favorite
                                </button>
                                <div class="streaming-links">
                                    ${Object.entries(match.streaming_urls || {}).map(([platform, url]) => `
                                        <a href="${url}" target="_blank" title="Listen on ${platform}">
                                            <i class="fab fa-${platform.toLowerCase()}"></i>
                                        </a>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

            resultsList.innerHTML = `<div class="row">${matchesHtml}</div>`;
            initializeFavoriteButtons();
        } catch (error) {
            loadingSpinner.classList.add('d-none');
            resultsList.innerHTML = '<div class="alert alert-danger">An error occurred while processing your request</div>';
        }
    }

    function initializeFavoriteButtons() {
        document.querySelectorAll('.favorite-btn').forEach(btn => {
            const songId = btn.dataset.songId;
            checkFavoriteStatus(songId, btn);
        });
    }

    async function toggleFavorite(songId, button) {
        try {
            const response = await fetch(`/favorite/${songId}`, { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                button.classList.toggle('btn-outline-primary', !data.is_favorite);
                button.classList.toggle('btn-primary', data.is_favorite);
                button.innerHTML = `<i class="fas fa-heart"></i> ${data.is_favorite ? 'Favorited' : 'Favorite'}`;
            }
        } catch (error) {
            console.error('Error toggling favorite:', error);
        }
    }

    async function checkFavoriteStatus(songId, button) {
        try {
            const response = await fetch(`/favorite/status/${songId}`);
            const data = await response.json();

            if (data.is_favorite) {
                button.classList.remove('btn-outline-primary');
                button.classList.add('btn-primary');
                button.innerHTML = '<i class="fas fa-heart"></i> Favorited';
            }
        } catch (error) {
            console.error('Error checking favorite status:', error);
        }
    }
});