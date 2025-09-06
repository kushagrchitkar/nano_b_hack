import React, { useState } from 'react';
import './App.css';
import ComicGenerator from './components/ComicGenerator';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Comic Generator</h1>
        <p>Generate comics from historical events in different styles</p>
      </header>
      <main className="App-main">
        <ComicGenerator />
      </main>
    </div>
  );
}

export default App;
