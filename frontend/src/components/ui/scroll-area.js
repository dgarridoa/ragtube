import { cn } from '../../lib/utils.js'

export function createScrollArea(props = {}) {
  const { className = '', children, ...rest } = props

  const scrollArea = document.createElement('div')
  scrollArea.className = cn('relative overflow-hidden', className)

  const viewport = document.createElement('div')
  viewport.className =
    'h-full w-full rounded-[inherit] overflow-auto scroll-area-viewport'

  if (children) {
    if (typeof children === 'string') {
      viewport.innerHTML = children
    } else if (Array.isArray(children)) {
      children.forEach(child => {
        if (typeof child === 'string') {
          viewport.insertAdjacentHTML('beforeend', child)
        } else if (child instanceof HTMLElement) {
          viewport.appendChild(child)
        }
      })
    } else if (children instanceof HTMLElement) {
      viewport.appendChild(children)
    }
  }

  scrollArea.appendChild(viewport)

  Object.entries(rest).forEach(([key, value]) => {
    scrollArea.setAttribute(key, value)
  })

  return scrollArea
}
