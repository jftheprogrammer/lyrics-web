import librosa
import numpy as np
import logging

def process_audio(audio_file):
    """
    Process audio file to extract melody features using librosa
    """
    try:
        # Load audio file
        y, sr = librosa.load(audio_file, sr=22050, duration=10)
        
        # Extract pitch features
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        
        # Get the most prominent pitch at each time
        pitch_features = []
        for t in range(pitches.shape[1]):
            pitches_t = pitches[:, t]
            magnitudes_t = magnitudes[:, t]
            if magnitudes_t.max() > 0:
                pitch_features.append(pitches_t[magnitudes_t.argmax()])
            else:
                pitch_features.append(0)
                
        # Normalize features
        pitch_features = np.array(pitch_features)
        if len(pitch_features) > 0:
            pitch_features = (pitch_features - pitch_features.mean()) / pitch_features.std()
            
        return pitch_features.tolist()
    except Exception as e:
        logging.error(f"Error processing audio: {str(e)}")
        raise
