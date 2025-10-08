from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", home_page, name="home_page"),

    # AUTH
    path("login_page/", login_page, name="login_page"),
    path("logout_page/", logout_page, name="logout_page"),

    # CATEGORY
    path("categories/", category_list, name="category_list"),
    path("categories/create/", category_create, name="category_create"),
    path("categories/<int:pk>/edit/", category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", category_delete, name="category_delete"),

    # PRODUCT
    path("products/", product_list, name="product_list"),
    path("products/create/", product_create, name="product_create"),
    path("products/<int:pk>/edit/", product_edit, name="product_edit"),
    path("products/<int:pk>/delete/", product_delete, name="product_delete"),

    # USER
    path("users/", user_list, name="user_list"),
    path("users/create/", user_create, name="user_create"),
    path("users/<int:pk>/edit/", user_edit, name="user_edit"),
    path("users/<int:pk>/delete/", user_delete, name="user_delete"),

    # SUGGESTION
    path("suggestion/", suggestion_list, name="suggestion_list"),
    path("suggestion/<int:pk>/delete/", suggestion_delete, name="suggestion_delete"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)