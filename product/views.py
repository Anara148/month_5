from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product, Review
from .serializers import (
    CategoryListSerializer, ProductListSerializer, ReviewListSerializer,
    CategoryDetailSerializer,ProductDetailSerializer, ReviewDetailSerializer, 
    CategoryValidateSerializer, ProductValidateSerializer, ReviewValidateSerializer
)
from django.db.models import Count
from rest_framework.viewsets import ModelViewSet
from common.permissions import IsOwner, IsAnonymous
from common.permissions import IsModerator
from common.validators import validate_age_from_token
from rest_framework.exceptions import ValidationError



class CategoryViewSet(ModelViewSet):
    
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
        return CategoryDetailSerializer
    

@api_view(['GET', 'PUT', 'DELETE'])
def category_detail_api_view(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return Response(data={'error': 'category does not exist!'},
                        status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        data = CategoryDetailSerializer(category).data
        return Response(data=data)
    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'PUT':
        category.name = request.data.get('name')
        category.save() 
        return Response(status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def category_list_api_view(request):
    print(request.user)
    if request.method == 'GET':

        categories = Category.objects.annotate(products_count=Count('products'))
        data = CategoryListSerializer(categories, many=True).data

        return Response(
            data=data,
            status=status.HTTP_200_OK
        )
    elif request.method == 'POST':
        serializer = CategoryValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)

        name = serializer.validated_data.get('name')
        category = Category.objects.create(name=name) 
        return Response(status=status.HTTP_201_CREATED)


class ProductViewSet(ModelViewSet):
    
    queryset = Product.objects.select_related(
        'category'
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail_api_view(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response(data={'error': 'товар не существует!'},
                        status=status.HTTP_404_NOT_FOUND)
    if request.method in ['PUT', 'DELETE']:
        if not request.user.is_authenticated:
            return Response({'error': 'Требуется авторизация'}, status=401)

        if not IsModerator().has_object_permission(request, None, product):
            return Response({'error': 'У вас нет прав на это действие'},
                            status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        data = ProductDetailSerializer(product).data
        return Response(data=data)
    
    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    elif request.method == 'PUT':
        product.title = request.data.get('title')
        product.description = request.data.get('description')
        product.price = request.data.get('price')
        category_id = request.data.get('category')
        product.category = Category.objects.get(id=category_id)
        product.save() 
        return Response(status=status.HTTP_200_OK)



@api_view(['GET', 'POST'])
def product_list_api_view(request):
    if request.method == 'GET':
        products = Product.objects.select_related('category').all()
        data = ProductListSerializer(products, many=True).data

        return Response(
            data=data,
            status=status.HTTP_200_OK
        )
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'error': 'Требуется авторизация'}, status=401)
        
        try:
            validate_age_from_token(request.user, min_age=18)
        except ValidationError as e:
            return Response({'error': e.detail[0]}, status=403)

        
        if not IsModerator().has_permission(request, None):
            return Response({'error': 'Модератор не может создавать продукты'},
                            status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, 
                            data=serializer.errors)


        title = serializer.validated_data.get('title')
        description = serializer.validated_data.get('description')
        price = serializer.validated_data.get('price')
        category_id = serializer.validated_data.get('category')
        
        
        product = Product.objects.create(
            title=title,
            description=description,
            price=price,
            category_id=category_id,
            owner=request.user
        )
        return Response(status=status.HTTP_201_CREATED)
    
    
class ReviewViewSet(ModelViewSet):
    
    queryset = Review.objects.select_related(
        'product'
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ReviewListSerializer
        return ReviewDetailSerializer



@api_view(['GET', 'PUT', 'DELETE'])
def review_detail_api_view(request, id):
    try:
        review = Review.objects.get(id=id)
    except Review.DoesNotExist:
        return Response(data={'error': 'review does not exist!'},
                        status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        data = ReviewDetailSerializer(review).data
        return Response(data=data)
    elif request.method == 'DELETE':
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'PUT':

        review.text = request.data.get('text')
        review.stars = request.data.get('stars')
        review.product_id = request.data.get('product_id')
        review.save() 
        return Response(status=status.HTTP_201_CREATED)



@api_view(['GET', 'POST'])
def review_list_api_view(request):
    if request.method == 'GET':
        reviews = Review.objects.select_related('product').all()
        data = ReviewListSerializer(reviews, many=True).data

        return Response(
            data=data, 
            status=status.HTTP_200_OK
        )
    elif request.method == 'POST':
        serializer = ReviewValidateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data=serializer.errors)


        text = serializer.validated_data.get('text')
        stars = serializer.validated_data.get('stars')
        product_id = serializer.validated_data.get('product_id')
        
        review = Review.objects.create(
            text=text,
            stars=stars,
            product_id=product_id
        )
        return Response(status=status.HTTP_201_CREATED) 



@api_view(['GET'])
def products_with_reviews_api_view(request):
    products = Product.objects.select_related('category').prefetch_related('reviews').all()
    result = []
    
    for product in products:
        reviews_data = []
        stars_sum = 0
        
        for review in product.reviews.all():
            reviews_data.append({
                'id': review.id,
                'text': review.text,
                'stars': review.stars
            })
            stars_sum += review.stars
        
        avg_rating = round(stars_sum / product.reviews.count(), 1) if product.reviews.count() > 0 else None
        
        result.append({
            'id': product.id,
            'title': product.title,
            'price': product.price,
            'category': product.category.id,
            'category_name': product.category.name,
            'reviews': reviews_data,
            'average_rating': avg_rating
        })
    
    return Response(data=result)

