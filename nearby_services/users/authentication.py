# users/authentication.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed

class CachedJWTAuthentication(JWTAuthentication):

    def get_validated_token(self, raw_token):
        cache_key = f"auth_token:{raw_token}"

        # Check Redis first
        validated_token = cache.get(cache_key)
        if validated_token:
            return validated_token

        # If not cached → validate normally
        validated_token = super().get_validated_token(raw_token)

        # Store in Redis (short TTL)
        cache.set(cache_key, validated_token, timeout=300)

        return validated_token
