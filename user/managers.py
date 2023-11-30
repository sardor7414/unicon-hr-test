from django.contrib.auth.base_user import BaseUserManager
from django.contrib import auth


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, first_name, last_name, phone, password, username=None, **extra_fields):
        if not first_name:
            raise ValueError("The given first_name must be set")
        if not last_name:
            raise ValueError("The given last_name must be set")
        if not phone:
            raise ValueError("The given phone must be set")
        user = self.model(
            first_name=first_name, last_name=last_name, phone=phone,
            password=password, username=username, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, phone, password, username=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(first_name, last_name, phone, password, username, **extra_fields)

    def with_perm(
            self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the backend argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()
