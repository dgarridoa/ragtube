import { createSelect } from './ui/select.js'
import {
  createCard,
  createCardHeader,
  createCardTitle,
  createCardContent,
} from './ui/card.js'

export function createChannelSelector(apiClient) {
  const container = createCard({ className: 'w-80' })

  const header = createCardHeader()
  const title = createCardTitle({ children: 'Select Channel' })
  header.appendChild(title)

  const content = createCardContent()

  const selectElement = createSelect({
    placeholder: 'All Channels',
    className: 'w-full',
    onValueChange: value => {
      // Emit custom event when channel changes
      const event = new CustomEvent('channelChanged', {
        detail: { channelId: value || null },
      })
      document.dispatchEvent(event)
    },
  })

  content.appendChild(selectElement)
  container.appendChild(header)
  container.appendChild(content)

  // Load channels function
  async function loadChannels() {
    try {
      const channels = await apiClient.getChannels()

      // Clear existing options except placeholder
      while (selectElement.children.length > 1) {
        selectElement.removeChild(selectElement.lastChild)
      }

      // Add channel options
      channels.forEach(channel => {
        const option = document.createElement('option')
        option.value = channel.id
        option.textContent = channel.title
        selectElement.appendChild(option)
      })

      console.log(`Loaded ${channels.length} channels`)
    } catch (error) {
      console.error('Failed to load channels:', error)

      // Show error state
      const errorOption = document.createElement('option')
      errorOption.value = ''
      errorOption.textContent = 'Failed to load channels'
      errorOption.disabled = true
      selectElement.appendChild(errorOption)
    }
  }

  // Initialize channels
  loadChannels()

  return {
    element: container,
    loadChannels,
  }
}
