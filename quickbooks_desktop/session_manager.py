"""
QuickBooks Desktop Session Manager
Wraps the QB SDK connection lifecycle for Python.
"""
import sys
# CRITICAL: Set COM threading model BEFORE importing pythoncom
# 0 = COINIT_MULTITHREADED (required for Flask/web apps)
if not hasattr(sys, 'coinit_flags'):
    sys.coinit_flags = 0
import pythoncom


class SessionManager:
    """
    Manages connection and session lifecycle with QuickBooks Desktop.
    
    Usage:
        qb = SessionManager()
        qb.open_connection()
        qb.begin_session()
        response = qb.send_request(xml_request)
        qb.close_qb()
    """
    
    def __init__(self, application_name="UniversalCellularInvoiceAutomation"):
        """
        Initialize the QB connection manager.
        
        Args:
            application_name: Name that appears in QB authorization dialog
        """
        self.application_name = application_name
        self.qbXMLRP = None
        self.ticket = None
        self.connection_open = False
        self.session_begun = False
        self.com_initialized = False
        
    def open_connection(self):
        """
        Open connection to QuickBooks.
        
        Raises:
            Exception: If connection fails or QB is not running
        """
        if self.connection_open:
            return
        
        try:
            import win32com.client
            # Try to initialize COM - may already be initialized by caller (e.g., create_qb_invoice)
            try:
                pythoncom.CoInitialize()
                self.com_initialized = True
            except Exception:
                # COM already initialized in this thread, that's fine
                self.com_initialized = False
            self.qbXMLRP = win32com.client.Dispatch("QBXMLRP2.RequestProcessor")
            self.qbXMLRP.OpenConnection("", self.application_name)
            self.connection_open = True
        except Exception as e:
            raise Exception(f"Failed to connect to QuickBooks: {str(e)}. Is QuickBooks running?")
        
    def begin_session(self, qb_file_path="", mode=0):
        """
        Begin a session with a QuickBooks company file.
        
        Args:
            qb_file_path: Path to .qbw file (empty string = currently open file)
            mode: 0 = Do Not Care, 1 = Single User, 2 = Multi-User
            
        Raises:
            Exception: If session cannot be started
        """
        if not self.connection_open:
            raise Exception("Must open connection before beginning session")
            
        if self.session_begun:
            return
        
        try:
            self.ticket = self.qbXMLRP.BeginSession(qb_file_path, mode)
            self.session_begun = True
        except Exception as e:
            raise Exception(f"Failed to begin session: {str(e)}. Is a company file open in QuickBooks?")
        
    def send_request(self, xml_request):
        """
        Send qbXML request and return response.
        
        Args:
            xml_request: Full qbXML request string
            
        Returns:
            XML response string from QuickBooks
            
        Raises:
            Exception: If request fails
        """
        if not self.session_begun:
            raise Exception("Must begin session before sending requests")
        
        try:
            return self.qbXMLRP.ProcessRequest(self.ticket, xml_request)
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
        
    def end_session(self):
        """End the QB session."""
        if self.session_begun:
            try:
                self.qbXMLRP.EndSession(self.ticket)
            except:
                pass  # Ignore errors on cleanup
            self.session_begun = False
            self.ticket = None
            
    def close_connection(self):
        """Close the connection to QuickBooks."""
        if self.session_begun:
            self.end_session()
            
        if self.connection_open:
            try:
                self.qbXMLRP.CloseConnection()
            except:
                pass  # Ignore errors on cleanup
            self.connection_open = False
        
        # Only uninitialize COM if WE initialized it (not the caller)
        if self.com_initialized:
            try:
                pythoncom.CoUninitialize()
            except:
                pass  # Ignore errors on cleanup
            self.com_initialized = False
            
    def close_qb(self):
        """Alias for close_connection (for backward compatibility)."""
        self.close_connection()
        
    def __enter__(self):
        """Context manager entry."""
        self.open_connection()
        self.begin_session()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_qb()
        return False
