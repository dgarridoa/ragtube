import { createSelect } from './ui/select.js'

export function createChannelSelector(apiClient) {
  // Compact header-style channel selector
  const selectElement = createSelect({
    placeholder: 'All Channels',
    className:
      'min-w-[100px] sm:min-w-[120px] max-w-[130px] sm:max-w-[150px] text-xs sm:text-sm border-0 bg-transparent hover:bg-accent focus:bg-accent',
    onValueChange: value => {
      // Emit custom event when channel changes
      const event = new CustomEvent('channelChanged', {
        detail: { channelId: value || null },
      })
      document.dispatchEvent(event)
    },
  })

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
    element: selectElement,
    loadChannels,
  }
}
