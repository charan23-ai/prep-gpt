
import React from 'react';
import { Button } from "@/components/ui/button";
import { Brain, Shield, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

const PrivacyHeader = () => {
  return (
    <header className="relative z-10 flex items-center justify-between p-6 glass-effect">
      <div className="flex items-center space-x-3">
        <Link to="/">
          <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white hover:bg-gray-800/50">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </Link>
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-gray-400 to-gray-600 rounded-full blur-lg opacity-50 pulse-glow"></div>
          <div className="relative bg-gradient-to-r from-gray-500 to-gray-600 p-3 rounded-full float-animation">
            <Brain className="w-8 h-8 text-white" />
          </div>
        </div>
        <div className="flex flex-col">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-300 to-white bg-clip-text text-transparent">
            PrivacyGPT
          </h1>
          <p className="text-sm text-gray-400 font-medium">Private AI Study Companion</p>
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="hidden md:flex items-center space-x-2 px-4 py-2 glass-effect rounded-full">
          <Shield className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-300 font-medium">Zero Data Storage</span>
        </div>
      </div>
    </header>
  );
};

export default PrivacyHeader;
