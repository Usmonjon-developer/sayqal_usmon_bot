from django.db import models

class Category(models.Model):
    name_uz = models.CharField(max_length=100, null=False, blank=False)
    name_ru = models.CharField(max_length=100, null=False, blank=False)
    name_en = models.CharField(max_length=100, null=False, blank=False)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    def __str__(self):
        return self.name_uz

    class Meta:
        db_table = "category"
        managed = False
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Product(models.Model):
    TYPE_CHOICES = [
        ('l', 'liter'),
        ('kg', 'kilogram'),
        ('ta', 'ta')
    ]
    name_uz = models.CharField(max_length=100, null=False, blank=False)
    name_ru = models.CharField(max_length=100, null=False, blank=False)
    name_en = models.CharField(max_length=100, null=False, blank=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    price = models.FloatField()
    description_uz = models.TextField()
    description_ru = models.TextField()
    description_en = models.TextField()
    image = models.ImageField(upload_to='product_images/')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name_uz

    class Meta:
        db_table = "product"
        managed = False
        verbose_name = "Product"
        verbose_name_plural = "Products"


class User(models.Model):
    first_name = models.CharField(max_length=100, null=False, blank=False)
    lang_id = models.CharField(max_length=100, null=False, blank=False)
    phone_number = models.CharField(max_length=100, null=False, blank=False)
    chat_id = models.CharField(max_length=100, unique=True, null=False, blank=False)  # 🟢 unique bo‘lishi kerak

    def __str__(self):
        return f"{self.first_name}"

    class Meta:
        db_table = "user"
        managed = True
        verbose_name = "User"
        verbose_name_plural = "Users"


class Suggestion(models.Model):
    chat_id = models.ForeignKey(
        User,
        to_field="chat_id",  # 🩵 asosiy tuzatish
        on_delete=models.CASCADE,
        db_column="chat_id"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chat_id} - {self.message[:30]}"

    class Meta:
        db_table = "suggestion"
        managed = False
        verbose_name = "Suggestion"
        verbose_name_plural = "Suggestions"