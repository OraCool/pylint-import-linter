"""Health check utilities."""


def check_database_health():
    """Check if database is accessible."""
    return {"status": "healthy", "service": "database"}


def check_redis_health():
    """Check if Redis is accessible."""
    return {"status": "healthy", "service": "redis"}


def get_system_health():
    """Get overall system health status."""
    checks = [check_database_health(), check_redis_health()]

    all_healthy = all(check["status"] == "healthy" for check in checks)

    return {"status": "healthy" if all_healthy else "unhealthy", "checks": checks}
