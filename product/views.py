from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product, Review
from .serializers import CategoryListSerializer, ProductListSerializer, ReviewListSerializer, CategoryDetailSerializer,ProductDetailSerializer, ReviewDetailSerializer
from django.db.models import Count

@api_view(['GET'])
def category_detail_api_view(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return Response(data={'error': 'category does not exist!'},
                        status=status.HTTP_404_NOT_FOUND)
    data = CategoryDetailSerializer(category).data
    return Response(data=data)


@api_view(['GET'])
def category_list_api_view(request):
    categories = Category.objects.annotate(products_count=Count('products'))
    data = CategoryListSerializer(categories, many=True).data

    return Response(
        data=data,
        status=status.HTTP_200_OK
    )



@api_view(['GET'])
def product_detail_api_view(request, id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response(data={'error': 'product does not exist!'},
                        status=status.HTTP_404_NOT_FOUND)
    data = ProductDetailSerializer(product).data
    return Response(data=data)



@api_view(['GET'])
def product_list_api_view(request):
    products = Product.objects.select_related('category').all()
    data = ProductListSerializer(products, many=True).data

    return Response(
        data=data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def review_detail_api_view(request, id):
    try:
        review = Review.objects.get(id=id)
    except Review.DoesNotExist:
        return Response(data={'error': 'review does not exist!'},
                        status=status.HTTP_404_NOT_FOUND)
    data = ReviewDetailSerializer(review).data
    return Response(data=data)


@api_view(['GET'])
def review_list_api_view(request):
    reviews = Review.objects.all().distinct()
    data = ReviewListSerializer(reviews, many=True).data

    return Response(
        data=data, 
        status=status.HTTP_200_OK
    )


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

