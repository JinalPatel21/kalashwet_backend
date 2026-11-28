from datetime import timedelta
import secrets
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from kalashwet_backend.setting.filters import filterable_fields, searchable_fields
from kalashwet_backend.setting.mixins import StatusMessageUpdateMixin
from kalashwet_backend.setting.permissions import HasModulePermission
from .choice import PermissionModule
from .models import Address, OtpCode, User
from .serializer import *


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """POST /v1/auth/login/, rate limited.

    Nothing else stands between a guessed password and an account: there is
    no lockout, and ACCESS_TOKEN_LIFETIME is seven days, so one success buys
    a week. The scope's rate lives in DEFAULT_THROTTLE_RATES.
    """
    throttle_scope = 'login'


class ThrottledTokenRefreshView(TokenRefreshView):
    """Refresh is the same target by another door - a stolen refresh token is
    valid for its full lifetime, since BLACKLIST_AFTER_ROTATION is off."""
    throttle_scope = 'login'


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /v1/me/ - read or update the signed-in user's own profile.

    Deliberately IsAuthenticated rather than HasModulePermission: reading
    your own rights cannot itself require a right. Gating this on the `user`
    module would mean a sales executive - who has no business administering
    accounts - could not load the panel at all.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MeSerializer
    filter_backends = []

    def get_serializer(self, *args, **kwargs):
        # Profile edits are partial so a customer can update one field at a time.
        if self.request.method == 'PATCH':
            kwargs.setdefault('partial', True)
        return super().get_serializer(*args, **kwargs)

    def get_object(self):
        return self.request.user

#
# class PermissionModuleListView(APIView):
#     """GET /v1/permission-modules/ - the modules and the tables inside each,
#     so the role-editor screen can draw its checkbox grid from the live app
#     registry instead of a hardcoded list that silently goes stale whenever a
#     model is added."""
#     permission_classes = [HasModulePermission]
#     permission_submodule = ''
#
#     def get(self, request):
#         return Response({
#             'modules': [
#                 {'module': module, 'tables': module_tables(module), 'actions': list(ACTIONS)}
#                 for module in PermissionModule.values
#             ],
#         })


class RoleListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasModulePermission]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    filterset_fields = filterable_fields(Role)
    search_fields = searchable_fields(Role)


class RoleDetailView(StatusMessageUpdateMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasModulePermission]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class RolePermissionListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasModulePermission]
    queryset = RolePermission.objects.select_related('role').order_by('role_id', 'module')
    serializer_class = RolePermissionSerializer
    filterset_fields = filterable_fields(RolePermission)
    search_fields = searchable_fields(RolePermission)


class RolePermissionDetailView(StatusMessageUpdateMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasModulePermission]
    queryset = RolePermission.objects.select_related('role')
    serializer_class = RolePermissionSerializer


class RolePermissionBulkSetView(APIView):
    """PUT /v1/roles/<pk>/permissions/ - replace a role's entire permission
    set in one call instead of the editor firing one POST/PATCH/DELETE per
    row it touched. The payload is the complete grid: rows given are
    upserted, rows left out are deleted - there's no partial-save mode, so
    the panel always sends every row it's showing, checked or not.

    Every row is validated before any of them are written, so one bad row
    can't leave the role half-updated. Mongo here runs standalone (no
    replica set), so this isn't wrapped in a real multi-document
    transaction - a write failing partway through the second loop is a
    known, accepted gap, not a covered case.
    """
    permission_classes = [HasModulePermission]
    permission_submodule = 'rolepermission'

    def put(self, request, pk):
        role = generics.get_object_or_404(Role, pk=pk)
        rows = request.data if isinstance(request.data, list) else request.data.get('permissions')
        if not isinstance(rows, list):
            return Response({'detail': "Expected a JSON array of permission rows (or {'permissions': [...]})."}, status=400)

        existing_by_key = {
            (row.module, row.submodule or ''): row
            for row in RolePermission.objects.filter(role=role)
        }

        prepared = []
        seen = set()
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                return Response({'index': index, 'detail': 'Each row must be an object.'}, status=400)
            module = row.get('module')
            submodule = row.get('submodule') or ''
            key = (module, submodule)
            if key in seen:
                return Response({'index': index, 'detail': f'Duplicate row for module={module!r}, submodule={submodule!r}.'}, status=400)
            seen.add(key)

            instance = existing_by_key.get(key)
            data = {**row, 'submodule': submodule, 'role': str(role.pk)}
            serializer = RolePermissionSerializer(instance=instance, data=data)
            if not serializer.is_valid():
                return Response({'index': index, 'errors': serializer.errors}, status=400)
            prepared.append((instance, serializer.validated_data))

        drop_ids = [row.pk for key, row in existing_by_key.items() if key not in seen]
        if drop_ids:
            RolePermission.objects.filter(pk__in=drop_ids).delete()

        results = []
        for instance, validated in prepared:
            if instance is None:
                results.append(RolePermission.objects.create(**validated))
                continue
            for attr, value in validated.items():
                if attr != 'role':
                    setattr(instance, attr, value)
            instance.save()
            results.append(instance)

        for row in results:
            row.role = role
        return Response(RolePermissionSerializer(results, many=True).data)


class UserListView(generics.ListAPIView):
    permission_classes = [HasModulePermission]
    queryset = User.objects.all()
    serializer_class = UseDetailSerializer
    filterset_fields = filterable_fields(User, exclude=['password'])
    search_fields = searchable_fields(User, exclude=['password'])


class UserCreateView(generics.CreateAPIView):
    permission_classes = [HasModulePermission]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class StaffAccountCreateView(APIView):
    """POST /v1/staff-users/ - create a central-auth staff login."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'detail': 'Only a central superuser can create staff accounts.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = StaffAccountCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'id': str(user.pk),
            'first_name': user.first_name,
            'last_name': user.last_name,
            'name': user.name,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
        }, status=status.HTTP_201_CREATED)


class UserDetailView(StatusMessageUpdateMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasModulePermission]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CustomerLoginView(APIView):
    """POST /v1/auth/login/ - accepts username (email or phone) and password."""
    permission_classes = [AllowAny]
    throttle_scope = 'login'

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response({'detail': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email__iexact=username).first() or User.objects.filter(phone=username).first()
        if not user or not user.check_password(password):
            return Response({'detail': 'Invalid email/mobile or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'detail': 'This account has been deactivated.'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class CustomerRegisterView(APIView):
    """POST /v1/auth/register/ - registers a customer account."""
    permission_classes = [AllowAny]
    serializer_class = CustomerRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        email = data.get('email', '').strip() or None
        phone = data.get('phone', '').strip() or None
        name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()

        user = User.objects.create_user(
            email=email,
            phone=phone,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            name=name,
            password=data.get('password'),
        )
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class SendOtpView(APIView):
    """POST /v1/auth/otp/send/ - sends OTP to mobile number."""
    permission_classes = [AllowAny]
    throttle_scope = 'login'

    def post(self, request):
        phone = request.data.get('phone', '').strip()
        if not phone or len(phone) < 10:
            return Response({'phone': ['Enter a valid 10-digit mobile number.']}, status=status.HTTP_400_BAD_REQUEST)

        # Never use a fixed OTP: anyone who knows it could take over an account.
        # Deliver this code through the configured SMS gateway before enabling
        # OTP login in production.
        from django.conf import settings
        if not settings.DEBUG:
            return Response({'detail': 'OTP sign-in is not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        otp = f'{secrets.randbelow(1_000_000):06d}'
        expires_at = timezone.now() + timedelta(minutes=10)
        OtpCode.objects.create(phone=phone, otp=otp, expires_at=expires_at)

        payload = {'detail': f'OTP sent to +91 {phone[-10:]}.'}
        if settings.DEBUG:
            payload['detail'] += f' Development OTP: {otp}'
        return Response(payload)


class VerifyOtpView(APIView):
    """POST /v1/auth/otp/verify/ - verifies OTP, auto-creates customer if new."""
    permission_classes = [AllowAny]
    throttle_scope = 'login'

    def post(self, request):
        phone = request.data.get('phone', '').strip()
        otp = request.data.get('otp', '').strip()

        if not phone or not otp:
            return Response({'detail': 'Phone and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        code = OtpCode.objects.filter(phone=phone, otp=otp, is_verified=False).order_by('-created_at').first()
        valid = bool(code and not code.is_expired())
        if valid:
            code.is_verified = True
            code.save(update_fields=['is_verified', 'updated_at'])

        if not valid:
            return Response({'detail': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(phone=phone).first()
        if not user:
            user = User.objects.create_user(phone=phone, name=f'Customer {phone[-4:]}')
        elif not user.is_active:
            return Response({'detail': 'This account has been deactivated.'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class AddressListCreateView(generics.ListCreateAPIView):
    """GET/POST /v1/addresses/ - customer saved delivery addresses."""
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer
    pagination_class = None

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-is_default', '-created_at')

    def perform_create(self, serializer):
        if serializer.validated_data.get('is_default'):
            Address.objects.filter(user=self.request.user).update(is_default=False)
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """PUT /v1/addresses/<id>/ - update or delete a customer address."""
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.validated_data.get('is_default'):
            Address.objects.filter(user=self.request.user).exclude(pk=self.get_object().pk).update(is_default=False)
        serializer.save()
