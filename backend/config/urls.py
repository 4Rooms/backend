"""
URL configuration for djangochat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from pathlib import Path

from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from backend.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("login.urls")),
    path("api/", include("registration.urls")),
    path("api/", include("chat.urls")),
    path("api/", include("accounts.urls")),
    path("oauth/", include("social_django.urls", namespace="social")),
    # swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def get_file_name(request_file_name: str) -> str:
    """Return the content of the file"""

    allowed_files = ["login_example.html", "chat_example.html"]
    examples_dir = BASE_DIR / "tests"

    try:
        return examples_dir / allowed_files[allowed_files.index(request_file_name)]
    except ValueError:
        return examples_dir / "login_example.html"


# for react router
urlpatterns += [
    re_path(
        r"^(?P<file_name>.*)/?$",
        lambda request, file_name: HttpResponse(open(get_file_name(file_name), "r", encoding="utf-8").read()),
    ),
]
