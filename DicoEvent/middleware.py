import time
import json
from loguru import logger
from django.utils.deprecation import MiddlewareMixin


class LoggingMiddleware(MiddlewareMixin):
    """Middleware to log all HTTP requests and responses."""
    
    def process_request(self, request):
        """Log incoming requests."""
        request.start_time = time.time()
        
        # Extract request information
        user = getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') else 'anonymous'
        method = request.method
        path = request.get_full_path()
        remote_addr = self.get_client_ip(request)
        
        # Log request body for POST/PUT/PATCH requests (excluding sensitive data)
        request_body = ""
        if method in ['POST', 'PUT', 'PATCH']:
            try:
                if hasattr(request, 'body') and request.body:
                    # Try to parse JSON
                    try:
                        body_data = json.loads(request.body.decode('utf-8'))
                        # Remove sensitive fields
                        sensitive_fields = ['password', 'token', 'secret', 'key']
                        filtered_body = {k: '***' if any(field in k.lower() for field in sensitive_fields) else v 
                                       for k, v in body_data.items()}
                        request_body = f" - Body: {json.dumps(filtered_body, default=str)}"
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        request_body = f" - Body: [Binary/Non-JSON data, size: {len(request.body)} bytes]"
            except Exception:
                request_body = " - Body: [Could not parse]"
        
        logger.info(f"→ {method} {path} - User: {user} - IP: {remote_addr}{request_body}")
        
    def process_response(self, request, response):
        """Log outgoing responses."""
        if not hasattr(request, 'start_time'):
            return response
            
        # Calculate response time
        response_time = (time.time() - request.start_time) * 1000  # in milliseconds
        
        # Extract response information
        user = getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') else 'anonymous'
        method = request.method
        path = request.get_full_path()
        status_code = response.status_code
        remote_addr = self.get_client_ip(request)
        
        # Log response
        log_level = self.get_log_level_for_status(status_code)
        logger.log(log_level, f"← {method} {path} - User: {user} - IP: {remote_addr} - Status: {status_code} - Time: {response_time:.2f}ms")
        
        return response
        
    def process_exception(self, request, exception):
        """Log exceptions."""
        user = getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') else 'anonymous'
        method = request.method
        path = request.get_full_path()
        remote_addr = self.get_client_ip(request)
        
        logger.error(f"✗ {method} {path} - User: {user} - IP: {remote_addr} - Exception: {str(exception)}")
        
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
        
    def get_log_level_for_status(self, status_code):
        """Get appropriate log level based on HTTP status code."""
        if status_code >= 500:
            return "ERROR"
        elif status_code >= 400:
            return "WARNING"
        elif status_code >= 300:
            return "INFO"
        else:
            return "INFO"