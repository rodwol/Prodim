import React from "react";
import { Link, useNavigate } from 'react-router-dom';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();
  return (
    <div style={{ textAlign: "center", padding: "50px" }}>
      <div className="Home">
        <header className="Home-header">
          <h2>PRODIM</h2>
          <nav>
            <ul>
              <li><Link to="/home">Home</Link></li>
              <li><Link to="/services">Services</Link></li>
              <li><Link to="/dashboard">Dashboard</Link></li>
              <li><Link to="/contact">Contact</Link></li>
            </ul>
          </nav>
          <button onClick={() => navigate('/login')}>Login</button>
        </header>
        <main className="Home-main">
          <h1>Take Control of Your Brain Health</h1>
        </main>
      </div>
    </div>
  );
};

export default Home;