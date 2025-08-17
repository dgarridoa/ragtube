import { createCard, createCardContent } from './ui/card.js'
import { createButton } from './ui/button.js'
import { createScrollArea } from './ui/scroll-area.js'
import { createAvatar, createAvatarFallback } from './ui/avatar.js'
import { formatTime, formatDate } from '../utils/helpers.js'

export function createChatInterface(apiClient) {
  const container = document.createElement('div')
  container.className = 'flex-1 flex flex-col'

  // Messages container with scroll area
  const messagesCard = createCard({ className: 'flex-1 m-4 mb-0' })
  const messagesScrollArea = createScrollArea({ className: 'h-full p-6' })
  const messagesContainer = document.createElement('div')
  messagesContainer.className = 'space-y-4'
  messagesContainer.id = 'messages-container'

  // Add welcome message
  const welcomeMessage = createMessage({
    role: 'assistant',
    content:
      "Hello! I'm here to help answer any questions you may have about the YouTubers listed. Feel free to ask me anything, and I will provide you with accurate and helpful answers using transcriptions from their videos.",
    timestamp: new Date(),
  })
  messagesContainer.appendChild(welcomeMessage)

  messagesScrollArea.appendChild(messagesContainer)
  messagesCard.appendChild(messagesScrollArea)

  // Input area
  const inputCard = createCard({ className: 'm-4 mt-0' })
  const inputContent = createCardContent({ className: 'p-4' })
  const inputForm = document.createElement('form')
  inputForm.className = 'flex space-x-3'
  inputForm.id = 'chat-form'

  const inputContainer = document.createElement('div')
  inputContainer.className = 'flex-1 relative'

  const messageInput = document.createElement('textarea')
  messageInput.placeholder = 'Ask anything about the YouTube videos...'
  messageInput.className =
    'flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 pr-12 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none'
  messageInput.id = 'message-input'
  messageInput.rows = 3
  messageInput.style.resize = 'none'

  const sendButton = createButton({
    type: 'submit',
    variant: 'default',
    size: 'icon',
    className: 'absolute right-2 bottom-2 h-8 w-8 rounded-full',
    children: createSendIcon(),
  })

  inputContainer.appendChild(messageInput)
  inputContainer.appendChild(sendButton)
  inputForm.appendChild(inputContainer)
  inputContent.appendChild(inputForm)
  inputCard.appendChild(inputContent)

  container.appendChild(messagesCard)
  container.appendChild(inputCard)

  // State management
  let currentChannelId = null
  let isLoading = false

  // Listen for channel changes
  document.addEventListener('channelChanged', event => {
    currentChannelId = event.detail.channelId
  })

  // Handle Enter key in textarea (Ctrl+Enter or Cmd+Enter to send)
  messageInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault()
      inputForm.dispatchEvent(new Event('submit'))
    }
  })

  // Handle form submission
  inputForm.addEventListener('submit', async e => {
    e.preventDefault()

    const message = messageInput.value.trim()
    if (!message || isLoading) return

    // Add user message
    const userMessage = createMessage({
      role: 'user',
      content: message,
      timestamp: new Date(),
    })
    messagesContainer.appendChild(userMessage)

    // Clear input
    messageInput.value = ''

    // Scroll to bottom
    scrollToBottom()

    // Add typing indicator
    const typingIndicator = createTypingIndicator()
    messagesContainer.appendChild(typingIndicator)
    scrollToBottom()

    try {
      isLoading = true
      updateLoadingState(true)

      let assistantMessage = null
      let contextDisplayed = false

      for await (const response of apiClient.streamRAGResponse(
        message,
        currentChannelId
      )) {
        if (response.context && !contextDisplayed) {
          // Remove typing indicator
          typingIndicator.remove()

          // Create assistant message with context
          assistantMessage = createMessage({
            role: 'assistant',
            content: '',
            timestamp: new Date(),
            context: response.context,
          })
          messagesContainer.appendChild(assistantMessage)
          contextDisplayed = true
          scrollToBottom()
        } else if (response.answer && assistantMessage) {
          // Stream the answer
          const contentElement =
            assistantMessage.querySelector('.message-content')
          contentElement.textContent += response.answer
          scrollToBottom()
        }
      }

      if (!assistantMessage) {
        // Remove typing indicator and show no results
        typingIndicator.remove()
        const noResultsMessage = createMessage({
          role: 'assistant',
          content: 'No relevant transcriptions were retrieved for your query.',
          timestamp: new Date(),
        })
        messagesContainer.appendChild(noResultsMessage)
        scrollToBottom()
      }
    } catch (error) {
      console.error('Chat error:', error)
      typingIndicator.remove()

      const errorMessage = createMessage({
        role: 'assistant',
        content:
          'I apologize, but I encountered an error while processing your request. Please try again.',
        timestamp: new Date(),
        isError: true,
      })
      messagesContainer.appendChild(errorMessage)
      scrollToBottom()
    } finally {
      isLoading = false
      updateLoadingState(false)
    }
  })

  function scrollToBottom() {
    const viewport = messagesScrollArea.querySelector('.scroll-area-viewport')
    if (viewport) {
      viewport.scrollTop = viewport.scrollHeight
    }
  }

  function updateLoadingState(loading) {
    sendButton.disabled = loading
    messageInput.disabled = loading

    if (loading) {
      sendButton.classList.add('opacity-50', 'cursor-not-allowed')
    } else {
      sendButton.classList.remove('opacity-50', 'cursor-not-allowed')
    }
  }

  return {
    element: container,
    focusInput: () => messageInput.focus(),
  }
}

function createMessage({
  role,
  content,
  timestamp,
  context = null,
  isError = false,
}) {
  const messageDiv = document.createElement('div')
  messageDiv.className =
    'flex space-x-3 animate-in slide-in-from-bottom-2 duration-300'

  // Avatar
  const avatar = createAvatar({ className: 'h-8 w-8' })
  const avatarFallback = createAvatarFallback({
    className:
      role === 'user'
        ? 'bg-primary text-primary-foreground'
        : 'bg-secondary text-secondary-foreground',
    children: role === 'user' ? 'U' : 'AI',
  })
  avatar.appendChild(avatarFallback)

  // Message content container
  const contentContainer = document.createElement('div')
  contentContainer.className = 'flex-1 space-y-2'

  // Message bubble
  const messageBubble = document.createElement('div')
  messageBubble.className = `rounded-lg p-4 max-w-3xl ${
    role === 'user'
      ? 'bg-primary text-primary-foreground ml-auto'
      : isError
        ? 'bg-destructive/10 border border-destructive text-destructive'
        : 'bg-muted'
  }`

  const messageContent = document.createElement('p')
  messageContent.className = 'message-content whitespace-pre-wrap'
  messageContent.textContent = content
  messageBubble.appendChild(messageContent)

  // Timestamp
  const timestampDiv = document.createElement('div')
  timestampDiv.className = 'text-xs text-muted-foreground'
  timestampDiv.textContent = formatTime(timestamp)

  contentContainer.appendChild(messageBubble)
  contentContainer.appendChild(timestampDiv)

  // Add context if provided
  if (context && context.length > 0) {
    const contextCard = createContextDisplay(context)
    contentContainer.appendChild(contextCard)
  }

  messageDiv.appendChild(avatar)
  messageDiv.appendChild(contentContainer)

  return messageDiv
}

function createTypingIndicator() {
  const messageDiv = document.createElement('div')
  messageDiv.className = 'flex space-x-3'

  const avatar = createAvatar({ className: 'h-8 w-8' })
  const avatarFallback = createAvatarFallback({
    className: 'bg-secondary text-secondary-foreground',
    children: 'AI',
  })
  avatar.appendChild(avatarFallback)

  const typingDiv = document.createElement('div')
  typingDiv.className = 'bg-muted rounded-lg p-4'
  typingDiv.innerHTML = `
    <div class="typing-indicator flex space-x-1">
      <span class="w-2 h-2 bg-muted-foreground rounded-full"></span>
      <span class="w-2 h-2 bg-muted-foreground rounded-full"></span>
      <span class="w-2 h-2 bg-muted-foreground rounded-full"></span>
    </div>
  `

  messageDiv.appendChild(avatar)
  messageDiv.appendChild(typingDiv)

  return messageDiv
}

function createContextDisplay(context) {
  const contextCard = createCard({ className: 'mt-3' })

  const header = document.createElement('div')
  header.className =
    'px-4 py-2 bg-muted/50 rounded-t-lg border-b cursor-pointer flex items-center justify-between'
  header.innerHTML = `
    <span class="text-sm font-medium">Retrieved Context (${context.length} sources)</span>
    <svg class="w-4 h-4 transition-transform context-chevron" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
    </svg>
  `

  const content = document.createElement('div')
  content.className = 'hidden context-content p-4 space-y-6'

  context.forEach((doc, index) => {
    const sourceDiv = document.createElement('div')
    sourceDiv.className = 'bg-card border rounded-lg overflow-hidden'

    // Main content container - side by side layout
    const mainContent = document.createElement('div')
    mainContent.className = 'flex gap-4 p-4'

    // Left side - Transcript content (flex-1 to take most space)
    const leftSide = document.createElement('div')
    leftSide.className = 'flex-1 space-y-3'

    // Title and publish time
    const titleContainer = document.createElement('div')
    titleContainer.className = 'flex items-start justify-between gap-2'

    const titleDiv = document.createElement('div')
    titleDiv.className = 'font-medium text-sm flex-1 flex items-center gap-2'
    titleDiv.innerHTML = `
      <svg class="w-4 h-4 text-red-500 shrink-0" fill="currentColor" viewBox="0 0 24 24">
        <path d="M21.593 7.203a2.506 2.506 0 0 0-1.762-1.766C18.265 5.007 12 5 12 5s-6.264-.007-7.831.404a2.56 2.56 0 0 0-1.766 1.778c-.413 1.566-.417 4.814-.417 4.814s-.004 3.264.406 4.814c.23.857.905 1.534 1.763 1.765 1.582.43 7.83.437 7.83.437s6.265.007 7.831-.403a2.515 2.515 0 0 0 1.767-1.763c.414-1.565.417-4.812.417-4.812s.02-3.265-.407-4.831zM9.996 15.005l.005-6 5.207 3.005-5.212 2.995z"/>
      </svg>
      <span>${doc.title}</span>
    `

    const publishTimeDiv = document.createElement('div')
    publishTimeDiv.className = 'text-xs text-muted-foreground shrink-0'
    publishTimeDiv.textContent = formatDate(doc.publish_time)

    titleContainer.appendChild(titleDiv)
    titleContainer.appendChild(publishTimeDiv)

    // Transcript content
    const transcriptLabel = document.createElement('div')
    transcriptLabel.className =
      'text-xs font-medium text-muted-foreground uppercase tracking-wide'
    transcriptLabel.textContent = 'Transcript'

    const contentDiv = document.createElement('div')
    contentDiv.className = 'text-sm text-muted-foreground'

    // Create expandable content
    const maxLength = 200
    const isLong = doc.content.length > maxLength

    if (isLong) {
      const truncatedText = doc.content.slice(0, maxLength)
      const remainingText = doc.content.slice(maxLength)

      const contentSpan = document.createElement('span')
      contentSpan.className = 'whitespace-pre-wrap'
      contentSpan.textContent = truncatedText

      const ellipsisSpan = document.createElement('span')
      ellipsisSpan.className =
        'text-primary cursor-pointer hover:underline font-medium ml-1'
      ellipsisSpan.textContent = '...'
      ellipsisSpan.title = 'Click to expand'

      const hiddenSpan = document.createElement('span')
      hiddenSpan.className = 'hidden whitespace-pre-wrap'
      hiddenSpan.textContent = remainingText

      const collapseSpan = document.createElement('span')
      collapseSpan.className =
        'hidden text-primary cursor-pointer hover:underline font-medium ml-1'
      collapseSpan.textContent = ' Show less'
      collapseSpan.title = 'Click to collapse'

      // Toggle functionality
      ellipsisSpan.addEventListener('click', e => {
        e.stopPropagation()
        ellipsisSpan.classList.add('hidden')
        hiddenSpan.classList.remove('hidden')
        collapseSpan.classList.remove('hidden')
      })

      collapseSpan.addEventListener('click', e => {
        e.stopPropagation()
        hiddenSpan.classList.add('hidden')
        collapseSpan.classList.add('hidden')
        ellipsisSpan.classList.remove('hidden')
      })

      contentDiv.appendChild(contentSpan)
      contentDiv.appendChild(ellipsisSpan)
      contentDiv.appendChild(hiddenSpan)
      contentDiv.appendChild(collapseSpan)
    } else {
      contentDiv.className = 'text-sm text-muted-foreground whitespace-pre-wrap'
      contentDiv.textContent = doc.content
    }

    leftSide.appendChild(titleContainer)
    leftSide.appendChild(transcriptLabel)
    leftSide.appendChild(contentDiv)

    // Right side - Video container (thumbnail or embedded video)
    const rightSide = document.createElement('div')
    rightSide.className = 'w-48 shrink-0'

    const videoContainer = document.createElement('div')
    videoContainer.className = 'relative w-full h-28 rounded-lg overflow-hidden'

    // YouTube thumbnail - clickable to show embedded video
    const thumbnail = document.createElement('div')
    thumbnail.className =
      'relative w-full h-full bg-black cursor-pointer border-2 border-border hover:border-primary transition-colors group'
    thumbnail.title = `Play "${doc.title}"`

    const thumbnailImg = document.createElement('img')
    thumbnailImg.src = `https://img.youtube.com/vi/${doc.video_id}/mqdefault.jpg`
    thumbnailImg.alt = doc.title
    thumbnailImg.className = 'w-full h-full object-cover'

    // Play overlay
    const playOverlay = document.createElement('div')
    playOverlay.className =
      'absolute inset-0 bg-black/30 flex items-center justify-center group-hover:bg-black/50 transition-colors'
    playOverlay.innerHTML = `
      <div class="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center group-hover:bg-red-500 transition-colors">
        <svg class="w-6 h-6 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
          <path d="M8 5v14l11-7z"/>
        </svg>
      </div>
    `

    thumbnail.appendChild(thumbnailImg)
    thumbnail.appendChild(playOverlay)

    // Embedded video container (hidden by default)
    const embedContainer = document.createElement('div')
    embedContainer.className = 'hidden w-full h-full relative'

    let isShowingVideo = false

    // Click to toggle between thumbnail and embedded video
    thumbnail.addEventListener('click', e => {
      e.stopPropagation()

      if (!isShowingVideo) {
        // Create and show embedded video in place
        const videoEmbed = createYouTubeEmbed(doc.video_id, doc.title)
        embedContainer.innerHTML = ''
        embedContainer.appendChild(videoEmbed)

        // Add back to thumbnail button
        const backButton = document.createElement('button')
        backButton.className =
          'absolute top-2 right-2 z-10 bg-black/70 text-white p-1 rounded hover:bg-black/90 transition-colors'
        backButton.innerHTML = `
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        `
        backButton.title = 'Back to thumbnail'
        backButton.addEventListener('click', e => {
          e.stopPropagation()
          embedContainer.classList.add('hidden')
          thumbnail.classList.remove('hidden')
          isShowingVideo = false
        })

        embedContainer.appendChild(backButton)
        embedContainer.classList.remove('hidden')
        thumbnail.classList.add('hidden')
        isShowingVideo = true
      }
    })

    videoContainer.appendChild(thumbnail)
    videoContainer.appendChild(embedContainer)
    rightSide.appendChild(videoContainer)

    // Assemble the layout
    mainContent.appendChild(leftSide)
    mainContent.appendChild(rightSide)
    sourceDiv.appendChild(mainContent)

    content.appendChild(sourceDiv)
  })

  // Toggle functionality
  header.addEventListener('click', () => {
    const isHidden = content.classList.contains('hidden')
    const chevron = header.querySelector('.context-chevron')

    if (isHidden) {
      content.classList.remove('hidden')
      chevron.style.transform = 'rotate(180deg)'
    } else {
      content.classList.add('hidden')
      chevron.style.transform = 'rotate(0deg)'
    }
  })

  contextCard.appendChild(header)
  contextCard.appendChild(content)

  return contextCard
}

function createSendIcon() {
  const icon = document.createElement('span')
  icon.innerHTML = '↑'
  icon.className = 'text-base font-bold'
  return icon
}

function createYouTubeEmbed(videoId, title) {
  const container = document.createElement('div')
  container.className = 'relative w-full h-full bg-black'

  const iframe = document.createElement('iframe')
  iframe.className = 'w-full h-full'
  iframe.src = `https://www.youtube.com/embed/${videoId}?rel=0&modestbranding=1&showinfo=0&autoplay=1`
  iframe.title = title || 'YouTube video player'
  iframe.frameBorder = '0'
  iframe.allow =
    'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share'
  iframe.allowFullscreen = true
  iframe.loading = 'lazy'

  // Add loading state
  const loadingDiv = document.createElement('div')
  loadingDiv.className =
    'absolute inset-0 flex items-center justify-center bg-black'
  loadingDiv.innerHTML = `
    <div class="flex items-center space-x-2 text-white">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
      <span class="text-sm">Loading video...</span>
    </div>
  `

  // Hide loading when iframe loads
  iframe.addEventListener('load', () => {
    loadingDiv.style.display = 'none'
  })

  container.appendChild(loadingDiv)
  container.appendChild(iframe)

  return container
}
