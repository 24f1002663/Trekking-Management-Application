from flask_caching import Cache

# Shared cache instance (Redis-backed). Kept in its own module so both
# app.py and the route blueprints can import it without a circular import,
# mirroring the mail_service.py pattern.
cache = Cache()
