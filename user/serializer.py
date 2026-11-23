from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from kalashwet_backend.setting.serializer import MongoModelSerializer
from .models import Role, RolePermission, User, Address
from .rbac import module_tables, permission_matrix



class RoleSerializer(MongoModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class RolePermissionSerializer(MongoModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), pk_field=serializers.CharField(),)
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    class Meta:
        model = RolePermission
        fields = "__all__"

    def validate(self, attrs):
        role = attrs.get('role') or (self.instance.role if self.instance else None)
        module = attrs.get('module') or (self.instance.module if self.instance else '')
        submodule = attrs.get('submodule', self.instance.submodule if self.instance else '')

        if submodule:
            known = module_tables(module)
            if submodule not in known:
                raise serializers.ValidationError({'submodule': (
                    f'{submodule!r} is not a table in {module!r}. '
                    f'Valid: {", ".join(known) or "(none)"}'
                )})

        # Surface the (role, module, submodule) unique constraint as a clean 400.
        existing = RolePermission.objects.filter(role=role, module=module, submodule=submodule)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            target = f'{module}.{submodule}' if submodule else module
            raise serializers.ValidationError(f'{role} already has a permission row for {target!r}.')
        return attrs


class UserSerializer(MongoModelSerializer):
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(),pk_field=serializers.CharField(),required=False,allow_null=True,write_only=True,)
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role', 'token', 'created_at', 'updated_at']
        extra_kwargs = {'password': {'write_only': True}}

    def get_token(self, obj):
        request = self.context.get('request')
        if request is None or request.method != 'POST':
            return None
        return str(RefreshToken.for_user(obj).access_token)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=['password'])
        return user


class UseDetailSerializer(MongoModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = User
        exclude = ['password']


class MeSerializer(MongoModelSerializer):
    """The signed-in user's own identity and rights, for /v1/me/."""
    role = RoleSerializer(read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'name', 'email', 'phone', 'is_active', 'is_staff', 'is_superuser', 'role', 'permissions']

    def get_permissions(self, obj):
        return permission_matrix(obj)


class AddressSerializer(MongoModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'full_name', 'phone', 'line1', 'line2', 'city', 'state', 'pincode', 'is_default']


class CustomerRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    email = serializers.EmailField(required=False, allow_blank=True, default='')
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default='')
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        email = attrs.get('email', '').strip()
        phone = attrs.get('phone', '').strip()
        if not email and not phone:
            raise serializers.ValidationError('Either email or phone is required.')
        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'A user with this email already exists.'})
        if phone and User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError({'phone': 'A user with this phone number already exists.'})
        return attrs

