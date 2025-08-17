// API client for communicating with the FastAPI backend
export class APIClient {
  constructor(baseURL = `http://${window.location.hostname}:5000`) {
    this.baseURL = baseURL
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

  async *streamRAGResponse(input, channelId = null) {
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
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      try {
        while (true) {
          const { done, value } = await reader.read()

          if (done) break

          const chunk = decoder.decode(value, { stream: true })
          const lines = chunk.split('\n').filter(line => line.trim())

          for (const line of lines) {
            try {
              const data = JSON.parse(line)
              yield data
            } catch (parseError) {
              console.warn('Failed to parse JSON line:', line, parseError)
            }
          }
        }
      } finally {
        reader.releaseLock()
      }
    } catch (error) {
      console.error('RAG stream error:', error)
      throw error
    }
  }
}
