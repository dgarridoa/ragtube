import './styles/main.css'
import { initTheme } from './utils/theme.js'
import { createChannelSelector } from './components/channel-selector.js'
import { createChatInterface } from './components/chat-interface.js'
import { APIClient } from './api/client.js'

// Initialize the application
async function init() {
  try {
    console.log('Initializing RAGTube frontend...')

    // Initialize theme
    initTheme()

    // Initialize API client
    const apiClient = new APIClient()

    // Test API connection
    await apiClient.checkReadiness()
    console.log('API connection successful')

    // Get DOM containers
    const channelSelectorContainer = document.getElementById('channel-selector')
    const chatMain = document.getElementById('chat-main')

    if (!channelSelectorContainer || !chatMain) {
      throw new Error('Required DOM elements not found')
    }

    // Initialize components
    const channelSelector = createChannelSelector(apiClient)
    const chatInterface = createChatInterface(apiClient)

    // Mount components
    channelSelectorContainer.appendChild(channelSelector.element)
    chatMain.appendChild(chatInterface.element)

    // Focus the chat input
    setTimeout(() => {
      chatInterface.focusInput()
    }, 100)

    console.log('RAGTube frontend initialized successfully')
  } catch (error) {
    console.error('Failed to initialize application:', error)
    showError(
      'Failed to connect to the API. Please check if the backend is running.'
    )
  }
}

function showError(message) {
  const app = document.getElementById('app')
  if (!app) return

  const errorDiv = document.createElement('div')
  errorDiv.className =
    'fixed inset-0 bg-background flex items-center justify-center z-50'
  errorDiv.innerHTML = `
    <div class="max-w-md mx-4 p-6 bg-card border border-destructive rounded-lg shadow-lg">
      <div class="flex items-center space-x-2 text-destructive mb-3">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
        </svg>
        <span class="font-semibold">Connection Error</span>
      </div>
      <p class="text-muted-foreground">${message}</p>
      <button onclick="location.reload()" class="mt-4 inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
        Retry Connection
      </button>
    </div>
  `
  app.appendChild(errorDiv)
}

// Start the application
init()
