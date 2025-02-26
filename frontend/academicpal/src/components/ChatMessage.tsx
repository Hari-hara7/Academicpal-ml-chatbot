import { Bot, User } from "lucide-react";

const ChatMessage: React.FC<ChatMessageProps> = ({ role, content }) => {
  return (
    <div className={`flex ${role === "user" ? "justify-end" : "justify-start"}`}>
      {role === "bot" && <Bot className="h-6 w-6 text-green-400 mr-2" />}
      <div
        className={`p-3 rounded-xl max-w-lg shadow-md ${
          role === "user" ? "bg-blue-600 text-white" : "bg-gray-700 text-white"
        }`}
      >
        {content}
      </div>
      {role === "user" && <User className="h-6 w-6 text-blue-400 ml-2" />}
    </div>
  );
};

export default ChatMessage;
