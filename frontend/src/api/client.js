// API client for communicating with the FastAPI backend
export class APIClient {
  constructor(baseURL = null) {
    if (!baseURL) {
      const currentHost = window.location.hostname
      const isLocalhost =
        currentHost === 'localhost' || currentHost === '127.0.0.1'
      if (isLocalhost) {
        this.baseURL = `http://localhost:5000`
      } else {
        this.baseURL = `https://${currentHost}/api`
      }
    } else {
      this.baseURL = baseURL
    }
  }

  async checkReadiness() {
    try {
      const response = await fetch(`${this.baseURL}/readiness`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Readiness check failed:', error)
      throw error
    }
  }

  async getChannels() {
    try {
      const response = await fetch(`${this.baseURL}/channel`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Failed to fetch channels:', error)
      throw error
    }
  }

  async *streamRAGResponse(input, channelId = null, signal = null) {
    try {
      const params = new URLSearchParams({ input })
      if (channelId) {
        params.append('channel_id', channelId)
      }

      const response = await fetch(`${this.baseURL}/rag?${params}`, {
        method: 'GET',
        headers: {
          Accept: 'application/x-ndjson',
        },
        signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      try {
        while (true) {
          const { done, value } = await reader.read()

          if (done) break

          const chunk = decoder.decode(value, { stream: true })
          buffer += chunk

          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (line.trim()) {
              try {
                const data = JSON.parse(line)
                yield data
              } catch (parseError) {
                console.warn('Failed to parse JSON line:', line, parseError)
              }
            }
          }
        }

        if (buffer.trim()) {
          try {
            const data = JSON.parse(buffer)
            yield data
          } catch (parseError) {
            console.warn('Failed to parse final JSON line:', buffer, parseError)
          }
        }
      } finally {
        reader.releaseLock()
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('RAG stream error:', error)
      }
      throw error
    }
  }
}
