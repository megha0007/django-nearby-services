from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from rest_framework.exceptions import PermissionDenied
from .serializers import UserRegisterSerializer, ServiceSerializer, UserListSerializer
from .models import Service, User, ActivityLog
from rest_framework import status
from .permissions import IsStaffOrAdmin, IsAdminRole
from django.conf import settings


# -----------------------------
# 🔐 USER REGISTRATION
# -----------------------------
class RegisterView(APIView):

    def post(self, request):
        try:
            serializer = UserRegisterSerializer(data=request.data)

            if serializer.is_valid():
                user = serializer.save()

                data = {
                    "status": "success",
                    "error_code": 0,
                    "message": "User registered successfully",
                    "data": {
                        "email": user.email,
                        "username": user.username,
                        "role": user.role
                    }
                }
                return Response(data, status=status.HTTP_201_CREATED)

            else:
                data = {
                    "status": "error",
                    "error_code": 100,
                    "message": serializer.errors,
                    "data": ""
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            data = {
                "status": "error",
                "error_code": 101,
                "message": f"Error: {str(e)}",
                "data": ""
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUserRoleView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, pk):
        try:
            role = request.data.get("role")

            if not role:
                return Response({
                    "status": "error",
                    "error_code": 100,
                    "message": "Role field is required",
                    "data": ""
                }, status=status.HTTP_400_BAD_REQUEST)

            ALLOWED_ROLES = ["admin", "staff", "user"]

            if role not in ALLOWED_ROLES:
                return Response({
                    "status": "error",
                    "error_code": 103,
                    "message": "Invalid role",
                    "data": ""
                }, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(pk=pk).first()

            if not user:
                return Response({
                    "status": "error",
                    "error_code": 101,
                    "message": "User not found",
                    "data": ""
                }, status=status.HTTP_404_NOT_FOUND)

            user.role = role
            user.save()
            ActivityLog.objects.create(
                    performed_by=request.user,
                    target_user=user,
                    action="create_user",
                    details={"email": user.email}
                )


            return Response({
                "status": "success",
                "error_code": 0,
                "message": "Role updated successfully",
                "data": {
                    "user_id": user.id,
                    "email": user.email,
                    "role": user.role
                }
            })

        except Exception as e:
            return Response({
                "status": "error",
                "error_code": 102,
                "message": f"Error: {str(e)}",
                "data": ""
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# -----------------------------
# 🛠 CREATE USER (Admin Only)
# -----------------------------
class AdminCreateUserView(APIView):
    permission_classes = [IsAdminRole]
    
    def permission_denied(self, request, message=None, **kwargs):
        # Accept extra kwargs like `code` to avoid TypeError
        response_data = {
            "status": "error",
            "error_code": 403,
            "method": request.method,
            "message": message or "You do not have permission to perform this action.",
            "data": ""
        }
        raise PermissionDenied(detail=response_data)

    def post(self, request):
        try:
            serializer = UserRegisterSerializer(data=request.data)

            if serializer.is_valid():
                user = serializer.save()
                ActivityLog.objects.create(
                    performed_by=request.user,
                    target_user=user,
                    action="create_user",
                    details={"email": user.email}
                )

                return Response({
                    "status": "success",
                    "error_code": 0,
                    "message": "User created successfully by admin",
                    "data": {
                        "user_id": user.id,
                        "email": user.email,
                        "role": user.role
                    }
                }, status=status.HTTP_201_CREATED)

            return Response({
                "status": "error",
                "error_code": 100,
                "message": serializer.errors,
                "data": ""
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": "error",
                "error_code": 101,
                "message": f"Error: {str(e)}",
                "data": ""
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# -----------------------------
# 🛠 DISABLE USER (Admin Only)
# -----------------------------           
            
class ToggleUserStatusView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, pk):
        try:
            user = User.objects.filter(pk=pk).first()

            if not user:
                return Response({
                    "status": "error",
                    "error_code": 101,
                    "message": "User not found",
                    "data": ""
                }, status=status.HTTP_404_NOT_FOUND)

            # Get desired status from request data
            is_active = request.data.get("is_active")

            if isinstance(is_active, str):
                is_active = is_active.lower() == "true"

            user.is_active = is_active
            user.save()

            if is_active is None:
                return Response({
                    "status": "error",
                    "error_code": 103,
                    "message": "Missing 'is_active' field in request",
                    "data": ""
                }, status=status.HTTP_400_BAD_REQUEST)

            # Update user status
            user.is_active = bool(is_active)
            user.save()
            print("11111111111111",user.is_active)
            ActivityLog.objects.create(
                    performed_by=request.user,
                    target_user=user,
                    action="toggle_status",
                    details={"email": user.email, "is_active": user.is_active}
                )


            action = "enabled" if user.is_active else "disabled"

            return Response({
                "status": "success",
                "error_code": 0,
                "message": f"User {action} successfully",
                "data": ""
            })

        except Exception as e:
            return Response({
                "status": "error",
                "error_code": 102,
                "message": f"Error: {str(e)}",
                "data": ""
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    def permission_denied(self, request, message=None, **kwargs):
        # Accept extra kwargs like `code` to avoid TypeError
        response_data = {
            "status": "error",
            "error_code": 403,
            "method": request.method,
            "message":  message or "You do not have permission to perform this action.",
            "data": ""
        }
        raise PermissionDenied(detail=response_data)

    def get(self, request, id=None):
        try:
            # Fetch a single user if ID is provided
            if id is not None and id != '':
                user_obj = User.objects.filter(id=id).first()
                if user_obj:
                    serializer = UserListSerializer(user_obj)
                    data = {
                        "status": "success",
                        "error_code": 0,
                        "method": request.method,
                        "message": _("User fetched successfully"),
                        "data": serializer.data
                    }
                else:
                    data = {
                        "status": "success",
                        "error_code": 100,
                        "method": request.method,
                        "message": "User not found",
                        "data": ""
                    }
                return Response(data, status=status.HTTP_200_OK)

            # Fetch all users if no ID
            users = User.objects.all().order_by("-date_joined")
            serializer = UserListSerializer(users, many=True)
            data = {
                "status": "success",
                "error_code": 0,
                "method": request.method,
                "message": "Users fetched successfully",
                "data": serializer.data
            }
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            
            data = {
                "status": "error",
                "error_code": 101,
                "message": f"Error: {str(e)}",
                "data": ""
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

       
# -----------------------------
# 🛠 CREATE SERVICE (Admin Only)
# -----------------------------
class ServiceCreateView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def post(self, request):
        try:
            serializer = ServiceSerializer(data=request.data)

            if serializer.is_valid():
                service = serializer.save(created_by=request.user)

                # Clear related cache
                cache.delete_pattern("nearby:*")
                cache.delete_pattern("service_detail:*")

                data = {
                    "status": "success",
                    "error_code": 0,
                    "message": "Service created successfully",
                    "data": serializer.data
                }
                return Response(data, status=status.HTTP_201_CREATED)

            else:
                data = {
                    "status": "error",
                    "error_code": 100,
                    "message": serializer.errors,
                    "data": ""
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            data = {
                "status": "error",
                "error_code": 101,
                "message": f"Error: {str(e)}",
                "data": ""
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# -----------------------------
# 📋 LIST ALL SERVICES
# -----------------------------
class ServiceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            services = Service.objects.all()
            serializer = ServiceSerializer(services, many=True)

            data = {
                "status": "success",
                "error_code": 0,
                "message": "Service list fetched successfully",
                "data": serializer.data
            }
            return Response(data)

        except Exception as e:
            data = {
                "status": "error",
                "error_code": 101,
                "message": f"Error: {str(e)}",
                "data": ""
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# -----------------------------
# 📄 SERVICE DETAIL (Cached)
# -----------------------------
class ServiceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        try:
            if not pk:
                return Response({
                    "status": "error",
                    "error_code": 102,
                    "message": "Service ID is required",
                    "data": ""
                })

            cache_key = f"service_detail:{pk}"
            cached_data = cache.get(cache_key)

            if cached_data:
                return Response({
                    "status": "success",
                    "error_code": 0,
                    "message": "Service fetched successfully (cached)",
                    "data": cached_data
                })

            service = Service.objects.filter(id=pk).first()

            if not service:
                return Response({
                    "status": "error",
                    "error_code": 100,
                    "message": "Service not found",
                    "data": ""
                })

            serializer = ServiceSerializer(service)

            cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL)

            return Response({
                "status": "success",
                "error_code": 0,
                "message": "Service fetched successfully",
                "data": serializer.data
            })

        except Exception as e:
            return Response({
                "status": "error",
                "error_code": 101,
                "message": f"Error: {str(e)}",
                "data": ""
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -----------------------------
# ✏ UPDATE SERVICE (Admin Only)
# -----------------------------
class ServiceUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrAdmin]

    def put(self, request, pk=None):
        try:
            service = Service.objects.filter(id=pk).first()

            if not service:
                return Response({
                    "status": "error",
                    "error_code": 100,
                    "message": "Service not found",
                    "data": ""
                })

            serializer = ServiceSerializer(service, data=request.data)

            if serializer.is_valid():
                serializer.save()

                cache.delete(f"service_detail:{pk}")
                cache.delete_pattern("nearby:*")

                return Response({
                    "status": "success",
                    "error_code": 0,
                    "message": "Service updated successfully",
                    "data": serializer.data
                })

            else:
                return Response({
                    "status": "error",
                    "error_code": 100,
                    "message": serializer.errors,
                    "data": ""
                })

        except Exception as e:
            return Response({
                "status": "error",
                "error_code": 101,
                "message": f"Error: {str(e)}",
                "data": ""
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# -----------------------------
# ❌ DELETE SERVICE (Admin Only)
# -----------------------------
class ServiceDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def delete(self, request, pk=None):
        try:
            service = Service.objects.filter(id=pk).first()

            if not service:
                return Response({
                    "status": "error",
                    "error_code": 100,
                    "message": "Service not found",
                    "data": ""
                })

            service.delete()

            cache.delete(f"service_detail:{pk}")
            cache.delete_pattern("nearby:*")

            return Response({
                "status": "success",
                "error_code": 0,
                "message": "Service deleted successfully",
                "data": ""
            })

        except Exception as e:
            return Response({
                "status": "error",
                "error_code": 101,
                "message": f"Error: {str(e)}",
                "data": ""
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# -----------------------------
# 📍 NEARBY SEARCH (Cached GIS Query)
# -----------------------------
class NearbyServiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            lat = request.GET.get("latitude")
            lng = request.GET.get("longitude")
            radius = request.GET.get("radius", 5)
            category = request.GET.get("category", "")

            # Validate required params
            if not lat or not lng:
                data = {
                    "status": "error",
                    "error_code": 102,
                    "message": "latitude and longitude are required",
                    "data": ""
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            try:
                lat = float(lat)
                lng = float(lng)
                radius = float(radius)
            except ValueError:
                data = {
                    "status": "error",
                    "error_code": 102,
                    "message": "Invalid latitude, longitude or radius",
                    "data": ""
                }
                return Response(data, status=status.HTTP_400_BAD_REQUEST)

            cache_key = f"nearby:{lat}:{lng}:{radius}:{category}"

            cached_data = cache.get(cache_key)
            if cached_data:
                data = {
                    "status": "success",
                    "error_code": 0,
                    "message": "Nearby services fetched successfully (cached)",
                    "data": cached_data
                }
                return Response(data)

            user_location = Point(lng, lat, srid=4326)

            services = Service.objects.annotate(
                distance=Distance("location", user_location)
            ).filter(
                location__distance_lte=(user_location, D(km=radius))
            )

            if category:
                services = services.filter(category=category)

            services = services.order_by("distance")

            serializer = ServiceSerializer(services, many=True)

            cache.set(cache_key, serializer.data, timeout=settings.CACHE_TTL)

            data = {
                "status": "success",
                "error_code": 0,
                "message": "Nearby services fetched successfully",
                "data": serializer.data
            }

            return Response(data)

        except Exception as e:
            data = {
                "status": "error",
                "error_code": 101,
                "message": f"Error: {str(e)}",
                "data": ""
            }
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActivityLogListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        try:
            logs = ActivityLog.objects.select_related("performed_by", "target_user").all()
            
            data = []
            for log in logs:
                data.append({
                    "id": log.id,
                    "action": log.action,
                    "performed_by": {
                        "id": log.performed_by.id,
                        "email": log.performed_by.email,
                        "role": log.performed_by.role
                    },
                    "target_user": {
                        "id": log.target_user.id if log.target_user else None,
                        "email": log.target_user.email if log.target_user else None,
                        "role": log.target_user.role if log.target_user else None
                    },
                    "timestamp": log.timestamp,
                    "details": log.details
                })

            return Response({
                "status": "success",
                "error_code": 0,
                "message": "Activity logs fetched successfully",
                "data": data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "error_code": 101,
                "message": f"Error: {str(e)}",
                "data": ""
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)