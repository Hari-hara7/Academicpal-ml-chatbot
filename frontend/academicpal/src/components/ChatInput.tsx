import React, { useState } from "react";
import { Send } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage }) => {
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    onSendMessage(input);
    setInput("");
  };

  return (
    <div className="p-4 bg-gray-800 flex items-center">
      <input
        type="text"
        className="flex-1 p-2 rounded-lg bg-gray-700 text-white focus:outline-none"
        placeholder="Type your message..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
      />
      <button className="ml-2 p-2 bg-blue-600 rounded-lg" onClick={handleSend}>
        <Send className="w-5 h-5 text-white" />
      </button>
    </div>
  );
};

export default ChatInput;
