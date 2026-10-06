from django.contrib import admin

from django.urls import (
    include,
    path,
)

from django.conf import settings

from django.conf.urls.static import static


urlpatterns = [

    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "api/",
        include("inspection.urls"),
    ),

]


# ============================================================
# LOCAL DEVELOPMENT FILE SERVING
# ============================================================

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

    urlpatterns += static(
        settings.DEMO_VIDEO_URL,
        document_root=settings.DEMO_VIDEO_ROOT,
    )