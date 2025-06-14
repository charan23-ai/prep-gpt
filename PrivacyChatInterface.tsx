
import React, { useState, useRef, useEffect } from 'react';
import PrivacyMessageBubble from './PrivacyMessageBubble';
import PrivacyChatInput from './PrivacyChatInput';
import { ScrollArea } from "@/components/ui/scroll-area";
import { BookOpen, Target, Lightbulb, Clock } from "lucide-react";

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
}

const PrivacyChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Welcome to PrivacyGPT! I'm your private AI study companion. All conversations are ephemeral and nothing is stored. How can I help you study today?",
      isUser: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const handleSendMessage = (messageText: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      isUser: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, newMessage]);
    
    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm here to help with your studies in complete privacy. Your question has been processed without any data storage or tracking. What would you like to learn about?",
        isUser: false,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex-1 flex flex-col max-h-screen">
      {/* Features Banner */}
      <div className="p-4 bg-gradient-to-r from-gray-800/80 to-gray-900/80 backdrop-blur-sm border-b border-gray-700/30">
        <div className="flex flex-wrap justify-center gap-6 text-sm">
          <div className="flex items-center space-x-2 text-gray-300">
            <BookOpen className="w-4 h-4" />
            <span>Private Study Help</span>
          </div>
          <div className="flex items-center space-x-2 text-gray-300">
            <Target className="w-4 h-4" />
            <span>Anonymous Test Prep</span>
          </div>
          <div className="flex items-center space-x-2 text-gray-300">
            <Lightbulb className="w-4 h-4" />
            <span>Secure Explanations</span>
          </div>
          <div className="flex items-center space-x-2 text-gray-300">
            <Clock className="w-4 h-4" />
            <span>Ephemeral Sessions</span>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <ScrollArea className="flex-1 p-6" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.map((message) => (
            <PrivacyMessageBubble
              key={message.id}
              message={message.text}
              isUser={message.isUser}
              timestamp={message.timestamp}
            />
          ))}
        </div>
      </ScrollArea>

      {/* Chat Input */}
      <PrivacyChatInput onSendMessage={handleSendMessage} />
    </div>
  );
};

export default PrivacyChatInterface;
