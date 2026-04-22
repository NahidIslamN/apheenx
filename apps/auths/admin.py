from django.contrib import admin

from apps.auths.models import CustomUser, OtpTable


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
	"""Admin registration for CustomUser with search fields to support autocomplete."""

	search_fields = ("email", "username", "full_name")
	list_display = ("email", "username", "is_active", "is_staff")
	ordering = ("-date_joined",)


admin.site.register(OtpTable)
