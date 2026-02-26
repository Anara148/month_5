from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    
    def __str__(self):
        return self.name
    

class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название товара')
    description = models.TextField(verbose_name='Описание', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    
    def __str__(self):
        return self.title
    


class Review(models.Model):
    text = models.TextField(verbose_name='Отзыв')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Товар')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Отзыв на {self.product.title}'
