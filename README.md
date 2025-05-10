# PhizzyAI

PhizzyAI is an AI-powered physical therapy assistant that helps users identify and address muscle pain and discomfort through interactive chat and a visual body diagram interface.

## Features

- **Interactive Body Diagram**: Click on body parts to identify areas of pain or discomfort
- **Voice Input**: Speak your symptoms for hands-free interaction
- **AI-Powered Analysis**: Receive detailed analysis of your symptoms from an AI physical therapist
- **Personalized Stretches**: Get recommended stretches specific to your affected muscle groups
- **Muscle Control Protocol (MCP)**: Backend service that manages muscle status and delivers appropriate stretching resources

## Architecture

The application consists of several key components:

1. **Streamlit Frontend**: Provides the user interface with body diagram and chat functionality
2. **Chatbot Module**: Handles AI interactions and processes user messages
3. **Body Diagram**: Interactive visual representation of the human body
4. **MCP Server**: Manages muscle status and provides stretching resources

## MCP Server Functions

The MCP server provides the following capabilities:

- **fetch_parts**: Retrieves the status of all body muscles (green/orange/red)
- **update_status**: Updates the status of specified muscle groups
- **send_stretches**: Sends stretching resources for specific muscle groups to the chat

## Running the Application

1. Ensure all dependencies are installed:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. Run the Streamlit app:
   ```
   streamlit run main.py
   ```

## Usage

1. Click on parts of the body diagram to indicate problem areas
2. Type your symptoms in the text field or use the voice input button
3. Receive AI analysis of your symptoms
4. Get personalized stretching recommendations with links to visual demonstrations 