import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [chatInput, setChatInput] = useState("");
  const [chatResponse, setChatResponse] = useState("");
  const [memoriesUsed, setMemoriesUsed] = useState([]);
  const [memoryInput, setMemoryInput] = useState("");
  const [allMemories, setAllMemories] = useState([]);

  const API_BASE = "http://127.0.0.1:8000/api";

  // Fetch all memories
  const fetchMemories = async () => {
    const res = await axios.get(`${API_BASE}/memories/all`);
    setAllMemories(res.data);
  };

  useEffect(() => {
    fetchMemories();
  }, []);

  // Store new memory
  const handleStoreMemory = async () => {
    if (!memoryInput) return;

    await axios.post(`${API_BASE}/memories`, {
      text: memoryInput
    });

    setMemoryInput("");
    fetchMemories();
  };

  // Send chat query
  const handleChat = async () => {
    if (!chatInput) return;

    const res = await axios.post(`${API_BASE}/chat`, {
      query: chatInput
    });

    setChatResponse(res.data.answer);
    setMemoriesUsed(res.data.memories_used);
  };

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>AI Memory Assistant</h1>

      <hr />

      <h2>Store New Memory</h2>
      <input
        type="text"
        value={memoryInput}
        onChange={(e) => setMemoryInput(e.target.value)}
        placeholder="Enter conversation text..."
        style={{ width: "400px", marginRight: "10px" }}
      />
      <button onClick={handleStoreMemory}>Store</button>

      <hr />

      <h2>Chat</h2>
      <input
        type="text"
        value={chatInput}
        onChange={(e) => setChatInput(e.target.value)}
        placeholder="Ask something..."
        style={{ width: "400px", marginRight: "10px" }}
      />
      <button onClick={handleChat}>Send</button>

      <div style={{ marginTop: "20px" }}>
        <h3>AI Response:</h3>
        <p>{chatResponse}</p>

        <h3>Memories Used:</h3>
        <ul>
          {memoriesUsed.map((m, index) => (
            <li key={index}>{m}</li>
          ))}
        </ul>
      </div>

      <hr />

      <h2>All Stored Memories</h2>
      <ul>
        {allMemories.map((memory) => (
          <li key={memory.id}>{memory.content}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
