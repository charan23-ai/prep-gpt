
import React from 'react';
import { Button } from "@/components/ui/button";
import { Brain, Sparkles, Shield } from "lucide-react";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="relative z-10 flex items-center justify-between p-6 glass-effect">
      <div className="flex items-center space-x-3">
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-blue-600 rounded-full blur-lg opacity-50 pulse-glow"></div>
          <div className="relative bg-gradient-to-r from-blue-500 to-blue-600 p-3 rounded-full float-animation">
            <Brain className="w-8 h-8 text-white" />
          </div>
        </div>
        <div className="flex flex-col">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
            PrepGPT
          </h1>
          <p className="text-sm text-blue-600/80 font-medium">Your AI Study Companion</p>
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="hidden md:flex items-center space-x-2 px-4 py-2 glass-effect rounded-full">
          <Sparkles className="w-4 h-4 text-blue-500" />
          <span className="text-sm text-blue-700 font-medium">Powered by AI</span>
        </div>
        
        <Link to="/privacy">
          <Button 
            className="bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-500 hover:to-gray-600 text-white font-semibold px-6 py-2 rounded-full hover:scale-105 transition-all duration-300"
          >
            <Shield className="w-4 h-4 mr-2" />
            PrivacyGPT
          </Button>
        </Link>
      </div>
    </header>
  );
};

export default Header;
