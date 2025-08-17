import { cn } from '../../lib/utils.js'

export function createCard(props = {}) {
  const { className = '', children, ...rest } = props

  const card = document.createElement('div')
  card.className = cn(
    'rounded-lg border bg-card text-card-foreground shadow-sm',
    className
  )

  if (children) {
    if (typeof children === 'string') {
      card.innerHTML = children
    } else if (Array.isArray(children)) {
      children.forEach(child => {
        if (typeof child === 'string') {
          card.insertAdjacentHTML('beforeend', child)
        } else if (child instanceof HTMLElement) {
          card.appendChild(child)
        }
      })
    } else if (children instanceof HTMLElement) {
      card.appendChild(children)
    }
  }

  Object.entries(rest).forEach(([key, value]) => {
    card.setAttribute(key, value)
  })

  return card
}

export function createCardHeader(props = {}) {
  const { className = '', children, ...rest } = props

  const header = document.createElement('div')
  header.className = cn('flex flex-col space-y-1.5 p-6', className)

  if (children) {
    if (typeof children === 'string') {
      header.innerHTML = children
    } else if (children instanceof HTMLElement) {
      header.appendChild(children)
    }
  }

  Object.entries(rest).forEach(([key, value]) => {
    header.setAttribute(key, value)
  })

  return header
}

export function createCardTitle(props = {}) {
  const { className = '', children, ...rest } = props

  const title = document.createElement('h3')
  title.className = cn(
    'text-2xl font-semibold leading-none tracking-tight',
    className
  )

  if (typeof children === 'string') {
    title.textContent = children
  } else if (children instanceof HTMLElement) {
    title.appendChild(children)
  }

  Object.entries(rest).forEach(([key, value]) => {
    title.setAttribute(key, value)
  })

  return title
}

export function createCardDescription(props = {}) {
  const { className = '', children, ...rest } = props

  const description = document.createElement('p')
  description.className = cn('text-sm text-muted-foreground', className)

  if (typeof children === 'string') {
    description.textContent = children
  } else if (children instanceof HTMLElement) {
    description.appendChild(children)
  }

  Object.entries(rest).forEach(([key, value]) => {
    description.setAttribute(key, value)
  })

  return description
}

export function createCardContent(props = {}) {
  const { className = '', children, ...rest } = props

  const content = document.createElement('div')
  content.className = cn('p-6 pt-0', className)

  if (children) {
    if (typeof children === 'string') {
      content.innerHTML = children
    } else if (Array.isArray(children)) {
      children.forEach(child => {
        if (typeof child === 'string') {
          content.insertAdjacentHTML('beforeend', child)
        } else if (child instanceof HTMLElement) {
          content.appendChild(child)
        }
      })
    } else if (children instanceof HTMLElement) {
      content.appendChild(children)
    }
  }

  Object.entries(rest).forEach(([key, value]) => {
    content.setAttribute(key, value)
  })

  return content
}

export function createCardFooter(props = {}) {
  const { className = '', children, ...rest } = props

  const footer = document.createElement('div')
  footer.className = cn('flex items-center p-6 pt-0', className)

  if (children) {
    if (typeof children === 'string') {
      footer.innerHTML = children
    } else if (children instanceof HTMLElement) {
      footer.appendChild(children)
    }
  }

  Object.entries(rest).forEach(([key, value]) => {
    footer.setAttribute(key, value)
  })

  return footer
}
