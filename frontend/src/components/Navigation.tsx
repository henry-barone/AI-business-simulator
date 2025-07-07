
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const Navigation = () => {
  const location = useLocation();
  
  const navItems = [
    { name: 'Overview', path: '/' },
    { name: 'About Us', path: '/about' },
    { name: 'The Sandbox', path: '/sandbox' },
    { name: 'Business Simulation', path: '/simulation' },
    { name: 'Case Studies', path: '/case-studies' },
  ];

  return (
    <header className="w-full bg-white shadow-sm border-b border-gray-100">
      <div className="container mx-auto px-6 py-5">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold text-gray-900 tracking-tight">
            SPAIK
          </Link>
          
          <nav className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.name}
                to={item.path}
                className={`text-sm font-medium transition-colors hover:text-purple-600 ${
                  location.pathname === item.path
                    ? 'text-purple-600'
                    : 'text-gray-700'
                }`}
              >
                {item.name}
              </Link>
            ))}
          </nav>
          
          <div className="flex items-center gap-3">
            <Button variant="ghost" className="text-gray-700 hover:text-gray-900 font-medium">
              Login
            </Button>
            <Button className="professional-button text-sm font-semibold">
              Sign Up
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navigation;
