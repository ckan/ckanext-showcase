import functools

def notify_after_action(notification_func):
    """
    A decorator that calls a notification function after the main action completes.

    :param notification_func: The notification function to call after the action.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute the original function and capture the result
            result = func(*args, **kwargs)
            
            # Extract the request id (assuming it's in the result)
            showcase_id = result.get('id') if result else None
            
            # Call the notification function if a valid request id is found
            if showcase_id:
                notification_func(showcase_id)
            
            # Return the original result
            return result
        
        return wrapper
    return decorator