from rest_framework import serializers
from .models import Category, Product, Review
from rest_framework.exceptions import ValidationError
from decimal import Decimal 



class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__' 


class CategoryListSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(source='products.count', read_only=True)
    
    class Meta:
        model = Category
        fields = 'id name products_count'.split()
       


class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'  
        
        

class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = 'id title price category category_name'.split()   
        


class ReviewDetailSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__' 


class ReviewListSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)
    
    class Meta:
        model = Review
        fields = 'id text product product_title'.split()  



class CategoryValidateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)



class ProductValidateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2, min_value=Decimal(0.01))
    category = serializers.IntegerField()
        

class ReviewValidateSerializer(serializers.Serializer):
    text = serializers.CharField()
    stars = serializers.IntegerField(min_value=1, max_value=5)
    product_id = serializers.IntegerField()


def validate_category(self, category):
    try:
        Category.objects.get(id=category)
    except Category.DoesNotExist:
        raise ValidationError('Category is not exist')
    return category


def validate_product_id(self, product_id):
    try:
        Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise ValidationError('Product is not exist')
    return product_id


def validate_stars(self, stars):
    stars_from_db = Review.objects.filter(id__in=stars)
    if len(stars) != len(stars_from_db):
        raise ValidationError('Review does not exist')
    return stars
