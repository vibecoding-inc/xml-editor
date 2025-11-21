# Generated resource file
import os

def qInitResources():
    """Initialize resources."""
    pass

def qCleanupResources():
    """Cleanup resources."""
    pass

def getResourcePath(name):
    """Get the path to a resource file."""
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, name.lstrip('/'))
