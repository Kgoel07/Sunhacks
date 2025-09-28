import os
import io
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import base64
from PIL import Image 

# --- New Gemini SDK Imports ---
from google import genai
from google.genai.errors import APIError

# --- CONFIGURATION & INITIALIZATION ---

# Load environment variables from the .env file
load_dotenv() 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

app = Flask(__name__)
# Enable CORS for communication between frontend (e.g., port 3000) and backend (port 5000)
CORS(app) 

# Initialize the Gemini Client outside of the request function
client = None
try:
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    client = None


# --- AI LOGIC (Integrated Gemini API) ---

def process_ai_request(text, image_data):
    """
    Handles the core logic for the AI assistant by calling the Gemini API.
    """
    if not client:
         return "Error: Gemini client not initialized. GEMINI_API_KEY is missing or invalid."

    # --- System Prompt with Formatting and Conversational Rules ---
    final_prompt = (
    "You are an AI Gym Assistant named 'GymAI'. Your goal is to provide concise, actionable, "
    "and motivational fitness advice. You should **only** respond to questions related to fitness, "
    "exercise, workouts, nutrition, and healthy lifestyle habits. If the user asks something "
    "unrelated, politely respond that it is outside your intended purpose and you cannot provide an answer.\n\n"

    "Do not use Markdown formatting (like **bold** or _italics_) in your responses. "
    "All text should be plain and clean for frontend display.\n\n"

    "When providing a numbered or bulleted list, always put each item on a separate line with a newline "
    "before the first item if following a paragraph, and a newline after each item. "
    "Do not place multiple numbers or bullets on a single line. Example format:\n\n"
    "1. First point.\n"
    "2. Second point.\n\n"

    "Keep your advice clear, concise, actionable, and motivational, while strictly staying within fitness-related topics."
)

    # -----------------------------------------------------------------

    # Prepare the content list
    content_parts = [final_prompt]
    
    # Add the user's question to the prompt
    if text:
        content_parts.append(f"\n\nUser Question: {text}")
    
    # Process Image Data if present
    if image_data:
        try:
            # Strip the base64 prefix (e.g., "data:image/png;base64,") and decode
            header, encoded = image_data.split(",", 1)
            image_bytes = base64.b64decode(encoded)
            image = Image.open(io.BytesIO(image_bytes))
            
            content_parts.append(image)
        except Exception as e:
            print(f"Error processing image: {e}")
            return "Error: Could not decode the uploaded image data."

    # Call the Gemini API
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Excellent multimodal model
            contents=content_parts,
        )
        # Return the clean response text from the model
        return response.text
        
    except APIError as e:
        print(f"Gemini API Error: {e}")
        return f"Gemini API Error: Could not get a response. Details: {e}"
    except Exception as e:
        print(f"General API Error: {e}")
        return "An unexpected error occurred while communicating with the AI model."


# --- API ENDPOINT ---

@app.route('/ask_ai', methods=['POST'])
def ask_ai_endpoint():
    """
    The main API route that receives data from the frontend.
    """
    try:
        # 1. Get the JSON payload sent from the React application
        data = request.get_json()
        
        # 2. Extract the data safely
        question = data.get('question', '').strip()
        uploaded_image = data.get('image', None) # Base64 string
        
        # 3. Process the data using your AI logic
        reply = process_ai_request(question, uploaded_image)
        
        # 4. Return the AI reply as a JSON object
        return jsonify({'reply': reply}), 200

    except Exception as e:
        # Log the error for debugging
        print(f"An error occurred during API processing: {e}")
        # Return a standard error response to the frontend
        return jsonify({'reply': 'An internal server error occurred. Please check the backend console.'}), 500

# --- RUN THE SERVER ---

if __name__ == '__main__':
    status = "Loaded" if client else "Missing/Invalid"
    print(f"Flask API running. Gemini Client Status: {status}")
    app.run(debug=True, port=5000, host = "0.0.0.0")