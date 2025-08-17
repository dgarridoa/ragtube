# RAGTube Frontend

A modern, interactive frontend for RAGTube built with **shadcn/ui**, **Vite**, and **Vanilla JavaScript**.

## ✨ Features

- 🎨 **Beautiful UI** - Built with shadcn/ui components and Tailwind CSS
- 🌙 **Dark/Light Mode** - Automatic theme switching with system preference detection
- 💬 **Real-time Chat** - Streaming responses from the RAG backend
- 📺 **YouTube Integration** - Direct links to video sources
- 📱 **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- ⚡ **Fast Development** - Hot reload with Vite
- 🔍 **Context Viewer** - Expandable panels showing retrieved document sources
- 🎯 **Channel Filtering** - Filter responses by specific YouTube channels

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ or compatible JavaScript runtime
- Your RAGTube backend running on `http://localhost:5000`

### Installation

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**

   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:8501`

### Production Build

```bash
npm run build
npm run preview
```

## 🛠️ Technology Stack

### Core Technologies

- **[Vite](https://vitejs.dev/)** - Ultra-fast build tool and dev server
- **Vanilla JavaScript** - No framework overhead, modern ES6+ features
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[shadcn/ui](https://ui.shadcn.com/)** - Beautiful, accessible component system

### Dependencies

- **Radix UI Primitives** - Accessible, unstyled UI components
- **Lucide Icons** - Beautiful, customizable SVG icons
- **clsx & tailwind-merge** - Conditional CSS class utilities
- **class-variance-authority** - Type-safe variant API

## 📁 Project Structure

```
frontend/
├── index.html              # Main HTML template
├── package.json            # Dependencies and scripts
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
└── src/
    ├── main.js            # Application entry point
    ├── lib/
    │   └── utils.js       # Utility functions (cn helper)
    ├── styles/
    │   └── main.css       # Global styles and CSS variables
    ├── utils/
    │   ├── theme.js       # Theme management
    │   └── helpers.js     # General utility functions
    ├── api/
    │   └── client.js      # API communication layer
    └── components/
        ├── ui/            # shadcn/ui base components
        │   ├── button.js
        │   ├── card.js
        │   ├── input.js
        │   ├── select.js
        │   ├── scroll-area.js
        │   ├── separator.js
        │   └── avatar.js
        ├── channel-selector.js  # Channel selection component
        └── chat-interface.js    # Main chat interface
```

## 🎨 Customization

### Theme Colors

The application uses CSS custom properties for theming. You can customize colors by modifying the CSS variables in `src/styles/main.css`:

```css
:root {
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  /* ... other variables */
}
```

### Component Styling

All components use the `cn()` utility for conditional classes. You can easily customize component styles by modifying the class strings in each component file.

### Adding New Components

To add new shadcn/ui components:

1. Create the component in `src/components/ui/`
2. Follow the shadcn/ui patterns for consistency
3. Import and use in your application components

## 🔧 Configuration

### API Endpoint

The frontend connects to the backend at `http://localhost:5000` by default. To change this, modify the `baseURL` in `src/api/client.js`:

```javascript
export class APIClient {
  constructor(baseURL = 'http://your-backend-url:port') {
    this.baseURL = baseURL
  }
}
```

### Development Server

Vite development server runs on port 8501 by default. You can change this in `vite.config.js`:

```javascript
export default defineConfig({
  server: {
    port: 3001, // Your preferred port
    host: true,
  },
})
```

## 📖 Component Usage

### Creating UI Components

```javascript
import { createButton } from './components/ui/button.js'
import { createCard, createCardContent } from './components/ui/card.js'

// Create a button
const button = createButton({
  variant: 'default',
  size: 'lg',
  children: 'Click me',
  onClick: () => console.log('Clicked!'),
})

// Create a card
const card = createCard({
  className: 'max-w-md',
  children: [createCardContent({ children: 'Card content here' })],
})
```

### API Integration

```javascript
import { APIClient } from './api/client.js'

const api = new APIClient()

// Get channels
const channels = await api.getChannels()

// Stream RAG responses
for await (const response of api.streamRAGResponse(query, channelId)) {
  if (response.context) {
    // Handle context
  } else if (response.answer) {
    // Handle streaming answer
  }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **"Cannot connect to API"**
   - Ensure your RAGTube backend is running on port 5000
   - Check if the backend URL is correct in `src/api/client.js`

2. **"Styles not loading"**
   - Make sure Tailwind CSS is properly installed
   - Check if `postcss.config.js` is correctly configured

3. **"Components not rendering"**
   - Verify all imports are correct
   - Check browser console for JavaScript errors

### Development Tips

- Use browser DevTools to inspect component structure
- Check the Network tab for API call issues
- Use React DevTools if you plan to migrate to React later

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the same license as the parent RAGTube project.
