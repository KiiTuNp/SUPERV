import React, { createContext, useContext, useEffect, useState } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MeetingContext = createContext();

export const MeetingProvider = ({ children }) => {
  const [meeting, setMeeting] = useState(null);
  const [participant, setParticipant] = useState(null);
  const [ws, setWs] = useState(null);
  const [meetingClosed, setMeetingClosed] = useState(false);
  const [lastHeartbeat, setLastHeartbeat] = useState(Date.now());

  const connectWebSocket = (meetingId) => {
    const wsUrl = `${BACKEND_URL.replace("https://", "wss://").replace("http://", "ws://")}/ws/meetings/${meetingId}`;
    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log("WebSocket connected");
      setWs(websocket);
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("WebSocket message:", data);
    };

    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    websocket.onclose = () => {
      console.log("WebSocket disconnected");
      setWs(null);
    };
  };

  useEffect(() => {
    let heartbeatInterval;
    if (meeting) {
      heartbeatInterval = setInterval(async () => {
        try {
          await axios.post(`${API}/meetings/${meeting.id}/heartbeat`, {
            meeting_id: meeting.id,
            organizer_name: meeting.organizer_name,
          });
          setLastHeartbeat(Date.now());
        } catch (error) {
          console.error("Erreur lors de l'envoi du heartbeat:", error);
        }
      }, 60000);
    }
    return () => {
      if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
      }
    };
  }, [meeting]);

  return (
    <MeetingContext.Provider
      value={{
        meeting,
        setMeeting,
        participant,
        setParticipant,
        ws,
        connectWebSocket,
        meetingClosed,
        setMeetingClosed,
        lastHeartbeat,
      }}
    >
      {children}
    </MeetingContext.Provider>
  );
};

export const useMeeting = () => useContext(MeetingContext);

