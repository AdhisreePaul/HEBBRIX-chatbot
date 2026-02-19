import React, { useState, useEffect } from "react";
import axios from "axios";
import "../src/App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [memories, setMemories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const API_BASE = "http://127.0.0.1:8000/api";

  const storeMemory = async () => {
    if (!input.trim()) return;
  
    await axios.post(`${API_BASE}/memories`, {
      text: input,
    });
  
    fetchMemories();
    setInput("");
  };
  
  const fetchMemories = async () => {
    const res = await axios.get(`${API_BASE}/memories/all`);
    setMemories(res.data);
  };

  useEffect(() => {
    fetchMemories();
  }, []);

  useEffect(() => {
    const chatBody = document.querySelector(".chat-body");
    if (chatBody) {
      chatBody.scrollTop = chatBody.scrollHeight;
    }
  }, [messages, loading]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const timestamp = new Date().toLocaleTimeString();

    const userMessage = {
      sender: "user",
      text: input,
      time: timestamp,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    const history = [...messages, userMessage].map((msg) => ({
      role: msg.sender === "user" ? "user" : "assistant",
      content: msg.text,
    }));

    const res = await axios.post(`${API_BASE}/chat`, {
      query: input,
      history: history,
    });

    const aiMessage = {
      sender: "ai",
      text: res.data.answer,
      memories_used: res.data.memories_used,
      time: new Date().toLocaleTimeString(),
    };

    setLoading(false);
    setMessages((prev) => [...prev, aiMessage]);
    setInput("");
  };

  return (
    <div className={darkMode ? "page dark" : "page"}>
      <div className="chat-wrapper">

        <div className="chat-container">
          <div className="chat-header">
            <span>AI Memory Assistant</span>
            <button
              className="theme-toggle"
              onClick={() => setDarkMode(!darkMode)}
            >
              {darkMode ? "☀️" : "🌙"}
            </button>
          </div>

          <div className="chat-body">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`message-wrapper ${
                  msg.sender === "user" ? "user-align" : "ai-align"
                }`}
              >
                <div className="avatar">
                  {msg.sender === "user" ? "👤" : "🤖"}
                </div>

                <div
                  className={`message ${
                    msg.sender === "user" ? "user-message" : "ai-message"
                  }`}
                >
                  <div className="message-text">{msg.text}</div>
                  <div className="timestamp">{msg.time}</div>

                  {msg.memories_used && (
                    <div className="memory-info">
                      <strong>Memories Used:</strong>
                      <ul>
                        {msg.memories_used.map((m, i) => (
                          <li key={i}>{m.content || m}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="message-wrapper ai-align">
                <div className="avatar">🤖</div>
                <div className="message ai-message typing">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
          </div>

          <div className="chat-input">
            <input
              type="text"
              placeholder="Ask something..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
            />
            <button className="send-btn" onClick={sendMessage}>
              Send
            </button>
            <button className="store-btn" onClick={storeMemory} title="Store as memory">
              💾
            </button>
          </div>

        </div>

        <div className="memory-panel">
          <h3>Stored Memories</h3>
          <ul>
            {memories.map((memory) => (
              <li key={memory.id}>{memory.content}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;
