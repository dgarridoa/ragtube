import { cn } from '../../lib/utils.js'

export function createSeparator(props = {}) {
  const { className = '', orientation = 'horizontal', ...rest } = props

  const separator = document.createElement('div')
  separator.setAttribute('role', 'separator')
  separator.className = cn(
    'shrink-0 bg-border',
    orientation === 'horizontal' ? 'h-[1px] w-full' : 'h-full w-[1px]',
    className
  )

  Object.entries(rest).forEach(([key, value]) => {
    separator.setAttribute(key, value)
  })

  return separator
}
