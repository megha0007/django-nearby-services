from rest_framework.throttling import SimpleRateThrottle


class RoleBasedUserThrottle(SimpleRateThrottle):
    scope = "role_based"

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        return f"throttle_user_{request.user.id}"

    def allow_request(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True  # handled by AnonRateThrottle

        # Dynamically assign rate
        if request.user.role in ["admin", "staff"]:
            self.rate = "500/min"
        else:
            self.rate = "200/min"

        self.num_requests, self.duration = self.parse_rate(self.rate)

        return super().allow_request(request, view)
