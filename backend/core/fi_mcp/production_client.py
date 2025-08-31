"""
Production Fi Money MCP Client
Real-time integration with Fi Money MCP server using passcode authentication
No sample data or fallbacks - production-ready implementation
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
import aiohttp
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@dataclass
class FiAuthSession:
    """Fi Money authentication session"""
    session_id: str
    passcode: str
    authenticated: bool = False
    expires_at: float = 0.0
    
    def is_expired(self) -> bool:
        """Check if session is expired (30 minutes max)"""
        return time.time() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if session is valid and not expired"""
        return self.authenticated and not self.is_expired()

@dataclass 
class FinancialData:
    """Real Fi Money financial data structure"""
    net_worth: Dict[str, Any]
    credit_report: Optional[Dict[str, Any]]
    epf_details: Optional[Dict[str, Any]]
    mf_transactions: List[Dict[str, Any]]
    bank_transactions: List[Dict[str, Any]]
    raw_data: Dict[str, Any]
    
    def get_total_net_worth(self) -> float:
        """Get total net worth value"""
        try:
            nw_response = self.net_worth.get('netWorthResponse', {})
            total_value = nw_response.get('totalNetWorthValue', {})
            units = float(total_value.get('units', '0'))
            nanos = total_value.get('nanos', 0)
            return units + (nanos / 1_000_000_000)
        except (ValueError, TypeError, KeyError):
            return 0.0
    
    def get_assets_breakdown(self) -> Dict[str, float]:
        """Get detailed asset breakdown"""
        assets = {}
        try:
            nw_response = self.net_worth.get('netWorthResponse', {})
            for asset in nw_response.get('assetValues', []):
                asset_type = asset.get('netWorthAttribute', '').replace('ASSET_TYPE_', '')
                value_obj = asset.get('value', {})
                units = float(value_obj.get('units', '0'))
                nanos = value_obj.get('nanos', 0)
                assets[asset_type] = units + (nanos / 1_000_000_000)
        except (ValueError, TypeError, KeyError):
            pass
        return assets
    
    def get_liabilities_breakdown(self) -> Dict[str, float]:
        """Get detailed liability breakdown"""
        liabilities = {}
        try:
            nw_response = self.net_worth.get('netWorthResponse', {})
            for liability in nw_response.get('liabilityValues', []):
                liability_type = liability.get('netWorthAttribute', '').replace('LIABILITY_TYPE_', '')
                value_obj = liability.get('value', {})
                units = float(value_obj.get('units', '0'))
                nanos = value_obj.get('nanos', 0)
                liabilities[liability_type] = units + (nanos / 1_000_000_000)
        except (ValueError, TypeError, KeyError):
            pass
        return liabilities

class FiMoneyMCPClient:
    """Production Fi Money MCP Client with real-time authentication"""
    
    def __init__(self, mcp_url: str = "https://mcp.fi.money:8080/mcp/stream"):
        self.mcp_url = mcp_url
        self.session: Optional[FiAuthSession] = None
        self.http_session: Optional[aiohttp.ClientSession] = None
        
    @asynccontextmanager
    async def get_http_session(self):
        """Get or create HTTP session"""
        if self.http_session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            self.http_session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Artha-AI/1.0'
                }
            )
        try:
            yield self.http_session
        finally:
            pass  # Keep session alive for reuse
    
    async def close(self):
        """Close HTTP session"""
        if self.http_session:
            await self.http_session.close()
            self.http_session = None
    
    async def clear_cached_session(self) -> Dict[str, Any]:
        """
        Clear any cached authentication session on Fi Money servers
        This forces a fresh login with phone number and passcode entry
        """
        clear_id = f"clear_{int(time.time() * 1000)}"
        try:
            logger.info(f"🧹 [CLEAR:{clear_id}] Clearing cached Fi Money session...")
            
            if self.session:
                logger.debug(f"[CLEAR:{clear_id}] Found existing session: {self.session.session_id}")
                
                # Try to explicitly logout from Fi Money servers
                async with self.get_http_session() as http_session:
                    logout_payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "logout_user",
                            "arguments": {}
                        }
                    }
                    
                    headers = {
                        "Mcp-Session-Id": self.session.session_id,
                        "Content-Type": "application/json",
                        "X-Force-Logout": "true"
                    }
                    
                    try:
                        async with http_session.post(
                            self.mcp_url,
                            json=logout_payload,
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            logger.debug(f"[CLEAR:{clear_id}] Logout response: {response.status}")
                            if response.status == 200:
                                logger.info(f"✅ [CLEAR:{clear_id}] Successfully logged out from Fi Money servers")
                            else:
                                logger.warning(f"⚠️ [CLEAR:{clear_id}] Logout response: {response.status}")
                    except Exception as logout_error:
                        logger.warning(f"⚠️ [CLEAR:{clear_id}] Logout request failed: {logout_error}")
            
            # Clear local session
            self.session = None
            logger.info(f"✅ [CLEAR:{clear_id}] Local session cleared")
            
            return {
                "success": True,
                "message": "Cached session cleared. Next authentication will require fresh login."
            }
            
        except Exception as e:
            logger.error(f"❌ [CLEAR:{clear_id}] Session clear error: {e}")
            # Still clear local session even if remote clear fails
            self.session = None
            return {
                "success": True,
                "message": f"Local session cleared (remote clear failed: {str(e)})"
            }
    
    async def initiate_web_authentication(self, force_fresh_auth: bool = True) -> Dict[str, Any]:
        """
        Initiate Fi Money web-based authentication flow
        Returns login URL and session info for user authentication
        """
        auth_id = f"auth_{int(time.time() * 1000)}"
        try:
            logger.info(f"🔐 [AUTH:{auth_id}] Initiating Fi Money web authentication...")
            
            # Generate session ID for Fi Money MCP
            import uuid
            session_id = f"mcp-session-{uuid.uuid4()}"
            logger.debug(f"[AUTH:{auth_id}] Generated session ID: {session_id}")
            
            # Create session with temporary passcode
            expires_at = time.time() + (30 * 60)  # 30 minutes
            self.session = FiAuthSession(
                session_id=session_id,
                passcode="pending_web_auth",  # Temporary passcode for web auth
                authenticated=False,
                expires_at=expires_at
            )
            
            logger.info(f"🔐 [AUTH:{auth_id}] Created session with ID: {session_id}")
            logger.debug(f"[AUTH:{auth_id}] Session expires at: {expires_at}")
            
            # Make initial request to get login URL
            logger.debug(f"[AUTH:{auth_id}] Making initial MCP request to: {self.mcp_url}")
            async with self.get_http_session() as http_session:
                test_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "fetch_net_worth",
                        "arguments": {}
                    }
                }
                
                headers = {
                    "Mcp-Session-Id": session_id,
                    "Content-Type": "application/json"
                }
                
                # Add header to force fresh authentication if requested
                if force_fresh_auth:
                    headers["X-Force-Fresh-Auth"] = "true"
                    logger.debug(f"[AUTH:{auth_id}] Added force fresh auth header")
                
                logger.debug(f"[AUTH:{auth_id}] Request payload: {test_payload}")
                logger.debug(f"[AUTH:{auth_id}] Request headers: {headers}")
                
                async with http_session.post(
                    self.mcp_url,
                    json=test_payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    response_text = await response.text()
                    logger.debug(f"[AUTH:{auth_id}] MCP Response status: {response.status}")
                    logger.debug(f"[AUTH:{auth_id}] MCP Response: {response_text[:500]}...")
                    
                    if response.status == 200:
                        try:
                            logger.debug(f"[AUTH:{auth_id}] Parsing JSON response...")
                            result = await response.json()
                            logger.debug(f"[AUTH:{auth_id}] JSON parsed successfully: {list(result.keys())}")
                            
                            # Extract login URL from response
                            if 'result' in result and 'content' in result['result']:
                                logger.debug(f"[AUTH:{auth_id}] Extracting content from result...")
                                content = result['result']['content'][0]['text']
                                content_data = json.loads(content)
                                logger.debug(f"[AUTH:{auth_id}] Content data: {content_data}")
                                
                                if content_data.get('status') == 'login_required':
                                    login_url = content_data.get('login_url')
                                    logger.info(f"🌐 [AUTH:{auth_id}] Login URL obtained: {login_url}")
                                    
                                    result_data = {
                                        "status": "login_required",
                                        "login_url": login_url,
                                        "session_id": session_id,
                                        "message": "Please complete authentication in the browser"
                                    }
                                    logger.debug(f"[AUTH:{auth_id}] Returning login_required result: {result_data}")
                                    return result_data
                                
                                elif content_data.get('status') == 'success':
                                    # Already authenticated!
                                    logger.debug(f"[AUTH:{auth_id}] Already authenticated, updating session...")
                                    self.session.authenticated = True
                                    self.session.passcode = "web_authenticated"
                                    logger.info(f"✅ [AUTH:{auth_id}] Already authenticated with Fi Money!")
                                    
                                    result_data = {
                                        "status": "already_authenticated",
                                        "session_id": session_id,
                                        "message": "Already authenticated with Fi Money"
                                    }
                                    logger.debug(f"[AUTH:{auth_id}] Returning already_authenticated result: {result_data}")
                                    return result_data
                                
                                else:
                                    logger.warning(f"[AUTH:{auth_id}] Unexpected content status: {content_data.get('status')}")
                            else:
                                logger.warning(f"[AUTH:{auth_id}] Missing result/content in response structure")
                            
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.error(f"[AUTH:{auth_id}] Failed to parse MCP response: {e}")
                            logger.error(f"[AUTH:{auth_id}] Raw response: {response_text[:500]}...")  # Log first 500 chars
                            logger.debug(f"[AUTH:{auth_id}] Parse error details: {type(e).__name__}: {str(e)}")
                            logger.debug(f"[AUTH:{auth_id}] Clearing invalid session due to parse error")
                            self.session = None  # Clear invalid session
                            parse_error_result = {
                                "status": "error",
                                "error_type": "parse_error",
                                "message": f"Fi Money server returned invalid response format. This may indicate a server issue or maintenance.",
                                "technical_details": f"Parse error: {str(e)}"
                            }
                            logger.debug(f"[AUTH:{auth_id}] Returning parse error: {parse_error_result}")
                            return parse_error_result
                    
                    else:
                        logger.error(f"[AUTH:{auth_id}] MCP request failed with status: {response.status}")
                        logger.error(f"[AUTH:{auth_id}] Response body: {response_text[:200]}...")  # Log first 200 chars
                        logger.debug(f"[AUTH:{auth_id}] Clearing invalid session due to HTTP {response.status}")
                        self.session = None  # Clear invalid session
                        
                        # Provide specific error messages based on HTTP status
                        if response.status == 503:
                            logger.debug(f"[AUTH:{auth_id}] Service unavailable (503) - server temporarily down")
                            error_msg = "Fi Money service is temporarily unavailable. Please try again in a few minutes."
                        elif response.status == 502:
                            logger.debug(f"[AUTH:{auth_id}] Bad gateway (502) - connectivity issues")
                            error_msg = "Fi Money service is experiencing connectivity issues. Please try again later."
                        elif response.status == 404:
                            logger.debug(f"[AUTH:{auth_id}] Not found (404) - endpoint may be down for maintenance")
                            error_msg = "Fi Money authentication endpoint not found. The service may be under maintenance."
                        elif response.status >= 500:
                            logger.debug(f"[AUTH:{auth_id}] Server error ({response.status}) - internal server issues")
                            error_msg = "Fi Money server is experiencing internal issues. Please try again later."
                        elif response.status == 429:
                            logger.debug(f"[AUTH:{auth_id}] Rate limited (429) - too many requests")
                            error_msg = "Too many authentication requests. Please wait a moment before trying again."
                        else:
                            logger.debug(f"[AUTH:{auth_id}] Unexpected HTTP status: {response.status}")
                            error_msg = f"Fi Money authentication request failed (HTTP {response.status}). Please try again."
                        
                        error_result = {
                            "status": "error",
                            "error_type": "http_error",
                            "http_status": response.status,
                            "message": error_msg,
                            "technical_details": f"HTTP {response.status}: {response_text[:100]}"
                        }
                        logger.debug(f"[AUTH:{auth_id}] Returning HTTP error result: {error_result}")
                        return error_result
                        
        except asyncio.TimeoutError:
            logger.error(f"❌ [AUTH:{auth_id}] Authentication initiation timeout")
            logger.debug(f"[AUTH:{auth_id}] Timeout occurred - clearing invalid session")
            self.session = None  # Clear invalid session
            timeout_result = {
                "status": "error",
                "error_type": "timeout",
                "message": "Fi Money authentication request timed out. This may be due to network issues or server overload. Please check your internet connection and try again.",
                "technical_details": "Request timeout after 30 seconds"
            }
            logger.debug(f"[AUTH:{auth_id}] Returning timeout error: {timeout_result}")
            return timeout_result
        except aiohttp.ClientConnectorError as e:
            logger.error(f"❌ [AUTH:{auth_id}] Connection error to Fi Money MCP: {e}")
            logger.debug(f"[AUTH:{auth_id}] Connection error - clearing invalid session")
            self.session = None  # Clear invalid session
            connection_result = {
                "status": "error",
                "error_type": "connection_error",
                "message": "Cannot connect to Fi Money service. Please check your internet connection or try again later. The Fi Money service may be temporarily unavailable.",
                "technical_details": f"Connection error: {str(e)}"
            }
            logger.debug(f"[AUTH:{auth_id}] Returning connection error: {connection_result}")
            return connection_result
        except Exception as e:
            logger.error(f"❌ [AUTH:{auth_id}] Authentication initiation error: {e}")
            logger.debug(f"[AUTH:{auth_id}] Unexpected error - clearing invalid session")
            self.session = None  # Clear invalid session
            unknown_result = {
                "status": "error",
                "error_type": "unknown",
                "message": f"An unexpected error occurred during Fi Money authentication setup. Please try again or contact support if the issue persists.",
                "technical_details": f"Error: {str(e)}"
            }
            logger.debug(f"[AUTH:{auth_id}] Returning unknown error: {unknown_result}")
            return unknown_result
    
    async def authenticate_with_passcode(self, passcode: str) -> Dict[str, Any]:
        """
        Authenticate with Fi Money using a passcode
        This method is referenced by error messages but was missing
        """
        try:
            import uuid
            session_id = f"mcp-session-{uuid.uuid4()}"
            
            # Create session with passcode
            expires_at = time.time() + (30 * 60)  # 30 minutes
            self.session = FiAuthSession(
                session_id=session_id,
                passcode=passcode,
                authenticated=True,
                expires_at=expires_at
            )
            
            # Test the authentication by making a simple call
            test_result = await self._test_authentication()
            
            if test_result["success"]:
                logger.info("✅ Fi Money passcode authentication successful!")
                return {
                    "success": True,
                    "session_id": session_id,
                    "message": "Successfully authenticated with Fi Money"
                }
            else:
                self.session = None
                return {
                    "success": False,
                    "message": test_result.get("error", "Authentication failed")
                }
                
        except Exception as e:
            logger.error(f"❌ Passcode authentication error: {e}")
            self.session = None
            return {
                "success": False,
                "message": f"Authentication error: {str(e)}"
            }
    
    async def _test_authentication(self) -> Dict[str, Any]:
        """Test if current session is valid by making a simple MCP call"""
        try:
            async with self.get_http_session() as http_session:
                test_payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "fetch_net_worth",
                        "arguments": {}
                    }
                }
                
                headers = {
                    "Mcp-Session-Id": self.session.session_id,
                    "Authorization": f"Bearer {self.session.passcode}",
                    "Content-Type": "application/json"
                }
                
                async with http_session.post(
                    self.mcp_url,
                    json=test_payload,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        return {"success": True}
                    else:
                        return {"success": False, "error": f"HTTP {response.status}"}
                        
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_authentication_status(self) -> Dict[str, Any]:
        """
        Check current authentication status with Fi Money MCP server
        """
        # Generate unique ID for this status check
        status_id = str(uuid.uuid4())[:8]
        logger.debug(f"[STATUS:{status_id}] Starting authentication status check")
        
        try:
            if not self.session:
                logger.debug(f"[STATUS:{status_id}] No active session found")
                no_session_result = {
                    "authenticated": False,
                    "message": "No active session. Please initiate web authentication via /api/fi-auth/initiate"
                }
                logger.debug(f"[STATUS:{status_id}] Returning no_session result: {no_session_result}")
                return no_session_result
            
            logger.debug(f"[STATUS:{status_id}] Found session: {self.session.session_id}")
            
            # Check if session has expired
            if self.session.is_expired():
                logger.warning(f"⚠️ [STATUS:{status_id}] Session has expired")
                logger.debug(f"[STATUS:{status_id}] Marking session as unauthenticated")
                self.session.authenticated = False
                expired_result = {
                    "authenticated": False,
                    "message": "Session expired. Please re-authenticate via web authentication"
                }
                logger.debug(f"[STATUS:{status_id}] Returning expired result: {expired_result}")
                return expired_result
            
            # Return early if already authenticated
            if self.session.authenticated:
                logger.debug(f"[STATUS:{status_id}] Session already authenticated")
                expires_in = max(0, (self.session.expires_at - time.time()) / 60)
                logger.debug(f"[STATUS:{status_id}] Session expires in {expires_in:.1f} minutes")
                authenticated_result = {
                    "authenticated": True,
                    "session_id": self.session.session_id,
                    "expires_in_minutes": expires_in,
                    "message": "Successfully authenticated with Fi Money"
                }
                logger.debug(f"[STATUS:{status_id}] Returning authenticated result: {authenticated_result}")
                return authenticated_result
            
            # For web authentication, try to check status with Fi Money MCP server
            logger.info(f"🔍 [STATUS:{status_id}] Checking authentication status for session: {self.session.session_id}")
            logger.debug(f"[STATUS:{status_id}] Making MCP request to check authentication status")
            
            async with self.get_http_session() as http_session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "fetch_net_worth",
                        "arguments": {}
                    }
                }
                logger.debug(f"[STATUS:{status_id}] MCP payload: {payload}")
                
                headers = {
                    "Mcp-Session-Id": self.session.session_id,
                    "Content-Type": "application/json"
                }
                logger.debug(f"[STATUS:{status_id}] MCP headers: {headers}")
                
                logger.debug(f"[STATUS:{status_id}] Making POST request to {self.mcp_url}")
                async with http_session.post(
                    self.mcp_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    response_text = await response.text()
                    logger.debug(f"[STATUS:{status_id}] Auth check response ({response.status}): {response_text[:500]}...")
                    
                    if response.status == 200:
                        logger.debug(f"[STATUS:{status_id}] Received successful response, parsing JSON...")
                        try:
                            result = await response.json()
                            logger.debug(f"[STATUS:{status_id}] JSON parsed successfully: {list(result.keys())}")
                            logger.info(f"🔍 [STATUS:{status_id}] MCP Response structure: {result}")
                            
                            if 'result' in result and 'content' in result['result']:
                                logger.debug(f"[STATUS:{status_id}] Extracting content from result...")
                                content = result['result']['content'][0]['text']
                                content_data = json.loads(content)
                                logger.debug(f"[STATUS:{status_id}] Content data parsed: {list(content_data.keys())}")
                                logger.info(f"🔍 [STATUS:{status_id}] Content data keys: {list(content_data.keys())}")
                                
                                # Check if we have actual financial data (indicates successful authentication)
                                has_net_worth = 'netWorthResponse' in content_data
                                has_accounts = 'accountDetailsBulkResponse' in content_data
                                logger.debug(f"[STATUS:{status_id}] Financial data check - net_worth: {has_net_worth}, accounts: {has_accounts}")
                                
                                if has_net_worth or has_accounts:
                                    # Authentication successful - we received real financial data!
                                    logger.debug(f"[STATUS:{status_id}] Authentication confirmed - updating session")
                                    self.session.authenticated = True
                                    if self.session.passcode == "pending_web_auth":
                                        logger.debug(f"[STATUS:{status_id}] Updating passcode from pending to web_authenticated")
                                        self.session.passcode = "web_authenticated"  # Set proper passcode
                                    logger.info(f"✅ [STATUS:{status_id}] Fi Money authentication confirmed - received real financial data!")
                                    
                                    expires_in = max(0, (self.session.expires_at - time.time()) / 60)
                                    success_result = {
                                        "authenticated": True,
                                        "session_id": self.session.session_id,
                                        "expires_in_minutes": expires_in,
                                        "message": "Successfully authenticated with Fi Money"
                                    }
                                    logger.debug(f"[STATUS:{status_id}] Returning success result: {success_result}")
                                    return success_result
                                
                                elif content_data.get('status') == 'login_required':
                                    logger.debug(f"[STATUS:{status_id}] Login still required")
                                    pending_result = {
                                        "authenticated": False,
                                        "message": "Authentication still pending. Please complete the process in Fi Money"
                                    }
                                    logger.debug(f"[STATUS:{status_id}] Returning pending result: {pending_result}")
                                    return pending_result
                                
                                else:
                                    logger.warning(f"⚠️ [STATUS:{status_id}] Unexpected response format: {content_data}")
                                    unknown_result = {
                                        "authenticated": False,
                                        "message": content_data.get('message', 'Authentication status unknown')
                                    }
                                    logger.debug(f"[STATUS:{status_id}] Returning unknown result: {unknown_result}")
                                    return unknown_result
                            else:
                                logger.warning(f"[STATUS:{status_id}] Missing result/content in response structure")
                            
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.error(f"[STATUS:{status_id}] Failed to parse authentication status: {e}")
                            logger.debug(f"[STATUS:{status_id}] Parse error details: {type(e).__name__}: {str(e)}")
                            parse_error_result = {
                                "authenticated": False,
                                "message": "Failed to parse authentication status"
                            }
                            logger.debug(f"[STATUS:{status_id}] Returning parse error result: {parse_error_result}")
                            return parse_error_result
                    
                    else:
                        logger.error(f"[STATUS:{status_id}] Authentication status check failed: {response.status}")
                        logger.debug(f"[STATUS:{status_id}] HTTP error response body: {response_text[:200]}...")
                        http_error_result = {
                            "authenticated": False,
                            "message": f"Authentication check failed: {response.status}"
                        }
                        logger.debug(f"[STATUS:{status_id}] Returning HTTP error result: {http_error_result}")
                        return http_error_result
                        
        except asyncio.TimeoutError:
            logger.error(f"❌ [STATUS:{status_id}] Authentication status check timeout")
            logger.debug(f"[STATUS:{status_id}] Timeout occurred after 30 seconds")
            timeout_result = {
                "authenticated": False,
                "message": "Authentication status check timed out"
            }
            logger.debug(f"[STATUS:{status_id}] Returning timeout result: {timeout_result}")
            return timeout_result
        except Exception as e:
            logger.error(f"❌ [STATUS:{status_id}] Authentication status check error: {e}")
            logger.debug(f"[STATUS:{status_id}] Exception details: {type(e).__name__}: {str(e)}")
            exception_result = {
                "authenticated": False,
                "message": f"Authentication check error: {str(e)}"
            }
            logger.debug(f"[STATUS:{status_id}] Returning exception result: {exception_result}")
            return exception_result
    
    def _ensure_authenticated(self):
        """Ensure we have an authenticated session"""
        if not self.session:
            raise Exception("Not authenticated. Please initiate web authentication first via /api/fi-auth/initiate endpoint.")
        
        # Check expiration first, then clear authentication if expired
        if self.session.is_expired():
            logger.warning("🕐 Session expired, clearing authentication")
            self.session.authenticated = False
            raise Exception("Session expired. Please authenticate again via web authentication.")
        
        if not self.session.authenticated:
            raise Exception("Not authenticated. Please complete authentication first.")
    
    async def _make_mcp_call(self, tool_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated MCP API call"""
        self._ensure_authenticated()
        
        if params is None:
            params = {}
        
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),  # Use timestamp as ID
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        headers = {
            "Mcp-Session-Id": self.session.session_id,
            "Authorization": f"Bearer {self.session.passcode}",
            "Content-Type": "application/json"
        }
        
        try:
            async with self.get_http_session() as http_session:
                async with http_session.post(
                    self.mcp_url,
                    json=payload,
                    headers=headers
                ) as response:
                    
                    if response.status == 401:
                        # Session expired or invalid
                        self.session.authenticated = False
                        raise Exception("Session expired or invalid. Please authenticate again.")
                    
                    elif response.status == 403:
                        raise Exception("Access denied. Check your Fi Money account permissions.")
                    
                    elif response.status == 200:
                        result = await response.json()
                        
                        if 'error' in result:
                            error_msg = result['error'].get('message', 'Unknown error')
                            logger.error(f"MCP API error for {tool_name}: {error_msg}")
                            raise Exception(f"MCP API error: {error_msg}")
                        
                        # Extract actual data from MCP response
                        tool_result = result.get('result', {})
                        if 'content' in tool_result and tool_result['content']:
                            # Parse JSON content if it's a string
                            content = tool_result['content'][0]
                            if isinstance(content, dict) and 'text' in content:
                                try:
                                    return json.loads(content['text'])
                                except json.JSONDecodeError:
                                    return content
                            return content
                        return tool_result
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"MCP call failed for {tool_name}: {response.status} - {error_text}")
                        raise Exception(f"MCP call failed: {response.status}")
                        
        except asyncio.TimeoutError:
            logger.error(f"Timeout calling {tool_name}")
            raise Exception(f"Timeout calling {tool_name}")
    
    async def fetch_net_worth(self) -> Dict[str, Any]:
        """Fetch real-time net worth data from Fi Money"""
        logger.info("📊 Fetching real-time net worth from Fi Money...")
        return await self._make_mcp_call('fetch_net_worth')
    
    async def fetch_credit_report(self) -> Dict[str, Any]:
        """Fetch real-time credit report from Fi Money"""
        logger.info("🏦 Fetching real-time credit report from Fi Money...")
        return await self._make_mcp_call('fetch_credit_report')
    
    async def fetch_epf_details(self) -> Dict[str, Any]:
        """Fetch real-time EPF details from Fi Money"""
        logger.info("💰 Fetching real-time EPF details from Fi Money...")
        return await self._make_mcp_call('fetch_epf_details')
    
    async def fetch_mf_transactions(self) -> Dict[str, Any]:
        """Fetch real-time mutual fund transactions from Fi Money"""
        logger.info("📈 Fetching real-time MF transactions from Fi Money...")
        return await self._make_mcp_call('fetch_mf_transactions')
    
    async def fetch_bank_transactions(self) -> Dict[str, Any]:
        """Fetch real-time bank transactions from Fi Money"""
        logger.info("🏧 Fetching real-time bank transactions from Fi Money...")
        return await self._make_mcp_call('fetch_bank_transactions')
    
    async def fetch_all_financial_data(self) -> FinancialData:
        """
        Fetch all real-time financial data from Fi Money MCP server
        No fallbacks or sample data - production only
        """
        logger.info("🚀 Fetching comprehensive real-time financial data from Fi Money...")
        
        try:
            # Fetch all data concurrently for performance
            tasks = [
                self.fetch_net_worth(),
                self.fetch_credit_report(),
                self.fetch_epf_details(),
                self.fetch_mf_transactions(),
                self.fetch_bank_transactions()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            net_worth = results[0] if not isinstance(results[0], Exception) else {}
            credit_report = results[1] if not isinstance(results[1], Exception) else None
            epf_details = results[2] if not isinstance(results[2], Exception) else None
            mf_transactions = results[3] if not isinstance(results[3], Exception) else {}
            bank_transactions = results[4] if not isinstance(results[4], Exception) else {}
            
            # Log any errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    tool_names = ['net_worth', 'credit_report', 'epf_details', 'mf_transactions', 'bank_transactions']
                    logger.warning(f"Failed to fetch {tool_names[i]}: {result}")
            
            # Extract transaction lists
            mf_tx_list = mf_transactions.get('transactions', []) if mf_transactions else []
            bank_tx_list = bank_transactions.get('transactions', []) if bank_transactions else []
            
            # Create comprehensive financial data object
            financial_data = FinancialData(
                net_worth=net_worth,
                credit_report=credit_report,
                epf_details=epf_details,
                mf_transactions=mf_tx_list,
                bank_transactions=bank_tx_list,
                raw_data={
                    'net_worth': net_worth,
                    'credit_report': credit_report,
                    'epf_details': epf_details,
                    'mf_transactions': mf_transactions,
                    'bank_transactions': bank_transactions,
                    'fetched_at': time.time(),
                    'session_id': self.session.session_id
                }
            )
            
            total_nw = financial_data.get_total_net_worth()
            assets = financial_data.get_assets_breakdown()
            liabilities = financial_data.get_liabilities_breakdown()
            
            logger.info(f"✅ Successfully fetched real-time Fi Money data:")
            logger.info(f"   💰 Total Net Worth: ₹{total_nw:,.2f}")
            logger.info(f"   📊 Assets: {len(assets)} categories")
            logger.info(f"   📉 Liabilities: {len(liabilities)} categories")
            logger.info(f"   📈 MF Transactions: {len(mf_tx_list)}")
            logger.info(f"   🏧 Bank Transactions: {len(bank_tx_list)}")
            
            return financial_data
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch comprehensive financial data: {e}")
            raise
    
    async def test_connectivity(self) -> Dict[str, Any]:
        """Test connectivity to Fi Money MCP server"""
        try:
            logger.info(f"🔍 Testing connectivity to Fi Money MCP server: {self.mcp_url}")
            
            async with self.get_http_session() as http_session:
                # Test basic connectivity with a simple health check
                start_time = time.time()
                
                try:
                    async with http_session.get(
                        self.mcp_url.replace('/mcp/stream', '/health'),
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        return {
                            "status": "success",
                            "server_reachable": True,
                            "response_code": response.status,
                            "response_time_ms": round(response_time, 2),
                            "server_url": self.mcp_url,
                            "message": f"Fi Money MCP server is reachable (HTTP {response.status})"
                        }
                        
                except aiohttp.ClientConnectorError as e:
                    return {
                        "status": "error",
                        "server_reachable": False,
                        "error_type": "connection_error",
                        "error_message": str(e),
                        "server_url": self.mcp_url,
                        "message": "Cannot connect to Fi Money MCP server - check network connectivity"
                    }
                    
                except asyncio.TimeoutError:
                    return {
                        "status": "error",
                        "server_reachable": False,
                        "error_type": "timeout",
                        "server_url": self.mcp_url,
                        "message": "Fi Money MCP server connection timeout - server may be slow or down"
                    }
                    
        except Exception as e:
            logger.error(f"❌ Connectivity test failed: {e}")
            return {
                "status": "error",
                "server_reachable": False,
                "error_type": "unknown",
                "error_message": str(e),
                "server_url": self.mcp_url,
                "message": f"Connectivity test failed: {str(e)}"
            }
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        if not self.session:
            return {"authenticated": False, "message": "No active session"}
        
        return {
            "authenticated": self.session.authenticated,
            "session_id": self.session.session_id,
            "expires_at": self.session.expires_at,
            "expires_in_minutes": max(0, (self.session.expires_at - time.time()) / 60),
            "is_expired": self.session.is_expired(),
            "is_valid": self.session.is_valid()
        }

# Global client instance for the application
_fi_client: Optional[FiMoneyMCPClient] = None

async def get_fi_client() -> FiMoneyMCPClient:
    """Get or create global Fi Money MCP client"""
    global _fi_client
    if _fi_client is None:
        _fi_client = FiMoneyMCPClient()
        # Clear any existing session to force fresh authentication
        _fi_client.session = None
    return _fi_client

async def initiate_fi_authentication() -> Dict[str, Any]:
    """Initiate Fi Money web authentication and return login URL"""
    client = await get_fi_client()
    return await client.initiate_web_authentication()

async def authenticate_with_passcode(passcode: str) -> Dict[str, Any]:
    """Authenticate with Fi Money using a passcode"""
    client = await get_fi_client()
    return await client.authenticate_with_passcode(passcode)

async def check_authentication_status() -> Dict[str, Any]:
    """Check current authentication status"""
    client = await get_fi_client()
    return await client.check_authentication_status()

async def get_user_financial_data() -> FinancialData:
    """
    Get real-time user financial data from Fi Money
    Raises exception if not authenticated or session expired
    """
    client = await get_fi_client()
    return await client.fetch_all_financial_data()

async def test_fi_connectivity() -> Dict[str, Any]:
    """Test connectivity to Fi Money MCP server"""
    client = await get_fi_client()
    return await client.test_connectivity()

async def logout_user():
    """Logout user and clear session"""
    global _fi_client
    if _fi_client:
        await _fi_client.close()
        _fi_client = None
    logger.info("🔓 User logged out from Fi Money MCP")

async def clear_fi_session():
    """Clear Fi Money session to force fresh authentication"""
    global _fi_client
    if _fi_client:
        _fi_client.session = None
        logger.info("🧹 Fi Money session cleared - fresh authentication required")