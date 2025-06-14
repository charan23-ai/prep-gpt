
import React from 'react';
import { Bot, User } from "lucide-react";

interface MessageBubbleProps {
  message: string;
  isUser: boolean;
  timestamp?: string;
}

const MessageBubble = ({ message, isUser, timestamp }: MessageBubbleProps) => {
  return (
    <div className={`flex items-start space-x-3 mb-6 ${isUser ? 'justify-end' : 'justify-start'} ${isUser ? 'animate-slide-in-right' : 'animate-slide-in-left'}`}>
      {!isUser && (
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-blue-600 rounded-full blur-md opacity-30"></div>
          <div className="relative bg-gradient-to-r from-blue-500 to-blue-600 p-2 rounded-full">
            <Bot className="w-5 h-5 text-white" />
          </div>
        </div>
      )}
      
      <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${isUser ? 'order-first' : ''}`}>
        <div className={`rounded-2xl p-4 ${
          isUser 
            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white ml-auto' 
            : 'glass-card text-blue-900'
        } shadow-lg`}>
          <p className="text-sm leading-relaxed">{message}</p>
          {timestamp && (
            <p className={`text-xs mt-2 ${isUser ? 'text-blue-100' : 'text-blue-500'}`}>
              {timestamp}
            </p>
          )}
        </div>
      </div>
      
      {isUser && (
        <div className="bg-gradient-to-r from-gray-400 to-gray-500 p-2 rounded-full">
          <User className="w-5 h-5 text-white" />
        </div>
      )}
    </div>
  );
};

export default MessageBubble;
