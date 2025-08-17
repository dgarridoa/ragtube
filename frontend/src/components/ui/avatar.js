import { cn } from '../../lib/utils.js'

export function createAvatar(props = {}) {
  const { className = '', children, ...rest } = props

  const avatar = document.createElement('span')
  avatar.className = cn(
    'relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full',
    className
  )

  if (children) {
    if (typeof children === 'string') {
      avatar.innerHTML = children
    } else if (children instanceof HTMLElement) {
      avatar.appendChild(children)
    }
  }

  Object.entries(rest).forEach(([key, value]) => {
    avatar.setAttribute(key, value)
  })

  return avatar
}

export function createAvatarImage(props = {}) {
  const { className = '', src, alt, ...rest } = props

  const img = document.createElement('img')
  img.className = cn('aspect-square h-full w-full', className)

  if (src) img.src = src
  if (alt) img.alt = alt

  Object.entries(rest).forEach(([key, value]) => {
    img.setAttribute(key, value)
  })

  return img
}

export function createAvatarFallback(props = {}) {
  const { className = '', children, ...rest } = props

  const fallback = document.createElement('div')
  fallback.className = cn(
    'flex h-full w-full items-center justify-center rounded-full bg-muted',
    className
  )

  if (typeof children === 'string') {
    fallback.textContent = children
  } else if (children instanceof HTMLElement) {
    fallback.appendChild(children)
  }

  Object.entries(rest).forEach(([key, value]) => {
    fallback.setAttribute(key, value)
  })

  return fallback
}
