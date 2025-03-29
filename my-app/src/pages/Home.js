import React from "react";
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { Link } from 'react-router-dom';
import Layout from './Layout.js';
import './Home.css';

const Home = () => {
  return (
      <div style={{ textAlign: "center", padding: "50px" }}>
      <div className="Home">
      <header className="Home-header">
        <h2>PRODIM</h2>
        <nav>
          <ul>
          <li><a href="/home"> Home </a></li>
            <li><a href="/services"> Services </a></li>
            <li><a href="/dashboard"> Dashboard </a></li>
            <li> <a href="/contact"> Contact </a></li>
          </ul>
        </nav>
      </header>
      <main className="Home-main">
        <h1> Take Control of Your Brain Health </h1>
      </main>
    </div>
    </div>
  );
};

export default Home;