# MyRAG WebUI

React.js frontend for MyRAG document management and retrieval system.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Features

- **Document Management**: Upload, view, and manage documents
- **Retrieval**: Chat interface for querying your documents using RAG

## Configuration

The backend API is expected to be running on `http://localhost:8000`. The Vite proxy is configured to forward `/api` requests to the backend.

## Build

To build for production:
```bash
npm run build
```
