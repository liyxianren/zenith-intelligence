import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-light border-t border-gray-200 py-6 px-8">
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="text-sm text-gray-600 font-medium">
          © 2026 AI Learning Assistant. All rights reserved.
        </div>
        <div className="flex space-x-6">
          <a href="#" className="text-sm text-gray-600 hover:text-primary transition-colors font-medium">
            Privacy Policy
          </a>
          <a href="#" className="text-sm text-gray-600 hover:text-primary transition-colors font-medium">
            Terms of Service
          </a>
          <a href="#" className="text-sm text-gray-600 hover:text-primary transition-colors font-medium">
            Contact
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;