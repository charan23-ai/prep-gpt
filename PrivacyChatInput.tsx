
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send } from "lucide-react";

interface PrivacyChatInputProps {
  onSendMessage: (message: string) => void;
}

const PrivacyChatInput = ({ onSendMessage }: PrivacyChatInputProps) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  return (
    <div className="p-6 border-t border-gray-700/30">
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        <div className="flex-1 relative">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask privately about your studies..."
            className="w-full pl-4 pr-4 py-4 rounded-2xl border-2 border-gray-700/50 focus:border-gray-500 bg-gray-800/50 backdrop-blur-sm text-gray-100 placeholder-gray-400 text-sm resize-none transition-all duration-300"
          />
        </div>
        
        <div className="flex space-x-2">
          <Button
            type="submit"
            disabled={!message.trim()}
            className="bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-500 hover:to-gray-600 p-3 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300"
          >
            <Send className="w-4 h-4 text-white" />
          </Button>
        </div>
      </form>
      
      <div className="flex flex-wrap gap-2 mt-3">
        {['Private Math Help', 'Anonymous Study Plan', 'Secure Essay Review', 'Confidential Quiz'].map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => setMessage(suggestion)}
            className="px-3 py-1 text-xs bg-gray-800/80 text-gray-300 rounded-full hover:bg-gray-700/80 transition-all duration-300 backdrop-blur-sm border border-gray-700/30"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
};

export default PrivacyChatInput;
