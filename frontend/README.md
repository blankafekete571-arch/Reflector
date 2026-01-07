# Reflektor React Frontend

Beautiful chat interface for the Reflektor self-reflection assistant.

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

Frontend runs at: **http://localhost:3000**

> **Note**: Make sure the backend is running at `http://localhost:8000`

## Features

✨ **Modern chat interface** with message bubbles  
📊 **Progress tracking** through 8 reflection steps  
💬 **Real-time messaging** with typing indicators  
� **View & download history** anytime  
📱 **Fully responsive** - works on all devices  

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   ├── services/           # API integration
│   ├── App.jsx             # Main app
│   └── *.css               # Styling
├── index.html
├── vite.config.js
└── package.json
```

## Build for Production

```bash
npm run build
```

Creates optimized files in `dist/` folder.

## Customization

### Change Colors
Edit `src/index.css`:
```css
:root {
  --primary-color: #6366f1;
  --secondary-color: #8b5cf6;
}
```

### API URL
Default: `http://localhost:8000`  
To change: Edit `src/services/api.js`

## Tech Stack

- React 18
- Vite
- Axios
- CSS3
