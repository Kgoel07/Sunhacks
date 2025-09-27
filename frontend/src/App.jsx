/*import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App*/

import { useState } from "react";
import axios from "axios";

function App() {
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  // Mock API call while backend isn't ready
  const askAI = async () => {
    if (!question) return;

    // Add user's message
    setChatHistory([...chatHistory, { user: true, text: question }]);

    try {
      // Replace the URL with your backend once it's ready
      // const res = await axios.post("http://localhost:5000/chat", { question });
      // const answer = res.data.answer;

      // Mock response for now
      const answer = "This is a placeholder response. Backend will reply here.";

      // Add AI response
      setChatHistory((prev) => [...prev, { user: false, text: answer }]);
    } catch (err) {
      console.error(err);
      setChatHistory((prev) => [...prev, { user: false, text: "Error: Could not get a response." }]);
    }

    setQuestion(""); // Clear input
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "600px", margin: "auto" }}>
      <h1>🏋️ AI Gym Agent</h1>
      <div style={{ marginBottom: "1rem", minHeight: "200px" }}>
        {chatHistory.map((msg, i) => (
          <p key={i} style={{ textAlign: msg.user ? "right" : "left" }}>
            <strong>{msg.user ? "You: " : "AI: "}</strong> {msg.text}
          </p>
        ))}
      </div>
      <input
        type="text"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a fitness question..."
        style={{ width: "80%", padding: "0.5rem" }}
      />
      <button onClick={askAI} style={{ padding: "0.5rem", marginLeft: "0.5rem" }}>Ask</button>
    </div>
  );
}

export default App;