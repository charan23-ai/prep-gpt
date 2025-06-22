
import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import { ScrollArea } from "@/components/ui/scroll-area";
import { BookOpen, Target, Lightbulb, Clock, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useQuestionStorage } from '../hooks/useQuestionStorage';
import { useToast } from "@/hooks/use-toast";

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm PrepGPT, your AI study companion. I'm here to help you with studying, homework, test preparation, and academic success. Your questions can be saved for future reference. How can I assist you today?",
      isUser: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { saveQuestion } = useQuestionStorage();
  const { toast } = useToast();

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
        text: "Thank you for your question! I'm processing your request and will provide you with a comprehensive answer.",
        isUser: false,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  const handleSaveQuestion = (questionId: string) => {
    const messageIndex = messages.findIndex(m => m.id === questionId);
    if (messageIndex !== -1 && messages[messageIndex].isUser) {
      const question = messages[messageIndex].text;
      const answerIndex = messageIndex + 1;
      const answer = answerIndex < messages.length ? messages[answerIndex].text : '';
      
      saveQuestion(question, answer);
      toast({
        title: "Question Saved",
        description: "Your question and answer have been saved for future reference.",
      });
    }
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex-1 flex flex-col max-h-screen">
      {/* Features Banner */}
      <div className="p-4 bg-gradient-to-r from-blue-50/80 to-blue-100/80 backdrop-blur-sm border-b border-blue-200/30">
        <div className="flex flex-wrap justify-center gap-6 text-sm">
          <div className="flex items-center space-x-2 text-blue-700">
            <BookOpen className="w-4 h-4" />
            <span>Study Help</span>
          </div>
          <div className="flex items-center space-x-2 text-blue-700">
            <Target className="w-4 h-4" />
            <span>Test Prep</span>
          </div>
          <div className="flex items-center space-x-2 text-blue-700">
            <Lightbulb className="w-4 h-4" />
            <span>Concept Explanation</span>
          </div>
          <div className="flex items-center space-x-2 text-blue-700">
            <Clock className="w-4 h-4" />
            <span>Study Planning</span>
          </div>
          <div className="flex items-center space-x-2 text-blue-700">
            <Save className="w-4 h-4" />
            <span>Question Storage</span>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <ScrollArea className="flex-1 p-6" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.map((message, index) => (
            <div key={message.id} className="relative group">
              <MessageBubble
                message={message.text}
                isUser={message.isUser}
                timestamp={message.timestamp}
              />
              {message.isUser && (
                <Button
                  onClick={() => handleSaveQuestion(message.id)}
                  size="sm"
                  variant="outline"
                  className="absolute -right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-blue-50 hover:bg-blue-100 border-blue-200 text-blue-600"
                >
                  <Save className="w-3 h-3" />
                </Button>
              )}
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Chat Input */}
      <ChatInput onSendMessage={handleSendMessage} />
    </div>
  );
};

export default ChatInterface;
