import { cn } from '../../lib/utils.js'

export function createSelect(props = {}) {
  const {
    className = '',
    options = [],
    placeholder = 'Select...',
    onValueChange,
    ...rest
  } = props

  const select = document.createElement('select')
  select.className = cn(
    'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
    className
  )

  // Add placeholder option
  if (placeholder) {
    const placeholderOption = document.createElement('option')
    placeholderOption.value = ''
    placeholderOption.textContent = placeholder
    placeholderOption.disabled = true
    placeholderOption.selected = true
    select.appendChild(placeholderOption)
  }

  // Add options
  options.forEach(option => {
    const optionElement = document.createElement('option')
    optionElement.value = option.value
    optionElement.textContent = option.label
    select.appendChild(optionElement)
  })

  // Handle value changes
  if (onValueChange) {
    select.addEventListener('change', e => {
      onValueChange(e.target.value)
    })
  }

  Object.entries(rest).forEach(([key, value]) => {
    if (key.startsWith('on') && key !== 'onValueChange') {
      const eventName = key.slice(2).toLowerCase()
      select.addEventListener(eventName, value)
    } else if (!key.startsWith('on')) {
      select.setAttribute(key, value)
    }
  })

  return select
}
