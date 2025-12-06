# apps/products/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.db.models import Count


from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at",)
    fields = ("name", "slug", "description", "created_at")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            Count("products")
        )

    @admin.display(description="Кол-во товаров", ordering="products__count")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # === Отображение в списке ===
    list_display = [
        'name', 'price', 'category', 'stock_quantity', 'is_active', 'in_stock_badge', 'preview_image'
    ]
    list_editable = ['price', 'stock_quantity', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['name', 'description', 'category__name']
    autocomplete_fields = ['category']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    # === Форма редактирования (fieldsets) ===
    fieldsets = (
        (None, {
            "fields": ("name", "category", "price", "stock_quantity")
        }),
        ("Контент", {
            "fields": ("description", "image_url")
        }),
        ("Статус", {
            "fields": ("is_active",)
        }),
        ("Даты", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    readonly_fields = ("created_at", "updated_at")

    # === Кастомные поля ===
    def preview_image(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="max-height: 150px; border-radius: 8px;" />',
                obj.image_url
            )
        return format_html('<span style="color: #999;">(Нет изображения)</span>')

    preview_image.short_description = "Превью изображения"

    def in_stock_badge(self, obj):
        if obj.stock_quantity > 0:
            return format_html(
                '<span style="background:#28a745;color:white;padding:4px 8px;border-radius:4px;font-size:11px;">В наличии ({})</span>',
                obj.stock_quantity
            )
        else:
            return format_html(
                '<span style="background:#dc3545;color:white;padding:4px 8px;border-radius:4px;font-size:11px;">Нет в наличии</span>'
            )

    in_stock_badge.short_description = "Наличие"

    # === Действия ===
    actions = ["reserve_1", "release_1", "reserve_10", "release_10"]

    def reserve_1(self, request, queryset):
        for product in queryset:
            product.reserve_quantity(1)
        self.message_user(request, f"Зарезервировано по 1 шт. у {queryset.count()} товар(ов)")

    reserve_1.short_description = "📦 Зарезервировать 1 шт."

    def release_1(self, request, queryset):
        for product in queryset:
            product.release_quantity(1)
        self.message_user(request, f"Освобождено по 1 шт. у {queryset.count()} товар(ов)")

    release_1.short_description = "🔄 Освободить 1 шт."

    def reserve_10(self, request, queryset):
        for product in queryset:
            product.reserve_quantity(10)
        self.message_user(request, f"Зарезервировано по 10 шт. у {queryset.count()} товар(ов)")

    reserve_10.short_description = "📦 Зарезервировать 10 шт."

    def release_10(self, request, queryset):
        for product in queryset:
            product.release_quantity(10)
        self.message_user(request, f"Освобождено по 10 шт. у {queryset.count()} товар(ов)")

    release_10.short_description = "🔄 Освободить 10 шт."
