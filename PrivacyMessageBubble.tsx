
import React from 'react';
import { Shield, User } from "lucide-react";

interface PrivacyMessageBubbleProps {
  message: string;
  isUser: boolean;
  timestamp?: string;
}

const PrivacyMessageBubble = ({ message, isUser, timestamp }: PrivacyMessageBubbleProps) => {
  return (
    <div className={`flex items-start space-x-3 mb-6 ${isUser ? 'justify-end' : 'justify-start'} ${isUser ? 'animate-slide-in-right' : 'animate-slide-in-left'}`}>
      {!isUser && (
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-gray-400 to-gray-600 rounded-full blur-md opacity-30"></div>
          <div className="relative bg-gradient-to-r from-gray-500 to-gray-600 p-2 rounded-full">
            <Shield className="w-5 h-5 text-white" />
          </div>
        </div>
      )}
      
      <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${isUser ? 'order-first' : ''}`}>
        <div className={`rounded-2xl p-4 ${
          isUser 
            ? 'bg-gradient-to-r from-gray-600 to-gray-700 text-white ml-auto' 
            : 'bg-gray-800/50 backdrop-blur-sm text-gray-100 border border-gray-700/30'
        } shadow-lg`}>
          <p className="text-sm leading-relaxed">{message}</p>
          {timestamp && (
            <p className={`text-xs mt-2 ${isUser ? 'text-gray-300' : 'text-gray-400'}`}>
              {timestamp}
            </p>
          )}
        </div>
      </div>
      
      {isUser && (
        <div className="bg-gradient-to-r from-gray-500 to-gray-600 p-2 rounded-full">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
};

export default PrivacyMessageBubble;
