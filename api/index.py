"""
Vercel serverless function entry point
"""
from sessions import handler as sessions_handler

def handler(request):
    """Main handler that routes to appropriate function"""
    return sessions_handler(request)

# Export for Vercel
app = handler
