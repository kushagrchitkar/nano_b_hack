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
  const [currentStep, setCurrentStep] = useState(0); // 0=scene, 1=image, 2+=dialogue
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

  // Helper function to calculate total steps for current panel
  const getMaxStepsForPanel = (panelIndex: number): number => {
    if (panelIndex >= panels.length) return 0;
    const panel = panels[panelIndex];
    // Scene (1) + Image (1) + Dialogues (n)
    return 2 + panel.dialogue.length;
  };

  // Helper function to get current step type
  const getCurrentStepType = (): 'scene' | 'image' | 'dialogue' => {
    if (currentStep === 0) return 'scene';
    if (currentStep === 1) return 'image';
    return 'dialogue';
  };

  // Helper function to get current dialogue index
  const getCurrentDialogueIndex = (): number => {
    return currentStep - 2; // Dialogues start at step 2
  };

  // Helper function to get appropriate button text
  const getNextButtonText = (): string => {
    const stepType = getCurrentStepType();
    const maxSteps = getMaxStepsForPanel(currentPanelIndex);
    const isLastStep = currentStep === maxSteps - 1;
    const isLastPanel = currentPanelIndex === panels.length - 1;
    
    if (isLastStep && isLastPanel) {
      return 'View Full Comic →';
    } else if (isLastStep) {
      return 'Next Panel →';
    } else if (stepType === 'scene') {
      return 'View Scene →';
    } else if (stepType === 'image') {
      const currentPanel = panels[currentPanelIndex];
      return currentPanel.dialogue.length > 0 ? 'Show Dialogue →' : 'Next Panel →';
    } else {
      return 'Next Line →';
    }
  };

  const handleNext = () => {
    console.log('Next clicked, panel:', currentPanelIndex, 'step:', currentStep);
    if (isTransitioning) return;
    
    const maxSteps = getMaxStepsForPanel(currentPanelIndex);
    
    if (currentStep < maxSteps - 1) {
      // Move to next step within current panel
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentStep(currentStep + 1);
        setIsTransitioning(false);
      }, 300);
    } else {
      // Move to next panel or end slideshow
      if (currentPanelIndex < panels.length - 1) {
        setIsTransitioning(true);
        setTimeout(() => {
          setCurrentPanelIndex(currentPanelIndex + 1);
          setCurrentStep(0); // Reset to scene description
          setIsTransitioning(false);
        }, 300);
      } else {
        // Last panel, last step - show final comic
        onViewFinalComic();
      }
    }
  };

  const handlePrevious = () => {
    console.log('Previous clicked, panel:', currentPanelIndex, 'step:', currentStep);
    if (isTransitioning) return;
    
    if (currentStep > 0) {
      // Move to previous step within current panel
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentStep(currentStep - 1);
        setIsTransitioning(false);
      }, 300);
    } else if (currentPanelIndex > 0) {
      // Move to previous panel's last step
      setIsTransitioning(true);
      setTimeout(() => {
        setCurrentPanelIndex(currentPanelIndex - 1);
        const prevPanelMaxSteps = getMaxStepsForPanel(currentPanelIndex - 1);
        setCurrentStep(prevPanelMaxSteps - 1);
        setIsTransitioning(false);
      }, 300);
    }
    // If we're at panel 0, step 0, do nothing (can't go back further)
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
  const stepType = getCurrentStepType();
  const maxSteps = getMaxStepsForPanel(currentPanelIndex);
  const canGoBack = currentPanelIndex > 0 || currentStep > 0;

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

        {/* Main content area */}
        <div className="panel-display-area">
          {showSlideshow && (
            <div className="step-container">
              
              {/* Scene Description Step */}
              {stepType === 'scene' && (
                <div className="scene-display">
                  <div className="scene-text">
                    <h2>Panel {currentPanel.panel_number} of {panels.length}</h2>
                    <p>{currentPanel.scene_description}</p>
                  </div>
                </div>
              )}
              
              {/* Panel Image with Optional Dialogue Overlay */}
              {(stepType === 'image' || stepType === 'dialogue') && (
                <div className="panel-display">
                  <div className="panel-image-container">
                    <img
                      src={`http://localhost:8001${currentPanel.image_url}`}
                      alt={`Panel ${currentPanel.panel_number}`}
                      className={`panel-image ${currentStep === 1 ? 'first-load' : ''}`}
                    />
                  </div>
                  
                  {/* Dialogue overlay - only show during dialogue steps */}
                  {stepType === 'dialogue' && (
                    <div className={`dialogue-overlay ${isTransitioning ? 'transitioning' : ''}`}>
                      <div className="dialogue-bubble">
                        "{currentPanel.dialogue[getCurrentDialogueIndex()]}"
                      </div>
                    </div>
                  )}
                </div>
              )}
              
            </div>
          )}
        </div>

        {/* Progress indicator */}
        {showSlideshow && (
          <div className="progress-indicator">
            <div className="step-counter">
              Step {currentStep + 1} of {maxSteps} | Panel {currentPanel.panel_number} of {panels.length}
            </div>
          </div>
        )}

        {/* Navigation controls */}
        {showSlideshow && (
          <div className="slideshow-navigation">
            <button 
              className="nav-btn nav-btn-prev"
              onClick={handlePrevious}
              disabled={!canGoBack || isTransitioning}
            >
              ← Previous
            </button>
            
            <button 
              className="nav-btn nav-btn-next"
              onClick={handleNext}
              disabled={isTransitioning}
            >
              {getNextButtonText()}
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