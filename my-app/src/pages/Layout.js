import React from 'react';
import Navbar from './Navbar';

function Layout({ children }) {
  return (
    <div>
      <Navbar /> {/* Include the Navbar */}
      <main>{children}</main> {/* Render the page content */}
    </div>
  );
}

export default Layout;