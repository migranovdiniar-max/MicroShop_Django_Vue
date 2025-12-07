# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Order, OrderItem


# Инлайн для товаров в заказе
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product_id", "product_name", "price", "quantity", "subtotal")
    readonly_fields = ("subtotal",)

    def subtotal(self, obj):
        return f"${obj.subtotal:.2f}"
    subtotal.short_description = "Подытог"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "colored_status",
        "total_amount_formatted",
        "items_count",
        "total_quantity",
        "user_name",
        "created_at_formatted",
        "view_items_link",
    )
    list_filter = (
        "status",
        "created_at",
        "updated_at",
    )
    search_fields = ("id", "user_id", "user_name", "user_email", "shipping_address")
    date_hierarchy = "created_at"
    inlines = [OrderItemInline]
    readonly_fields = (
        "user_id", "total_amount", "created_at", "updated_at",
        "items_count_calc", "total_quantity_calc"
    )
    list_editable = ("status",)
    actions = ["mark_as_confirmed", "mark_as_shipped", "mark_as_delivered", "mark_as_cancelled"]

    fieldsets = (
        ("Основная информация", {
            "fields": ("user_id", "user_name", "user_email")
        }),
        ("Доставка и статус", {
            "fields": ("status", "shipping_address")
        }),
        ("Финансы", {
            "fields": ("total_amount", "items_count_calc", "total_quantity_calc"),
            "description": "Сумма и количество рассчитываются автоматически"
        }),
        ("Даты", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    # Цветной статус
    def colored_status(self, obj):
        colors = {
            "pending": "#ffc107",      # жёлтый
            "confirmed": "#007bff",    # синий
            "shipped": "#17a2b8",      # бирюзовый
            "delivered": "#28a745",    # зелёный
            "cancelled": "#dc3545",    # красный
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background:{}; color:white; padding:4px 10px; border-radius:4px; font-size:11px;">{}</span>',
            color, obj.get_status_display()
        )
    colored_status.short_description = "Статус"

    # Форматированная сумма
    def total_amount_formatted(self, obj):
        return f"${obj.total_amount:.2f}"
    total_amount_formatted.short_description = "Сумма"

    # Дата в удобном виде
    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%d.%m.%Y %H:%M")
    created_at_formatted.short_description = "Создан"

    # Количество товаров (дублируем для детального просмотра)
    def items_count_calc(self, obj=None):
        return obj.items_count if obj and obj.pk else "-"
    items_count_calc.short_description = "Кол-во позиций"

    def total_quantity_calc(self, obj=None):
        return obj.total_quantity if obj and obj.pk else "-"
    total_quantity_calc.short_description = "Кол-во единиц"

    # Ссылка на товары
    def view_items_link(self, obj):
        if obj.items.exists():
            from django.urls import reverse
            url = reverse("admin:orders_orderitem_changelist") + f"?order__id__exact={obj.id}"
            return format_html('<a href="{}" style="color:#e83e8c;">Товары ?</a>', url)
        return "—"
    view_items_link.short_description = "Товары"

    # Массовые действия
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status="confirmed")
        self.message_user(request, "Выбранные заказы подтверждены.")
    mark_as_confirmed.short_description = "Подтвердить заказы"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status="shipped")
        self.message_user(request, "Заказы отмечены как отправленные.")
    mark_as_shipped.short_description = "Отправить заказы"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status="delivered")
        self.message_user(request, "Заказы отмечены как доставленные.")
    mark_as_delivered.short_description = "Доставить заказы"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status="cancelled")
        self.message_user(request, "Заказы отменены.")
    mark_as_cancelled.short_description = "Отменить заказы"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_id", "product_name", "price", "quantity", "subtotal", "created_at")
    list_filter = ("order__status", "created_at")
    search_fields = ("product_name", "order__id", "order__user_id")
    readonly_fields = ("subtotal",)

    def subtotal(self, obj):
        return f"${obj.subtotal:.2f}"
    subtotal.short_description = "Подытог"