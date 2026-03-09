import { useState, useRef, useEffect } from "react";
import { useChat } from "@/hooks/useChat";

export function ChatRoom({
  roomId,
  userId,
  username,
}: {
  roomId: string;
  userId: string;
  username: string;
}) {
  const { messages, sendMessage, isConnected, users } = useChat(
    roomId,
    userId,
    username
  );
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (inputValue.trim()) {
      sendMessage(inputValue);
      setInputValue("");
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">{roomId}</h1>
        <p className="text-sm text-gray-400">
          {isConnected ? "🟢 Connected" : "🔴 Disconnected"} •{" "}
          {users.length} online
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`p-3 rounded-lg max-w-xs ${
              msg.userId === userId
                ? "ml-auto bg-blue-600"
                : "bg-gray-700"
            }`}
          >
            <p className="text-sm font-semibold">{msg.username}</p>
            <p className="text-sm break-words">{msg.text}</p>
            <p className="text-xs text-gray-300 mt-1">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </p>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-gray-800 p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type a message..."
            className="flex-1 bg-gray-700 text-white px-4 py-2 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            disabled={!isConnected}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-2 rounded-lg font-semibold"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}