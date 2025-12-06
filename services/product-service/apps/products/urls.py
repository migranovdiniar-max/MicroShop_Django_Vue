# products/urls.py  (или catalog/urls.py)
from django.urls import path
from . import views

app_name = "catalog"  # или "products" — как тебе удобнее

urlpatterns = [
    # ──────────────────────────────
    # Категории
    # ──────────────────────────────
    path(
        "categories/",
        views.CategoryListView.as_view(),
        name="category-list"
    ),
    path(
        "categories/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category-detail"
    ),

    # ──────────────────────────────
    # Товары
    # ──────────────────────────────
    path(
        "products/",
        views.ProductListView.as_view(),
        name="product-list"
    ),
    path(
        "products/<int:pk>/",
        views.ProductDetailView.as_view(),
        name="product-detail"
    ),

    # ──────────────────────────────
    # Действия с количеством на складе (резервация / снятие резерва / проверка)
    # ──────────────────────────────
    path(
        "products/<int:product_id>/reserve/",
        views.reserve_product,
        name="product-reserve"
    ),
    path(
        "products/<int:product_id>/release/",
        views.release_product,
        name="product-release"
    ),
    path(
        "products/<int:product_id>/availability/",
        views.check_availability,
        name="product-availability"
    ),
]