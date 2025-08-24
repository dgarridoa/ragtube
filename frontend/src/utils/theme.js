// Theme management utilities
export function initTheme() {
  const themeToggle = document.getElementById('theme-toggle')
  const htmlElement = document.documentElement

  // Theme toggle handler
  themeToggle?.addEventListener('click', () => {
    const isDark = htmlElement.classList.contains('dark')

    if (isDark) {
      htmlElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    } else {
      htmlElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    }

    updateThemeIcon(themeToggle, !isDark)
  })

  // Update icon based on current theme
  updateThemeIcon(themeToggle, htmlElement.classList.contains('dark'))

  // Listen for system theme changes
  window
    .matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', e => {
      if (!localStorage.getItem('theme')) {
        if (e.matches) {
          htmlElement.classList.add('dark')
        } else {
          htmlElement.classList.remove('dark')
        }
        updateThemeIcon(themeToggle, e.matches)
      }
    })
}

function updateThemeIcon(button, isDark) {
  if (!button) return

  const iconSvg = button.querySelector('svg')
  if (!iconSvg) return

  if (isDark) {
    // Moon icon for dark mode
    iconSvg.innerHTML = `
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z">
      </path>
    `
  } else {
    // Sun icon for light mode
    iconSvg.innerHTML = `
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z">
      </path>
    `
  }
}

export function getCurrentTheme() {
  return document.documentElement.classList.contains('dark') ? 'dark' : 'light'
}
