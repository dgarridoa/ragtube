import { cn } from '../../lib/utils.js'

export function createInput(props = {}) {
  const { className = '', type = 'text', ...rest } = props

  const input = document.createElement('input')
  input.type = type
  input.className = cn(
    'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
    className
  )

  Object.entries(rest).forEach(([key, value]) => {
    if (key.startsWith('on')) {
      const eventName = key.slice(2).toLowerCase()
      input.addEventListener(eventName, value)
    } else {
      input.setAttribute(key, value)
    }
  })

  return input
}
