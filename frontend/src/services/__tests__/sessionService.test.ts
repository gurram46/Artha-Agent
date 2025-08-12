import { sessionService } from '../sessionService'

// Mock fetch
const mockFetch = jest.fn()
global.fetch = mockFetch

describe('SessionService', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  describe('setSessionData', () => {
    it('should make POST request to session endpoint', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      })

      await sessionService.setSessionData('testKey', { data: 'testValue' })

      expect(mockFetch).toHaveBeenCalledWith('/api/session/set', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          key: 'testKey',
          value: { data: 'testValue' },
        }),
      })
    })

    it('should throw error when request fails', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      })

      await expect(sessionService.setSessionData('testKey', 'testValue'))
        .rejects.toThrow('Failed to set session data: 500 Internal Server Error')
    })

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      await expect(sessionService.setSessionData('testKey', 'testValue'))
        .rejects.toThrow('Network error')
    })
  })

  describe('getSessionData', () => {
    it('should make GET request to session endpoint', async () => {
      const mockData = { data: 'testValue' }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ value: mockData }),
      })

      const result = await sessionService.getSessionData('testKey')

      expect(mockFetch).toHaveBeenCalledWith('/api/session/get?key=testKey', {
        method: 'GET',
        credentials: 'include',
      })
      expect(result).toEqual(mockData)
    })

    it('should return null when session data not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      })

      const result = await sessionService.getSessionData('nonexistentKey')
      expect(result).toBeNull()
    })

    it('should throw error for non-404 failures', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      })

      await expect(sessionService.getSessionData('testKey'))
        .rejects.toThrow('Failed to get session data: 500 Internal Server Error')
    })
  })

  describe('removeSessionData', () => {
    it('should make DELETE request to session endpoint', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      })

      await sessionService.removeSessionData('testKey')

      expect(mockFetch).toHaveBeenCalledWith('/api/session/remove', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ key: 'testKey' }),
      })
    })
  })

  describe('clearSessionData', () => {
    it('should make DELETE request to clear endpoint', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      })

      await sessionService.clearSessionData()

      expect(mockFetch).toHaveBeenCalledWith('/api/session/clear', {
        method: 'DELETE',
        credentials: 'include',
      })
    })
  })

  describe('migrateFromLocalStorage', () => {
    it('should migrate sensitive data from localStorage to session', async () => {
      // Setup localStorage with sensitive data
      const userData = { id: '1', name: 'Test User' }
      const authToken = 'test-token'
      
      localStorage.setItem('userData', JSON.stringify(userData))
      localStorage.setItem('authToken', authToken)
      localStorage.setItem('nonSensitiveData', 'keep-this')

      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      })

      await sessionService.migrateFromLocalStorage()

      // Should have called setSessionData for sensitive data
      expect(mockFetch).toHaveBeenCalledWith('/api/session/set', 
        expect.objectContaining({
          body: JSON.stringify({ key: 'userData', value: userData }),
        })
      )
      expect(mockFetch).toHaveBeenCalledWith('/api/session/set',
        expect.objectContaining({
          body: JSON.stringify({ key: 'authToken', value: authToken }),
        })
      )

      // Should have removed sensitive data from localStorage
      expect(localStorage.getItem('userData')).toBeNull()
      expect(localStorage.getItem('authToken')).toBeNull()
      
      // Should have kept non-sensitive data
      expect(localStorage.getItem('nonSensitiveData')).toBe('keep-this')
    })

    it('should handle migration errors gracefully', async () => {
      localStorage.setItem('userData', JSON.stringify({ id: '1' }))
      
      mockFetch.mockRejectedValueOnce(new Error('Migration failed'))
      
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})

      await sessionService.migrateFromLocalStorage()

      expect(consoleSpy).toHaveBeenCalledWith(
        'Error migrating userData from localStorage:',
        expect.any(Error)
      )

      consoleSpy.mockRestore()
    })
  })

  describe('fallback methods', () => {
    describe('setLocalData', () => {
      it('should set data in localStorage', () => {
        sessionService.setLocalData('testKey', 'testValue')
        expect(localStorage.setItem).toHaveBeenCalledWith('testKey', JSON.stringify('testValue'))
      })

      it('should handle localStorage errors', () => {
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
        ;(localStorage.setItem as jest.Mock).mockImplementationOnce(() => {
          throw new Error('Storage error')
        })

        sessionService.setLocalData('testKey', 'testValue')
        expect(consoleSpy).toHaveBeenCalled()

        consoleSpy.mockRestore()
      })
    })

    describe('getLocalData', () => {
      it('should get data from localStorage', () => {
        ;(localStorage.getItem as jest.Mock).mockReturnValueOnce(JSON.stringify('testValue'))
        
        const result = sessionService.getLocalData('testKey')
        expect(result).toBe('testValue')
      })

      it('should return null for non-existent keys', () => {
        ;(localStorage.getItem as jest.Mock).mockReturnValueOnce(null)
        
        const result = sessionService.getLocalData('nonexistent')
        expect(result).toBeNull()
      })

      it('should handle JSON parse errors', () => {
        ;(localStorage.getItem as jest.Mock).mockReturnValueOnce('invalid-json')
        
        const result = sessionService.getLocalData('testKey')
        expect(result).toBeNull()
      })
    })

    describe('removeLocalData', () => {
      it('should remove data from localStorage', () => {
        sessionService.removeLocalData('testKey')
        expect(localStorage.removeItem).toHaveBeenCalledWith('testKey')
      })
    })
  })
})