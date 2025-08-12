import React from 'react'
import { render, screen, waitFor, act } from '@testing-library/react'
import { AppProvider, useAppContext, UserData } from '../AppContext'
import { sessionService } from '../../services/sessionService'

// Mock the session service
jest.mock('../../services/sessionService', () => ({
  sessionService: {
    getSessionData: jest.fn(),
    setSessionData: jest.fn(),
    removeSessionData: jest.fn(),
    migrateFromLocalStorage: jest.fn(),
  },
}))

const mockSessionService = sessionService as jest.Mocked<typeof sessionService>

// Test component that uses the context
function TestComponent() {
  const { state, dispatch } = useAppContext()
  
  return (
    <div>
      <div data-testid="loading">{state.loading ? 'loading' : 'not-loading'}</div>
      <div data-testid="authenticated">{state.isAuthenticated ? 'authenticated' : 'not-authenticated'}</div>
      <div data-testid="user">{state.user ? state.user.name : 'no-user'}</div>
      <div data-testid="demo-mode">{state.demoMode ? 'demo' : 'not-demo'}</div>
      <button 
        data-testid="set-user" 
        onClick={() => dispatch({ 
          type: 'SET_USER', 
          payload: { id: '1', email: 'test@example.com', name: 'Test User' } 
        })}
      >
        Set User
      </button>
      <button 
        data-testid="logout" 
        onClick={() => dispatch({ type: 'LOGOUT' })}
      >
        Logout
      </button>
    </div>
  )
}

describe('AppContext', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockSessionService.getSessionData.mockResolvedValue(null)
    mockSessionService.setSessionData.mockResolvedValue(undefined)
    mockSessionService.removeSessionData.mockResolvedValue(undefined)
    mockSessionService.migrateFromLocalStorage.mockResolvedValue(undefined)
  })

  it('should provide initial state', async () => {
    render(
      <AppProvider>
        <TestComponent />
      </AppProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('not-loading')
    })

    expect(screen.getByTestId('authenticated')).toHaveTextContent('not-authenticated')
    expect(screen.getByTestId('user')).toHaveTextContent('no-user')
    expect(screen.getByTestId('demo-mode')).toHaveTextContent('not-demo')
  })

  it('should load user data from session service on mount', async () => {
    const mockUser: UserData = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User'
    }

    mockSessionService.getSessionData.mockImplementation((key) => {
      if (key === 'userData') return Promise.resolve(mockUser)
      if (key === 'authToken') return Promise.resolve('mock-token')
      return Promise.resolve(null)
    })

    render(
      <AppProvider>
        <TestComponent />
      </AppProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('not-loading')
    })

    expect(screen.getByTestId('authenticated')).toHaveTextContent('authenticated')
    expect(screen.getByTestId('user')).toHaveTextContent('Test User')
    expect(mockSessionService.migrateFromLocalStorage).toHaveBeenCalled()
    expect(mockSessionService.getSessionData).toHaveBeenCalledWith('userData')
    expect(mockSessionService.getSessionData).toHaveBeenCalledWith('authToken')
  })

  it('should save user data to session service when user is set', async () => {
    render(
      <AppProvider>
        <TestComponent />
      </AppProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('not-loading')
    })

    await act(async () => {
      screen.getByTestId('set-user').click()
    })

    await waitFor(() => {
      expect(mockSessionService.setSessionData).toHaveBeenCalledWith('userData', {
        id: '1',
        email: 'test@example.com',
        name: 'Test User'
      })
    })

    expect(screen.getByTestId('authenticated')).toHaveTextContent('authenticated')
    expect(screen.getByTestId('user')).toHaveTextContent('Test User')
  })

  it('should remove user data from session service on logout', async () => {
    render(
      <AppProvider>
        <TestComponent />
      </AppProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('not-loading')
    })

    // Set user first
    await act(async () => {
      screen.getByTestId('set-user').click()
    })

    // Then logout
    await act(async () => {
      screen.getByTestId('logout').click()
    })

    await waitFor(() => {
      expect(mockSessionService.removeSessionData).toHaveBeenCalledWith('userData')
      expect(mockSessionService.removeSessionData).toHaveBeenCalledWith('authToken')
    })

    expect(screen.getByTestId('authenticated')).toHaveTextContent('not-authenticated')
    expect(screen.getByTestId('user')).toHaveTextContent('no-user')
  })

  it('should handle session service errors gracefully', async () => {
    mockSessionService.getSessionData.mockRejectedValue(new Error('Session service error'))

    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})

    render(
      <AppProvider>
        <TestComponent />
      </AppProvider>
    )

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error loading persisted state:', expect.any(Error))
    })

    consoleSpy.mockRestore()
  })

  it('should preserve demo mode on logout', async () => {
    // Mock sessionStorage for demo mode
    const mockSessionStorage = {
      getItem: jest.fn().mockReturnValue('true'),
      setItem: jest.fn(),
    }
    Object.defineProperty(window, 'sessionStorage', {
      value: mockSessionStorage,
      writable: true,
    })

    render(
      <AppProvider>
        <TestComponent />
      </AppProvider>
    )

    await waitFor(() => {
      expect(screen.getByTestId('demo-mode')).toHaveTextContent('demo')
    })

    // Set user and then logout
    await act(async () => {
      screen.getByTestId('set-user').click()
    })

    await act(async () => {
      screen.getByTestId('logout').click()
    })

    // Demo mode should be preserved
    expect(screen.getByTestId('demo-mode')).toHaveTextContent('demo')
  })

  it('should throw error when used outside provider', () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})

    expect(() => {
      render(<TestComponent />)
    }).toThrow('useAppContext must be used within an AppProvider')

    consoleSpy.mockRestore()
  })
})