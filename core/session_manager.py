"""
Session Manager - Handle session persistence and management
"""

import json
import pickle
import logging
import threading
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.sessions = {}
        self.lock = threading.Lock()
        self.session_file = self.config.get('session_file', 'sessions.json')
        
        # Load existing sessions
        self._load_sessions()
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """
        Save session data
        
        Args:
            session_id: Unique session identifier
            session_data: Session data to save
            
        Returns:
            bool: True if successful
        """
        try:
            with self.lock:
                self.sessions[session_id] = {
                    'data': session_data,
                    'created_at': datetime.now().isoformat(),
                    'last_accessed': datetime.now().isoformat(),
                    'expires_at': self._calculate_expiry()
                }
                
                return self._save_sessions()
                
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            dict: Session data or None if not found/expired
        """
        try:
            with self.lock:
                if session_id not in self.sessions:
                    return None
                
                session = self.sessions[session_id]
                
                # Check if session is expired
                if self._is_expired(session):
                    logger.info(f"Session {session_id} has expired")
                    self.delete_session(session_id)
                    return None
                
                # Update last accessed time
                session['last_accessed'] = datetime.now().isoformat()
                self._save_sessions()
                
                return session['data']
                
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if successful
        """
        try:
            with self.lock:
                if session_id in self.sessions:
                    del self.sessions[session_id]
                    return self._save_sessions()
                return True
                
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False
    
    def list_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all available sessions
        
        Returns:
            dict: Session information
        """
        with self.lock:
            session_info = {}
            for session_id, session in self.sessions.items():
                session_info[session_id] = {
                    'created_at': session['created_at'],
                    'last_accessed': session['last_accessed'],
                    'expires_at': session['expires_at'],
                    'is_expired': self._is_expired(session)
                }
            return session_info
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions
        
        Returns:
            int: Number of sessions cleaned up
        """
        try:
            with self.lock:
                expired_sessions = []
                
                for session_id, session in self.sessions.items():
                    if self._is_expired(session):
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.sessions[session_id]
                
                if expired_sessions:
                    self._save_sessions()
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
                return len(expired_sessions)
                
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0
    
    def _calculate_expiry(self) -> str:
        """Calculate session expiry time"""
        session_timeout = self.config.get('login', {}).get('session_timeout', 3600)
        expiry = datetime.now() + timedelta(seconds=session_timeout)
        return expiry.isoformat()
    
    def _is_expired(self, session: Dict[str, Any]) -> bool:
        """Check if session is expired"""
        try:
            expires_at = datetime.fromisoformat(session['expires_at'])
            return datetime.now() > expires_at
        except:
            return True
    
    def _load_sessions(self):
        """Load sessions from file"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
                logger.info(f"Loaded {len(self.sessions)} sessions from {self.session_file}")
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            self.sessions = {}
    
    def _save_sessions(self) -> bool:
        """Save sessions to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.session_file) if os.path.dirname(self.session_file) else '.', 
                       exist_ok=True)
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")
            return False
    
    def export_session(self, session_id: str, export_file: str) -> bool:
        """
        Export session to file
        
        Args:
            session_id: Session identifier
            export_file: File path to export to
            
        Returns:
            bool: True if successful
        """
        try:
            session_data = self.load_session(session_id)
            if not session_data:
                return False
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported session {session_id} to {export_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting session {session_id}: {e}")
            return False
    
    def import_session(self, import_file: str, session_id: str = None) -> Optional[str]:
        """
        Import session from file
        
        Args:
            import_file: File path to import from
            session_id: Optional session identifier (generated if not provided)
            
        Returns:
            str: Session identifier or None if failed
        """
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            if not session_id:
                session_id = f"imported_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            if self.save_session(session_id, session_data):
                logger.info(f"Imported session to {session_id} from {import_file}")
                return session_id
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error importing session from {import_file}: {e}")
            return None
