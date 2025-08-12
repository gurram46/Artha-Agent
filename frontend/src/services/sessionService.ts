/**
 * Secure Session Service for Artha AI
 * Replaces localStorage for sensitive data with secure server-side sessions
 */

interface SessionData {
  userData?: any;
  financialData?: any;
  authToken?: string;
  userRiskProfile?: any;
  conversationId?: string;
}

class SessionService {
  private readonly API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  private sessionId: string | null = null;

  constructor() {
    // Only store non-sensitive session ID in localStorage
    this.sessionId = localStorage.getItem('sessionId');
    if (!this.sessionId) {
      this.sessionId = this.generateSessionId();
      localStorage.setItem('sessionId', this.sessionId);
    }
  }

  private generateSessionId(): string {
    return 'sess_' + Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
  }

  /**
   * Store sensitive data on server-side session
   */
  async setSessionData(key: string, value: any): Promise<boolean> {
    try {
      const response = await fetch(`${this.API_BASE}/api/session/set`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for session management
        body: JSON.stringify({
          sessionId: this.sessionId,
          key,
          value: JSON.stringify(value)
        })
      });

      return response.ok;
    } catch (error) {
      console.error('Failed to set session data:', error);
      return false;
    }
  }

  /**
   * Retrieve sensitive data from server-side session
   */
  async getSessionData(key: string): Promise<any> {
    try {
      const response = await fetch(`${this.API_BASE}/api/session/get`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          sessionId: this.sessionId,
          key
        })
      });

      if (response.ok) {
        const data = await response.json();
        return data.value ? JSON.parse(data.value) : null;
      }
      return null;
    } catch (error) {
      console.error('Failed to get session data:', error);
      return null;
    }
  }

  /**
   * Remove specific session data
   */
  async removeSessionData(key: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.API_BASE}/api/session/remove`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          sessionId: this.sessionId,
          key
        })
      });

      return response.ok;
    } catch (error) {
      console.error('Failed to remove session data:', error);
      return false;
    }
  }

  /**
   * Clear all session data
   */
  async clearSession(): Promise<boolean> {
    try {
      const response = await fetch(`${this.API_BASE}/api/session/clear`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          sessionId: this.sessionId
        })
      });

      if (response.ok) {
        // Generate new session ID
        this.sessionId = this.generateSessionId();
        localStorage.setItem('sessionId', this.sessionId);
      }

      return response.ok;
    } catch (error) {
      console.error('Failed to clear session:', error);
      return false;
    }
  }

  /**
   * Fallback methods for non-sensitive data (can still use localStorage)
   */
  setLocalData(key: string, value: any): void {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Failed to set local data:', error);
    }
  }

  getLocalData(key: string): any {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Failed to get local data:', error);
      return null;
    }
  }

  removeLocalData(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to remove local data:', error);
    }
  }

  /**
   * Migration helper: Move existing localStorage data to secure sessions
   */
  async migrateFromLocalStorage(): Promise<void> {
    const sensitiveKeys = [
      'userData',
      'authToken', 
      'userRiskProfile',
      'current_conversation_id',
      'artha_user_id'
    ];

    for (const key of sensitiveKeys) {
      const value = localStorage.getItem(key);
      if (value) {
        await this.setSessionData(key, JSON.parse(value));
        localStorage.removeItem(key);
      }
    }

    // Migrate financial data
    const financialKeys = [
      'financial_portfolioHealth',
      'financial_riskAssessment', 
      'financial_tripPlanning',
      'financial_lastUpdated'
    ];

    for (const key of financialKeys) {
      const value = localStorage.getItem(key);
      if (value) {
        await this.setSessionData(key, JSON.parse(value));
        localStorage.removeItem(key);
      }
    }
  }
}

const sessionService = new SessionService();
export { sessionService };
export default sessionService;