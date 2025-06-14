
import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Paperclip } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
}

const ChatInput = ({ onSendMessage }: ChatInputProps) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  return (
    <div className="p-6 border-t border-blue-200/30">
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        <div className="flex-1 relative">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask PrepGPT anything about your studies..."
            className="w-full pl-4 pr-12 py-4 rounded-2xl border-2 border-blue-200/50 focus:border-blue-400 bg-white/80 backdrop-blur-sm text-blue-900 placeholder-blue-500/70 text-sm resize-none transition-all duration-300"
          />
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="absolute right-2 top-1/2 transform -translate-y-1/2 text-blue-500 hover:text-blue-600 hover:bg-blue-100/50"
          >
            <Paperclip className="w-4 h-4" />
          </Button>
        </div>
        
        <div className="flex space-x-2">
          <Button
            type="submit"
            disabled={!message.trim()}
            className="azure-button p-3 rounded-full disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4 text-white" />
          </Button>
        </div>
      </form>
      
      <div className="flex flex-wrap gap-2 mt-3">
        {['Help with Math', 'Study Schedule', 'Essay Review', 'Practice Quiz'].map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => setMessage(suggestion)}
            className="px-3 py-1 text-xs bg-blue-100/80 text-blue-700 rounded-full hover:bg-blue-200/80 transition-all duration-300 backdrop-blur-sm"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ChatInput;
