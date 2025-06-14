
import React from 'react';
import Header from '../components/Header';
import ChatInterface from '../components/ChatInterface';

const Index = () => {
  return (
    <div className="min-h-screen azure-gradient">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-32 h-32 bg-blue-300/20 rounded-full blur-3xl float-animation"></div>
        <div className="absolute top-40 right-20 w-24 h-24 bg-blue-400/30 rounded-full blur-2xl" style={{ animationDelay: '1s' }}></div>
        <div className="absolute bottom-20 left-1/4 w-40 h-40 bg-blue-200/20 rounded-full blur-3xl" style={{ animationDelay: '2s' }}></div>
        <div className="absolute bottom-40 right-10 w-28 h-28 bg-blue-500/20 rounded-full blur-2xl float-animation" style={{ animationDelay: '1.5s' }}></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex flex-col min-h-screen max-w-6xl mx-auto">
        <Header />
        
        <main className="flex-1 flex flex-col bg-white/20 backdrop-blur-sm rounded-t-3xl mt-4 mx-4 mb-4 shadow-2xl border border-white/30">
          <ChatInterface />
        </main>
      </div>

      {/* Bottom Gradient Overlay */}
      <div className="fixed bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-blue-100/50 to-transparent pointer-events-none"></div>
    </div>
  );
};

export default Index;
