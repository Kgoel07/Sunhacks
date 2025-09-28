import React, { useState, useRef, useEffect, Fragment } from "react";

// --- Typing Indicator Component ---
// This component shows the three pulsing dots
const TypingIndicator = ({ darkMode }) => (
    <div
        style={{
            background: darkMode ? "#222" : "#e8e8e8",
            padding: "10px 14px",
            borderRadius: 14,
            maxWidth: "78%",
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-start",
            boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
            color: darkMode ? "#fff" : "#000",
            fontSize: 14,
            fontWeight: 700,
        }}
    >
        <span className="dot" style={{ opacity: 0.5 }}>•</span>
        <span className="dot" style={{ opacity: 0.7 }}>•</span>
        <span className="dot" style={{ opacity: 0.9 }}>•</span>

        {/* Note: In a real project, you'd add CSS for the pulse animation */}
        {/* For now, it will appear as static dots, which still communicates "loading" */}
    </div>
);
// --- End Typing Indicator Component ---


export default function App() {
    const [question, setQuestion] = useState("");
    const [chatHistory, setChatHistory] = useState([]); // { user: bool, text: string, image?: base64 }
    const [darkMode, setDarkMode] = useState(true);
    const [uploadedImage, setUploadedImage] = useState(null); // base64 data URL
    const [isTyping, setIsTyping] = useState(false); // NEW STATE for loading indicator
    const fileInputRef = useRef(null);
    const chatEndRef = useRef(null);

    // Auto-scroll to newest message
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, [chatHistory, uploadedImage, isTyping]); // Added isTyping to trigger scroll

    const handleImageUpload = (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onloadend = () => {
            setUploadedImage(reader.result); // base64 data URL
        };
        reader.readAsDataURL(file);
        e.target.value = "";
    };

    const removeUploadedImage = () => setUploadedImage(null);

    const askAI = () => {
        const text = question.trim();
        if (!text && !uploadedImage) return;

        // 1. Prepare data and push user message
        setChatHistory((prev) => [
            ...prev,
            { user: true, text: text || "", image: uploadedImage || null },
        ]);

        // 2. Start the typing indicator
        setIsTyping(true);

        // 3. Data to send to the backend
        const payload = {
            question: text,
            image: uploadedImage, // base64 string
        };

        // 4. Clear UI input
        setQuestion("");
        setUploadedImage(null);

        // 5. *** ACTUAL API CALL TO FLASK BACKEND ***
        const backendUrl = 'http://localhost:5000/ask_ai';

        fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`Server returned status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                const reply = data.reply;
                setChatHistory((prev) => [...prev, { user: false, text: reply }]);
            })
            .catch((error) => {
                console.error('API Error:', error);
                setChatHistory((prev) => [
                    ...prev,
                    { user: false, text: `Connection Error: Failed to reach the AI server. Check your console. 🚨` }
                ]);
            })
            .finally(() => {
                // 6. Stop the typing indicator regardless of success or failure
                setIsTyping(false); 
            });
        // *** END API CALL ***
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            askAI();
        }
    };
    
    // --- Helper function to render text with newlines (FIX) ---
    const renderTextWithNewlines = (text) => {
        if (!text) return null;
        return text.split('\n').map((line, lineIndex) => (
            <Fragment key={lineIndex}>
                {/* Insert <br /> for every line after the first one (index > 0) */}
                {lineIndex > 0 && <br />}
                {line}
            </Fragment>
        ));
    };
    // -----------------------------------------------------------

    return (
        <div
            style={{
                height: "100vh",
                width: "100vw",
                display: "flex",
                flexDirection: "column",
                background: darkMode
                    ? "linear-gradient(160deg, #07121a, #0f2a33, #163d45)"
                    : "linear-gradient(160deg, #f6f8fa, #e9eef2, #e0e6ea)",
                color: darkMode ? "#fff" : "#000",
                fontFamily: "system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial",
                boxSizing: "border-box",
                padding: "0.5rem",
            }}
        >
            {/* Header */}
            <div
                style={{
                    padding: "0.6rem 1rem",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: "0.5rem",
                }}
            >
                <h1 style={{ margin: 0, fontSize: 20, fontWeight: 600 }}>AI Gym Assistant</h1>
                {/* Theme: label + slider (slider shows Light/Dark inside knob) */}
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                    <span style={{ fontSize: 12, opacity: 0.9 }}>Theme:</span>

                    <label
                        style={{
                            position: "relative",
                            display: "inline-block",
                            width: 100,
                            height: 36,
                            marginTop: 6,
                        }}
                        aria-label="Toggle theme"
                    >
                        <input
                            type="checkbox"
                            checked={darkMode}
                            onChange={() => setDarkMode((s) => !s)}
                            style={{ opacity: 0, width: 0, height: 0 }}
                        />
                        {/* track */}
                        <span
                            style={{
                                position: "absolute",
                                inset: 0,
                                borderRadius: 36,
                                backgroundColor: darkMode ? "rgba(255,255,255,0.08)" : "#e2e8f0",
                                boxShadow: darkMode ? "inset 0 1px 0 rgba(255,255,255,0.02)" : "0 1px 2px rgba(0,0,0,0.06)",
                                transition: "background-color 0.25s",
                            }}
                        />
                        {/* knob */}
                        <span
                            style={{
                                position: "absolute",
                                top: 4,
                                left: darkMode ? 60 : 6,
                                height: 28,
                                width: 28,
                                borderRadius: "50%",
                                background: darkMode ? "linear-gradient(180deg,#fff,#f0f0f0)" : "#fff",
                                color: "#000",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                fontSize: 10,
                                fontWeight: 700,
                                transition: "left 0.25s",
                                boxShadow: "0 2px 6px rgba(0,0,0,0.25)",
                            }}
                        >
                            {darkMode ? "Dark" : "Light"}
                        </span>
                    </label>
                </div>
            </div>

            {/* Chat area */}
            <div
                style={{
                    flex: 1,
                    margin: "0.5rem",
                    borderRadius: 16,
                    backgroundColor: darkMode ? "rgba(0,0,0,0.25)" : "#fff",
                    padding: "12px",
                    overflowY: "auto",
                    display: "flex",
                    flexDirection: "column",
                    gap: 8,
                    boxShadow: darkMode ? "0 8px 30px rgba(0,0,0,0.6)" : "0 6px 18px rgba(0,0,0,0.08)",
                }}
            >
                {chatHistory.map((msg, i) => (
                    <div
                        key={i}
                        style={{
                            display: "flex",
                            justifyContent: msg.user ? "flex-end" : "flex-start",
                            padding: "0 6px",
                        }}
                    >
                        <div
                            style={{
                                background: msg.user
                                    ? "linear-gradient(90deg,#00c6ff,#0072ff)" 
                                    : darkMode ? "#222" : "#e8e8e8", 
                                color: msg.user ? "#fff" : darkMode ? "#fff" : "#000",
                                padding: "10px 14px",
                                borderRadius: 14,
                                maxWidth: "78%",
                                wordBreak: "break-word",
                                boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
                                display: "flex",
                                flexDirection: "column",
                                gap: 6,
                            }}
                        >
                            {msg.image && (
                                <img
                                    src={msg.image}
                                    alt="upload"
                                    style={{
                                        width: 140,
                                        height: 140,
                                        objectFit: "cover",
                                        borderRadius: 8,
                                        border: "1px solid rgba(255,255,255,0.06)",
                                        alignSelf: "center",
                                    }}
                                />
                            )}

                            {msg.text && <div style={{ fontSize: 14 }}>{renderTextWithNewlines(msg.text)}</div>}
                        </div>
                    </div>
                ))}
                
                {/* --- TYPING INDICATOR RENDERING --- */}
                {isTyping && (
                    <div
                        style={{
                            display: "flex",
                            justifyContent: "flex-start",
                            padding: "0 6px",
                        }}
                    >
                        <TypingIndicator darkMode={darkMode} />
                    </div>
                )}
                {/* ---------------------------------- */}


                <div ref={chatEndRef} />
            </div>

            {/* Input area with preview */}
            <div
                style={{
                    padding: 12,
                    display: "flex",
                    flexDirection: "column",
                    gap: 8,
                    boxSizing: "border-box",
                    width: "100%",
                    maxWidth: 980,
                    margin: "0 auto", 
                }}
            >
                {/* --- IMAGE PREVIEW RESTORED HERE --- */}
                {uploadedImage && (
                    <div 
                        style={{ 
                            display: "flex", 
                            alignItems: "center", 
                            gap: 8,
                            width: "100%",
                            maxWidth: 720,
                            margin: "0 auto", 
                        }}
                    >
                        <div style={{ position: "relative" }}>
                            <img
                                src={uploadedImage}
                                alt="preview"
                                style={{ width: 72, height: 72, objectFit: "cover", borderRadius: 8, border: "1px solid rgba(255,255,255,0.06)" }}
                            />
                            <button
                                onClick={removeUploadedImage}
                                style={{
                                    position: "absolute",
                                    top: -8,
                                    right: -8,
                                    width: 22,
                                    height: 22,
                                    borderRadius: "50%",
                                    background: "#ff4d4f",
                                    color: "#fff",
                                    border: "none",
                                    boxShadow: "0 2px 6px rgba(0,0,0,0.4)",
                                    cursor: "pointer",
                                    fontSize: 12,
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                }}
                                title="Remove image"
                            >
                                ×
                            </button>
                        </div>
                        <div style={{ fontSize: 13, opacity: 0.9 }}>{/* optional filename area */}</div>
                    </div>
                )}
                {/* ------------------------------------ */}

                {/* Input group container */}
                <div style={{ display: "flex", justifyContent: "center", width: "100%" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, width: "100%", maxWidth: 720, margin: "0 auto", justifyContent: "center" }}>
                        <input
                            type="text"
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask a fitness question..."
                            style={{ flex: 1, padding: "12px 16px", borderRadius: 999, border: "none", outline: "none", background: darkMode ? "rgba(255,255,255,0.04)" : "#f3f4f6", color: darkMode ? "#fff" : "#000", fontSize: 15, boxShadow: "inset 0 1px 0 rgba(255,255,255,0.02)" }}
                        />
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            title="Upload image"
                            style={{ width: 44, height: 44, borderRadius: 12, border: "none", background: darkMode ? "rgba(255,255,255,0.06)" : "#fff", color: darkMode ? "#fff" : "#000", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, cursor: "pointer", boxShadow: "0 6px 18px rgba(0,0,0,0.25)" }}
                        >
                            +
                        </button>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleImageUpload}
                            style={{ display: "none" }}
                        />
                        <button
                            onClick={askAI}
                            style={{ padding: "12px 18px", borderRadius: 999, border: "none", background: "linear-gradient(90deg,#00c6ff,#0072ff)", color: "#fff", fontWeight: 700, cursor: "pointer", boxShadow: "0 8px 24px rgba(0,123,255,0.22)" }}
                        >
                            Ask
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}