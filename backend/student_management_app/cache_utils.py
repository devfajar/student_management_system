from django.core.cache import cache

COURSES_CACHE_KEY = "courses_list"
SUBJECTS_CACHE_KEY = "subjects_list"
SESSIONS_CACHE_KEY = "sessions_list"
FEE_STRUCTURES_CACHE_KEY = "fee_structures_list"
DASHBOARD_PREFIX = "dashboard_stats"

def get_dashboard_cache_key(user):
    role = "admin" if str(user.user_type) == '1' else ("staff" if str(user.user_type) == '2' else "student")
    return f"{DASHBOARD_PREFIX}_{role}_{user.id}"

def invalidate_dashboard_cache():
    try:
        # Clear dashboard keys or delete pattern
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(f"{DASHBOARD_PREFIX}*")
        else:
            # Fallback if standard cache backend
            cache.clear()
    except Exception:
        pass

def invalidate_courses_cache():
    try:
        cache.delete(COURSES_CACHE_KEY)
        invalidate_dashboard_cache()
    except Exception:
        pass

def invalidate_subjects_cache():
    try:
        cache.delete(SUBJECTS_CACHE_KEY)
        invalidate_dashboard_cache()
    except Exception:
        pass

def invalidate_sessions_cache():
    try:
        cache.delete(SESSIONS_CACHE_KEY)
        invalidate_dashboard_cache()
    except Exception:
        pass

def invalidate_fee_structures_cache():
    try:
        cache.delete(FEE_STRUCTURES_CACHE_KEY)
    except Exception:
        pass
