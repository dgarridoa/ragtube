import { cn } from '../../lib/utils.js'

const buttonVariants = {
  variant: {
    default: 'bg-primary text-primary-foreground hover:bg-primary/90',
    destructive:
      'bg-destructive text-destructive-foreground hover:bg-destructive/90',
    outline:
      'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    link: 'text-primary underline-offset-4 hover:underline',
  },
  size: {
    default: 'h-10 px-4 py-2',
    sm: 'h-9 rounded-md px-3',
    lg: 'h-11 rounded-md px-8',
    icon: 'h-10 w-10',
  },
}

export function createButton(props = {}) {
  const {
    variant = 'default',
    size = 'default',
    className = '',
    children = '',
    ...rest
  } = props

  const button = document.createElement('button')

  const variantClasses =
    buttonVariants.variant[variant] || buttonVariants.variant.default
  const sizeClasses = buttonVariants.size[size] || buttonVariants.size.default

  button.className = cn(
    'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
    variantClasses,
    sizeClasses,
    className
  )

  if (typeof children === 'string') {
    button.textContent = children
  } else if (children instanceof HTMLElement) {
    button.appendChild(children)
  }

  // Apply other properties
  Object.entries(rest).forEach(([key, value]) => {
    if (key.startsWith('on')) {
      const eventName = key.slice(2).toLowerCase()
      button.addEventListener(eventName, value)
    } else {
      button.setAttribute(key, value)
    }
  })

  return button
}
