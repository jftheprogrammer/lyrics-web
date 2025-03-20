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
        const lyrics = document.getElementById('lyrics-input').value;
        await searchSong('lyrics', new FormData().append('lyrics', lyrics));
    });

    // Audio recording
    recordButton.addEventListener('click', async function() {
        if (!recorder.isRecording) {
            try {
                await recorder.startRecording();
                recordButton.innerHTML = '<i class="fas fa-stop"></i> Stop Recording';
                recordButton.classList.replace('btn-outline-primary', 'btn-danger');
                recordingStatus.textContent = 'Recording... (hum your melody)';
            } catch (error) {
                recordingStatus.textContent = 'Error: Could not access microphone';
            }
        } else {
            const audioBlob = await recorder.stopRecording();
            recordButton.innerHTML = '<i class="fas fa-microphone"></i> Start Recording';
            recordButton.classList.replace('btn-danger', 'btn-outline-primary');
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
                <div class="card mb-2">
                    <div class="card-body">
                        <h5 class="card-title">${match.title}</h5>
                        <h6 class="card-subtitle mb-2 text-muted">${match.artist}</h6>
                        <div class="progress">
                            <div class="progress-bar" role="progressbar" 
                                 style="width: ${match.confidence * 100}%"
                                 aria-valuenow="${match.confidence * 100}" 
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                                ${(match.confidence * 100).toFixed(1)}%
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');

            resultsList.innerHTML = matchesHtml;
        } catch (error) {
            loadingSpinner.classList.add('d-none');
            resultsList.innerHTML = '<div class="alert alert-danger">An error occurred while processing your request</div>';
        }
    }
});
