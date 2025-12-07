# cart/admin.py или orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Cart, CartItem


# Инлайн для товаров в корзине — будет показываться прямо на странице корзины
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ("product_id", "product_name", "price", "quantity", "subtotal")
    readonly_fields = ("subtotal",)

    def has_change_permission(self, request, obj=None):
        # Разрешаем редактировать только если корзина ещё не оплачена (можно доработать)
        return True

    def subtotal(self, obj):
        return f"${obj.subtotal:.2f}"
    subtotal.short_description = "Подытог"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "user_id",
        "total_items_display",
        "total_amount_display",
        "created_at",
        "updated_at",
        "view_items_link",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("user_id",)
    date_hierarchy = "created_at"
    inlines = [CartItemInline]
    readonly_fields = ("user_id", "created_at", "updated_at", "total_amount_calculated", "total_items_calculated")

    fieldsets = (
        (None, {
            "fields": ("user_id",)
        }),
        ("Автоматические расчёты", {
            "fields": ("total_items_calculated", "total_amount_calculated"),
            "description": "Эти поля рассчитываются автоматически",
        }),
        ("Даты", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    # Красивые отображения в списке
    def total_items_display(self, obj):
        count = obj.total_items
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">{} шт.</span>',
            count
        ) if count > 0 else "0"
    total_items_display.short_description = "Товаров"

    def total_amount_display(self, obj):
        amount = obj.total_amount
        return format_html(
            '<span style="font-weight: bold; color: #007bff;">${:.2f}</span>',
            amount
        )
    total_amount_display.short_description = "Сумма"

    # Ссылка на просмотр товаров в корзине
    def view_items_link(self, obj):
        if obj.items.exists():
            url = reverse("admin:cart_cartitem_changelist") + f"?cart__id__exact={obj.id}"
            return format_html(
                '<a href="{}" style="color:#dc3545; font-weight:bold;">Посмотреть товары →</a>',
                url
            )
        return "—"
    view_items_link.short_description = "Товары"

    # Дублируем расчёты в деталке (на случай, если кто-то смотрит без инлайна)
    def total_items_calculated(self, obj=None):
        if obj and obj.pk:
            return obj.total_items
        return "-"
    total_items_calculated.short_description = "Всего товаров"

    def total_amount_calculated(self, obj=None):
        if obj and obj.pk:
            return f"${obj.total_amount:.2f}"
        return "-"
    total_amount_calculated.short_description = "Итоговая сумма"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product_id", "product_name", "price", "quantity", "subtotal", "created_at")
    list_filter = ("cart__user_id", "created_at")
    search_fields = ("product_name", "product_id", "cart__user_id")
    list_editable = ("quantity", "price")
    readonly_fields = ("subtotal", "created_at", "update_at")

    fieldsets = (
        (None, {
            "fields": ("cart", "product_id", "product_name")
        }),
        ("Цена и количество", {
            "fields": ("price", "quantity", "subtotal")
        }),
        ("Даты", {
            "fields": ("created_at", "update_at"),
            "classes": ("collapse",),
        }),
    )

    def subtotal(self, obj):
        return f"${obj.subtotal:.2f}"
    subtotal.short_description = "Подытог"