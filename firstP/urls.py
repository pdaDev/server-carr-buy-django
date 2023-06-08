from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import render

from django.urls import path, include, re_path
from rest_framework import routers
from .api import *

from rest_framework_swagger.views import get_swagger_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


router = routers.DefaultRouter()
router.register('car/brends', BrendViewSet)
router.register(r"car/generations", GenerationViewSet)
router.register(r"car/models", ModelViewSet)
router.register(r'car/generation_variants', GenerationVariantViewSet)
router.register(r'car/equipments', EquipmentsViewSet)
router.register(r'car/cars', CarViewSet)
router.register(r"reviews", ReviewsViewSet)
router.register(r'producers', ProducersViewSet)
router.register('engines', EnginesViewSet)
router.register('transmission', TransmissionViewSet)
router.register(r'administration/user', AdminUserViewSet)
router.register('car/concrete-car', ConcreteCarViewSet)





urlpatterns = [
                  path('reviews/me/', MyRewiewsListAPI.as_view()),
                  path('handbook/', HandbookAPIView.as_view()),
                  path('car/info/', CarRetrieveAPIView.as_view()),
                  path('car/price/', CarPriceAPIView.as_view()),
                  path('car/brend/<int:pk>/', CarBrendRetrieveAPIView.as_view()),
                  path('car/brend/populars/', MostPopularBrendsAPIVIew.as_view()),
                  path('car/generation/<int:pk>/', CarGenerationRetrieveAPIView.as_view()),
                  path('car/model/<int:pk>/', CarModelRetrieveAPIView.as_view()),
                  path('car/brend/<int:pk>/models/', CarBrendModelsAPIView.as_view()),
                  path('car/model/<int:pk>/generations/', CarModelGenerationsAPIView.as_view()),
                  path('car/generation/<int:pk>/equipments/', CarGenerationEquipmentsAPIView.as_view()),
                  path('car/generation/<int:pk>/equipments-generations_variants/',
                       CarGenerationEuipmentsAndGenerationVariantsn.as_view()),
                  path('car/equipment/<int:pk>/car-body-types/', CarEquipmentsCarBodyTypesAPIView.as_view()),
                  path('car/id/', CarIdAPIView.as_view()),
                  path('car/<int:pk>/search-info/', CarSearchInfoAPIView.as_view()),
                  path('user/<int:pk>/', UserRetrieveAPIView.as_view()),
                  path('reviews/info/', ReviewInfoAPIView.as_view()),
                  path("advertisements/", AdvertisementListCreateAPIView.as_view()),
                  path("advertisements/me/", AdvertisementsMeAPIView.as_view()),
                  path("advertisements/me/history/", AdvertisementHistoryListAPIView.as_view()),
                  path("advertisements/me/recommendations/", AdvertisementRecomendationsListAPIView.as_view()),
                  path("advertisements/me/<int:pk>/", AdvertisementsMeAPIView.as_view()),
                  path("advertisements/<int:pk>/", AdvertisementRetrieveDeletePatchAPIView.as_view()),
                  path('api/auth/register/', RegisterVIEW.as_view()),
                  path("advertisements/favourites/ids/", FavouriteAdvertisementIdsAPIView.as_view()),
                  path("advertisements/favourites/", FavouriteAdvertisementAPI.as_view()),
                  path("advertisements/favourites/<int:pk>/", FavouriteAdvertisementAPI.as_view()),
                  path("compare/ids/", CompareIdsListAPIView.as_view()),
                  path("compare/concrete/", CompareByTypeAPIView.as_view()),
                  path("compare/", CompareAPIView.as_view()),
                  path("compare/<int:pk>/", CompareAPIView.as_view()),
                  path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
                  path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                  path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
                  path('car/name/<int:pk>/', CarGetFullNameAPIView.as_view()),
                  path('api/auth/me/', AuthorizationVIEW.as_view()),
                  path('api/auth/activate/<str:pk>/', AuthActivateAPIView.as_view()),
                  path('api/auth/activate/', AuthActivateAPIView.as_view()),
                  path('api/auth/reset_password/', ResetPasswordAPIView.as_view()),
                  path('chat/cars/', ChatCarsAPIVIew.as_view()),
                  path('chat/users/', ChatUsersAPIVIew.as_view()),
                  path('test/cars/', TestApiView.as_view()),

                  path("", include(router.urls)),
              ] + static('/media/', document_root=settings.MEDIA_ROOT)
