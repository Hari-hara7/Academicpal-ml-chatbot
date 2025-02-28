import React, { useState, useRef, useEffect } from "react";
import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";
import { Send, MessageCircle, User, Bot } from "lucide-react";
import logo from "../assets/logo_academic_pal-removebg-preview.png";

interface Message {
  text: string;
  isUser: boolean;
}

const NotesGPT: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { 
      text: "👋 Welcome to AcademicPal! I'm your AI-powered notes assistant. Ask me anything about your subjects!", 
      isUser: false 
    },
    {
      text: "Try searching for 'python', 'math', 'physics', or 'chemistry'.", 
      isUser: false 
    }
  ]);
  const [showWelcome, setShowWelcome] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    if (showWelcome) setShowWelcome(false);

    setMessages((prev) => [...prev, { text: message, isUser: true }]);

    const botResponse = await fetchBotResponse(message);
    handleResponse(botResponse);
  };

  const fetchBotResponse = async (message: string): Promise<string> => {
    const lowerCaseMessage = message.toLowerCase();
    if (lowerCaseMessage.includes("python")) {
      return "🔍 Found notes for Python: https://drive.google.com/drive/folders/your-link";
    } else if (lowerCaseMessage.includes("math")) {
      return "📚 Math notes include Algebra, Calculus, and Linear Algebra.";
    } else if (lowerCaseMessage.includes("physics")) {
      return "🛸 Check out Physics notes: https://drive.google.com/drive/folders/your-link\n🔍 Found notes for New Physics (Physics): https://drive.google.com/drive/folders/1e-LQMg0B7XF9wJDfWg4vWwc8SZg16LXt";
    } else if (lowerCaseMessage.includes("chemistry")) {
      return "⚗️ Chemistry notes cover Organic and Inorganic concepts.\n🔍 Found notes for Chemistry: https://drive.google.com/drive/folders/11s9sgR-Hpb40p2tVlsetlBWcE6UPIubO";
    } else if (lowerCaseMessage.includes("psp")) {
      return "🔍 Found notes for Problem Solving (Physics): https://drive.google.com/drive/u/5/folders/1yKkXdRkNXuui8Ysq7hCygAPak9OS49O_";
    } else {
      return "🤔 I couldn’t find anything. Try another subject or keyword!";
    }
  };

  const handleResponse = (response: string) => {
    setMessages((prev) => [...prev, { text: response, isUser: false }]);
  };

  const renderMessageWithLinks = (text: string) => {
    const linkRegex = /(https?:\/\/[^\s)]+)/g;

    return text.split(linkRegex).map((part, index) => {
      if (linkRegex.test(part)) {
        return (
          <a
            key={index}
            href={part}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 underline hover:text-blue-300"
          >
            {part}
          </a>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 flex items-center bg-gray-800 shadow-md">
        <img src={logo} alt="AcademicPal Logo" className="h-10 w-10 mr-3" />
        <h1 className="text-xl font-semibold">AcademicPal AI</h1>
      </div>

      {/* Welcome Screen */}
      {showWelcome ? (
        <div className="flex flex-col items-center justify-center flex-1 text-center">
          <img src={logo} alt="Chatbot Logo" className="w-20 h-20 mb-4" />
          <h2 className="text-2xl font-semibold">Hello! I'm your AI notes assistant</h2>
          <p className="text-gray-400 mt-2">
            Ask me anything about <b>B.Tech Subjects</b>! <br />
            <span className="text-sm text-gray-500">
              Explore Python, Math, Physics & more.
            </span>
          </p>
          <div className="flex mt-4 space-x-3">
            <MessageCircle className="h-6 w-6 text-blue-500" />
            <Send className="h-6 w-6 text-green-500" />
          </div>
        </div>
      ) : (
        // Chat Messages
        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900">
          {messages.map((msg, index) => (
            <div key={index} className={`flex items-start space-x-3 ${msg.isUser ? "justify-end" : ""}`}>
              {msg.isUser ? (
                <User className="h-6 w-6 text-green-500" />
              ) : (
                <Bot className="h-6 w-6 text-blue-500" />
              )}
              <div
                className={`p-3 rounded-lg max-w-xs ${
                  msg.isUser ? "bg-green-600" : "bg-gray-800"
                }`}
              >
                {renderMessageWithLinks(msg.text)}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      )}

      {/* Chat Input */}
      <ChatInput onSendMessage={handleSendMessage} onResponseReceived={handleResponse} />
    </div>
  );
};

export default NotesGPT;
