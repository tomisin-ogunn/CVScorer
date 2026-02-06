import React from 'react';

const Navbar: React.FC = () => {
  return (
    <nav className="bg-gradient-to-r from-primary-600 to-primary-700 shadow-lg fixed top-0 left-0 right-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-white tracking-tight">
              CVChecker
            </h1>
          </div>
          <div className="hidden sm:block">
            <div className="flex items-center space-x-4">
              <span className="text-primary-100 text-sm">
                Compare CVs with Job Descriptions
              </span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
