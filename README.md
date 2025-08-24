# research-agent
an ai research agentic system that uses ai agents to simplify the problem and provide solutions 

## Agentic Server Initialization
1- start your mysql server.
2- create a database.
3- create an .env file with the following environment variables:
```terminal
MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, BASE_URL, API_KEY
```
4- install the dependencies, running the following command:
```terminal
pip install -r requirements.txt
```
5- run the agents.py using this command:
```terminal
python ./agents.py
```
Enjoy!

## Agentic Chat Client
A full-stack Next.js web application that serves as a polished chat client for an external agentic server. This app features Google sign-in, a real-time streaming chat UI, local state persistence, and a developer panel for debugging.

### Features:
- Authentication: Secure Google sign-in using NextAuth.js.
- Real-time Chat: Connects to a WebSocket /ws endpoint to stream agent responses with a typing effect.
- Conversation Management: Displays a history of conversations and allows users to start a new chat.
- Local Persistence: Saves unsent drafts, scroll positions, and UI state using localStorage.
- UI/UX: Utilizes a modern, responsive layout with shadcn/ui components and Tailwind CSS.
- Developer Tools: A toggleable Developer Panel for viewing raw WebSocket events and debugging.
- Containerization: Ready for production deployment with Docker.

## Getting Started
#### Prerequisites
Node.js (v18+)
npm or yarn
Docker (optional, but recommended)

#### Environment Variables
Create a .env.local file in the root directory and populate it with the following variables. A .env.example file is provided for reference.

## NextAuth.js
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET= # Generate a secure secret with `openssl rand -base64 32`
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

## Agentic Server API
AGENT_SERVER_BASE_URL=http://localhost:8000

## Google OAuth Setup
Go to the Google Cloud Console.
Create a new project or select an existing one.
Navigate to APIs & Services > OAuth consent screen.
Configure the consent screen details.
Go to Credentials, click Create Credentials, and select OAuth client ID.
Choose Web application.
Add http://localhost:3000 to Authorized JavaScript origins.
Add http://localhost:3000/api/auth/callback/google to Authorized redirect URIs.
Copy the Client ID and Client Secret and paste them into your .env file.

## Local Development
Install dependencies:
npm install
Run the development server:
npm run dev
The app will be available at http://localhost:3000.

## Docker
Build and Run with Docker Compose
Build the Docker image:
docker-compose up --build
This will build the Next.js app and run it in a container. The app will be accessible on port 3000.
To stop the containers:
  - ```docker-compose down```

## Project Structure:
```
/src
  /app
    /api
      /auth
        /[...nextauth]/route.ts  # NextAuth API routes
    /components
      /ui                      # shadcn/ui components
    /lib
      apiClient.ts
      auth.ts
      queryClient.ts
    layout.tsx
    page.tsx
  /docker
    Dockerfile
    docker-compose.yml
.env.example
README.md
```

## Architecture:
The application is built on Next.js 14 using the App Router. Data fetching is managed with TanStack Query for caching and server-side state management.
- **Authentication:** next-auth handles the Google OAuth flow and session management via cookies.
- **Data Flow:** The client-side application fetches conversation history and details from the external agentic server using a fetch wrapper that injects the user ID.
- **Real-time Streaming:** A custom useWsStream hook will manage the WebSocket connection. It listens for agent events, parses the JSON payloads, and updates the UI state incrementally to create a smooth "typing" effect.
- **UI State:** The app uses React's built-in state management and custom hooks for local persistence.
