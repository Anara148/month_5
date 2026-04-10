from django.contrib import admin
from django.urls import path, include
from product import views
from rest_framework.routers import DefaultRouter
from product.views import CategoryViewSet, ProductViewSet, ReviewViewSet
from .swagger import urlpatterns as swagger_urls


router = DefaultRouter()
router.register(
    'categories', CategoryViewSet
)
router.register(
    'products', ProductViewSet
)
router.register(
    'reviews', ReviewViewSet
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from users.views import CustomJWTView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/categories/', views.category_list_api_view),
    path('api/v1/categories/<int:id>/', views.category_detail_api_view),

    path('api/v1/products/', views.product_list_api_view),
    path('api/v1/products/<int:id>/', views.product_detail_api_view),

    path('api/v1/reviews/', views.review_list_api_view),
    path('api/v1/reviews/<int:id>/', views.review_detail_api_view),
    path('api/v1/products/reviews/', views.products_with_reviews_api_view), 


    path('api/v2/', include(router.urls)),
    path('api/v1/users/', include('users.urls')),

    path('api/token/', CustomJWTView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    

]

urlpatterns += swagger_urls