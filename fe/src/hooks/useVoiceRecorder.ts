import { useState, useRef } from "react";

export const useVoiceRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });
      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (e) => {
        chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
    } catch (error) {
      console.error("Microphone access denied:", error);
    }
  };

  const stopRecording = (): Blob | null => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
      chunksRef.current = [];
      setIsRecording(false);
      return audioBlob;
    }
    return null;
  };

  return { isRecording, startRecording, stopRecording };
};