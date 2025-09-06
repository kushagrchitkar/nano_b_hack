import React, { useState } from 'react';
import './ComicGenerator.css';

interface ComicGenerationResponse {
  success: boolean;
  comic_path?: string;
  comic_url?: string;
  error?: string;
}

const ComicGenerator: React.FC = () => {
  const [eventDescription, setEventDescription] = useState('');
  const [style, setStyle] = useState('amar_chitra_katha');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedComic, setGeneratedComic] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!eventDescription.trim()) {
      setError('Please enter an event description');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGeneratedComic(null);

    try {
      // Use synchronous endpoint for simplicity
      const response = await fetch(`http://localhost:8001/api/generate-comic-sync?event=${encodeURIComponent(eventDescription)}&style=${style}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ComicGenerationResponse = await response.json();

      if (data.success && data.comic_url) {
        setGeneratedComic(`http://localhost:8001${data.comic_url}`);
      } else {
        setError(data.error || 'Failed to generate comic');
      }
    } catch (err) {
      setError('Network error occurred while generating comic. Make sure the FastAPI server is running on port 8001.');
      console.error('Comic generation error:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleReset = () => {
    setEventDescription('');
    setStyle('amar_chitra_katha');
    setGeneratedComic(null);
    setError(null);
  };

  return (
    <div className="comic-generator">
      <div className="generator-form">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="event">Event Description:</label>
            <textarea
              id="event"
              value={eventDescription}
              onChange={(e) => setEventDescription(e.target.value)}
              placeholder="Enter a historical event or story (e.g., 'birth of Alexander the Great', 'discovery of fire')"
              rows={3}
              disabled={isGenerating}
            />
          </div>

          <div className="form-group">
            <label htmlFor="style">Comic Style:</label>
            <select
              id="style"
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              disabled={isGenerating}
            >
              <option value="amar_chitra_katha">Amar Chitra Katha</option>
              <option value="xkcd">XKCD</option>
            </select>
          </div>

          <div className="form-actions">
            <button
              type="submit"
              disabled={isGenerating || !eventDescription.trim()}
              className="generate-btn"
            >
              {isGenerating ? 'Generating Comic...' : 'Generate Comic'}
            </button>
            <button
              type="button"
              onClick={handleReset}
              disabled={isGenerating}
              className="reset-btn"
            >
              Reset
            </button>
          </div>
        </form>
      </div>

      {isGenerating && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Generating your comic... This may take a few moments.</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}

      {generatedComic && (
        <div className="comic-result">
          <h3>Your Generated Comic</h3>
          <div className="comic-display">
            <img
              src={generatedComic}
              alt="Generated comic"
              className="comic-image"
            />
          </div>
          <div className="comic-actions">
            <a
              href={generatedComic}
              download
              className="download-btn"
            >
              Download Comic
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComicGenerator;