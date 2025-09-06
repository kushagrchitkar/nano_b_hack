import React, { useState, useEffect } from 'react';
import './ComicGenerator.css';
import ComicSlideshow from './ComicSlideshow';

interface PanelInfo {
  panel_number: number;
  image_url: string;
  scene_description: string;
  dialogue: string[];
  narration?: string;
}

interface ComicGenerationResponse {
  success: boolean;
  comic_path?: string;
  comic_url?: string;
  panels?: PanelInfo[];
  error?: string;
}

interface Quote {
  author: string;
  quote: string;
}

const ComicGenerator: React.FC = () => {
  const [eventDescription, setEventDescription] = useState('');
  const [style, setStyle] = useState('amar_chitra_katha');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedComic, setGeneratedComic] = useState<string | null>(null);
  const [panels, setPanels] = useState<PanelInfo[]>([]);
  const [showSlideshow, setShowSlideshow] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [currentQuote, setCurrentQuote] = useState<Quote | null>(null);

  // Load quotes on component mount
  useEffect(() => {
    const loadQuotes = async () => {
      try {
        const response = await fetch('/quotes.json');
        const data = await response.json();
        setQuotes(data.quotes);
      } catch (err) {
        console.error('Failed to load quotes:', err);
      }
    };
    loadQuotes();
  }, []);

  // Cycle through quotes while generating
  useEffect(() => {
    if (isGenerating && quotes.length > 0) {
      const getRandomQuote = () => {
        const randomIndex = Math.floor(Math.random() * quotes.length);
        return quotes[randomIndex];
      };

      // Set initial random quote
      setCurrentQuote(getRandomQuote());

      // Change quote every 3 seconds while generating
      const interval = setInterval(() => {
        setCurrentQuote(getRandomQuote());
      }, 3000);

      return () => clearInterval(interval);
    } else {
      setCurrentQuote(null);
    }
  }, [isGenerating, quotes]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!eventDescription.trim()) {
      setError('Please enter an event description');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGeneratedComic(null);
    setPanels([]);

    try {
      // Use synchronous endpoint for slideshow functionality
      const response = await fetch(`http://localhost:8001/api/generate-comic-sync?event=${encodeURIComponent(eventDescription)}&style=${style}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ComicGenerationResponse = await response.json();

      if (data.success && data.comic_url && data.panels) {
        setGeneratedComic(`http://localhost:8001${data.comic_url}`);
        setPanels(data.panels);
        setShowSlideshow(true);
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
    setPanels([]);
    setShowSlideshow(false);
    setError(null);
  };

  const handleCloseSlideshow = () => {
    setShowSlideshow(false);
  };

  const handleViewFinalComic = () => {
    setShowSlideshow(false);
    // generatedComic state is already set, so the final comic will display
  };

  return (
    <div className={`comic-generator style-${style}`}>
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
          {currentQuote && (
            <div className="quote-display">
              <blockquote>"{currentQuote.quote}"</blockquote>
              <cite>— {currentQuote.author}</cite>
            </div>
          )}
          <p>Generating your comic... This may take a few moments.</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}

      {generatedComic && !showSlideshow && (
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
            <button
              onClick={() => setShowSlideshow(true)}
              className="replay-slideshow-btn"
              disabled={!panels.length}
            >
              Replay Slideshow
            </button>
          </div>
        </div>
      )}

      {showSlideshow && panels.length > 0 && generatedComic && (
        <ComicSlideshow
          panels={panels}
          finalComicUrl={generatedComic}
          onClose={handleCloseSlideshow}
          onViewFinalComic={handleViewFinalComic}
        />
      )}
    </div>
  );
};

export default ComicGenerator;