import React, { useState, useEffect } from 'react';
import './App.css';
import ComicGenerator from './components/ComicGenerator';
import homepageImage from './homepage.jpeg';

function App() {
  const [showHomepage, setShowHomepage] = useState(true);
  const [showGenerator, setShowGenerator] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowGenerator(true);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const handleEnterApp = () => {
    setShowHomepage(false);
  };

  if (showHomepage) {
    return (
      <div className="homepage-container">
        <div className="homepage-image">
          <img src={homepageImage} alt="Comic Generator Homepage" />
        </div>
        <div className={`homepage-overlay ${showGenerator ? 'fade-in' : ''}`}>
          <h1 className="homepage-title">COMIC GENERATOR</h1>
          <p className="homepage-subtitle">Transform any event into an epic comic adventure!</p>
          {showGenerator && (
            <button className="enter-button fade-in-delayed" onClick={handleEnterApp}>
              CREATE YOUR COMIC
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="App" style={{ '--bg-image': `url(${homepageImage})` } as any}>
      <header className="App-header">
        <h1>Comic Generator</h1>
        <p>Generate comics in different styles</p>
      </header>
      <main className="App-main">
        <ComicGenerator />
      </main>
    </div>
  );
}

export default App;
