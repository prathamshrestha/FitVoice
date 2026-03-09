import { useEffect, useState, useCallback } from "react";
import { getSocket } from "@/lib/socket";

export interface Message {
  id: string;
  userId: string;
  username: string;
  text: string;
  timestamp: number;
  type: "text" | "voice"; // for voice messages
}

export const useChat = (roomId: string, userId: string, username: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [users, setUsers] = useState<string[]>([]);

  useEffect(() => {
    const socket = getSocket();

    // Join room
    socket.emit("join_room", { roomId, userId, username });

    // Listen for messages
    socket.on("receive_message", (message: Message) => {
      setMessages((prev) => [...prev, message]);
    });

    // Listen for user list
    socket.on("user_list", (userList: string[]) => {
      setUsers(userList);
    });

    // Connection status
    socket.on("connect", () => setIsConnected(true));
    socket.on("disconnect", () => setIsConnected(false));

    return () => {
      socket.off("receive_message");
      socket.off("user_list");
    };
  }, [roomId, userId, username]);

  const sendMessage = useCallback(
    (text: string) => {
      const socket = getSocket();
      const message: Message = {
        id: `${Date.now()}`,
        userId,
        username,
        text,
        timestamp: Date.now(),
        type: "text",
      };
      socket.emit("send_message", { roomId, message });
    },
    [roomId, userId, username]
  );

  const sendVoiceMessage = useCallback(
    (audioBlob: Blob) => {
      const socket = getSocket();
      const reader = new FileReader();
      reader.onload = () => {
        socket.emit("send_voice", {
          roomId,
          userId,
          username,
          audio: reader.result, // base64 encoded audio
        });
      };
      reader.readAsDataURL(audioBlob);
    },
    [roomId, userId, username]
  );

  return { messages, sendMessage, sendVoiceMessage, isConnected, users };
};