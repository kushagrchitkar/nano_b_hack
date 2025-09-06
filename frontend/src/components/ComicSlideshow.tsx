import React, { useState, useEffect } from 'react';
import './ComicSlideshow.css';

interface PanelInfo {
  panel_number: number;
  image_url: string;
  scene_description: string;
  dialogue: string[];
  narration?: string;
}

interface ComicSlideshowProps {
  panels: PanelInfo[];
  finalComicUrl: string;
  onClose: () => void;
  onViewFinalComic: () => void;
}

const ComicSlideshow: React.FC<ComicSlideshowProps> = ({
  panels,
  finalComicUrl,
  onClose,
  onViewFinalComic
}) => {
  const [currentPanelIndex, setCurrentPanelIndex] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [showSlideshow, setShowSlideshow] = useState(false);

  useEffect(() => {
    // Start with black screen, then show first panel after brief delay
    const timer = setTimeout(() => {
      setShowSlideshow(true);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    // Focus on the overlay when it mounts to enable keyboard navigation
    const focusOverlay = () => {
      const overlay = document.querySelector('.comic-slideshow-overlay') as HTMLElement;
      if (overlay) {
        overlay.focus();
      }
    };
    
    if (showSlideshow) {
      setTimeout(focusOverlay, 100);
    }
  }, [showSlideshow]);

  const handleNext = () => {
    console.log('Next clicked, current index:', currentPanelIndex, 'total panels:', panels.length);
    if (isTransitioning) return;
    
    if (currentPanelIndex < panels.length - 1) {
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentPanelIndex(currentPanelIndex + 1);
        setIsTransitioning(false);
      }, 300);
    } else {
      // Last panel - show final comic
      onViewFinalComic();
    }
  };

  const handlePrevious = () => {
    console.log('Previous clicked, current index:', currentPanelIndex);
    if (isTransitioning || currentPanelIndex === 0) return;
    
    setIsTransitioning(true);
    setTimeout(() => {
      setCurrentPanelIndex(currentPanelIndex - 1);
      setIsTransitioning(false);
    }, 300);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    console.log('Key pressed:', e.key); // Debug log
    if (e.key === 'ArrowRight' || e.key === ' ') {
      e.preventDefault();
      e.stopPropagation();
      handleNext();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      e.stopPropagation();
      handlePrevious();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      e.stopPropagation();
      onClose();
    }
  };

  if (!panels.length) {
    return null;
  }

  const currentPanel = panels[currentPanelIndex];
  const isLastPanel = currentPanelIndex === panels.length - 1;

  return (
    <div 
      className="comic-slideshow-overlay"
      onClick={onClose}
      onKeyDown={handleKeyPress}
      tabIndex={0}
    >
      <div className="comic-slideshow-container" onClick={(e) => e.stopPropagation()}>
        
        {/* Close button */}
        <button className="slideshow-close-btn" onClick={onClose}>
          ✕
        </button>

        {/* Panel display area */}
        <div className="panel-display-area">
          {showSlideshow && (
            <div className={`panel-image-container ${isTransitioning ? 'transitioning' : ''}`}>
              <img
                src={`http://localhost:8001${currentPanel.image_url}`}
                alt={`Panel ${currentPanel.panel_number}`}
                className="panel-image"
              />
            </div>
          )}
        </div>

        {/* Panel info */}
        {showSlideshow && (
          <div className="panel-info">
            <div className="panel-counter">
              Panel {currentPanel.panel_number} of {panels.length}
            </div>
            
            {currentPanel.scene_description && (
              <div className="scene-description">
                {currentPanel.scene_description}
              </div>
            )}
            
            {currentPanel.dialogue.length > 0 && (
              <div className="dialogue-section">
                {currentPanel.dialogue.map((line, index) => (
                  <div key={index} className="dialogue-line">
                    "{line}"
                  </div>
                ))}
              </div>
            )}
            
            {currentPanel.narration && (
              <div className="narration-section">
                <em>{currentPanel.narration}</em>
              </div>
            )}
          </div>
        )}

        {/* Navigation controls */}
        {showSlideshow && (
          <div className="slideshow-navigation">
            <button 
              className="nav-btn nav-btn-prev"
              onClick={handlePrevious}
              disabled={currentPanelIndex === 0 || isTransitioning}
            >
              ← Previous
            </button>
            
            <button 
              className="nav-btn nav-btn-next"
              onClick={handleNext}
              disabled={isTransitioning}
            >
              {isLastPanel ? 'View Full Comic →' : 'Next →'}
            </button>
          </div>
        )}

        {/* Instructions */}
        {showSlideshow && (
          <div className="slideshow-instructions">
            Use arrow keys or buttons to navigate • Press Esc to close
          </div>
        )}
      </div>
    </div>
  );
};

export default ComicSlideshow;