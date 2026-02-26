from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product, Review
from .serializers import CategoryListSerializer, ProductListSerializer, ReviewListSerializer, CategoryDetailSerializer,ProductDetailSerializer, ReviewDetailSerializer


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
    category = Category.objects.all()
    data = CategoryListSerializer(category, many=True).data

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
    product = Product.objects.all()
    data = ProductListSerializer(product, many=True).data

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
    reviews = Review.objects.all()
    data = ReviewListSerializer(reviews, many=True).data

    return Response(
        data=data, 
        status=status.HTTP_200_OK
    )



