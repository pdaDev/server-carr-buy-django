import string
import random

import ujson
from django.http import QueryDict
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str, force_bytes
from .models import *
from django.shortcuts import redirect
from .serializers import *
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.mail import EmailMessage
from django.conf import settings

from itertools import chain

import uuid


class PhotosManager:
    def __init__(self, Model, fk):
        self.Model = Model
        self.fk = fk

    def parse_added(self, request, instance):
        if 'photos' in request.data.keys():
            photos = dict(request.data)['photos']
            for p in photos:
                args = {self.fk: instance}
                self.Model.objects.create(**args, photo=p)

    def parse_deleted(self, request, instance):
        if 'deleted_photos' in request.data.keys():
            delete_photos = dict(request.data)['deleted_photos']
            for id in delete_photos:
                try:
                    photo = self.Model.objects.get(id=id)
                    photo.delete()
                except:
                    photo = None

    def parse_added_and_deleted(self, request, instance):
        self.parse_added(request, instance)
        self.parse_deleted(request, instance)


class EngineViewSet(viewsets.ModelViewSet):
    queryset = Engine.objects.all()

    serializer_class = EngineSerializer
    permission_classes = [
        permissions.AllowAny
    ]


def send_account_confirmation_mail(user_id):
    user = dict(UserSerializer(AuthUser.objects.get(id=user_id)).data)
    subject = "Активация аккаунта"
    user_first_name = user['first_name']
    user_last_name = user['last_name']
    user_name = f"{user_first_name} {user_last_name}"
    from_email = 'settings.EMAIL_HOST_USER'
    encoded_user_id = urlsafe_base64_encode(force_bytes(user_id))
    html_content = f'<h2>Дорогой, {user_name}!</h2><p>Для того чтобы активировать аккаунт, пожалуйста, перейдите по ссылке ниже<p>' \
                   f'{settings.ROOT_URL}api/auth/activate/{encoded_user_id}/'

    to = user['email']
    msg = EmailMessage(subject, html_content, from_email, [to])
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()


class RegisterVIEW(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            new_user = serializer.save()
            send_account_confirmation_mail(new_user.pk)
            return Response({"data": serializer.data})
        else:
            return Response({"data": "serializer.errors"}, status=status.HTTP_400_BAD_REQUEST)


class FavouriteAdvertisementAPI(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, **kwargs):
        data = FavouriteAdvertisement.objects.filter(user=request.user.id)

        if 'sort' in request.query_params.keys():
            sort = request.query_params['sort']

            data = AdvertisementFavouritesGetSerializer(data, many=True).data
            if sort is not None:
                if '-' in sort:
                    data = list(sorted(data, key=lambda d: d[sort.replace('-', '')], reverse=True))
                else:
                    data = list(sorted(data, key=lambda d: d[sort]))

        data = data if 'sort' in request.query_params.keys() else AdvertisementFavouritesGetSerializer(data,
                                                                                                       many=True).data
        has_pagination = 'limit' in request.query_params.keys() and 'offset' in request.query_params.keys()
        sliced = data
        if has_pagination:
            limit = int(request.query_params['limit'])
            offset = int(request.query_params['offset'])
            start = int(limit * offset)
            end = int((offset + 1) * limit)
            sliced = data[start:end]

        return Response({"count": len(list(data)), "results": sliced})

    def post(self, request, **kwargs):
        pk = request.data['id']
        try:
            ad = Advertisement.objects.get(advertisement_id=pk)
        except:
            return Response({"error": "there isn't such advertisement"})

        user = AuthUser.objects.get(id=request.user.id)

        try:
            already_favourite = FavouriteAdvertisement.objects.get(advertisement_id=pk, user=request.user.id)
        except:
            already_favourite = None

        if ad.status_code.code == 'O' and ad.owner != user and already_favourite is None:
            new_fav = FavouriteAdvertisement.objects.create(
                advertsment=ad,
                user=user
            )
        else:
            return Response({"error": "can't "})

        uid = User.objects.get(username=request.user).id
        list = FavouriteAdvertisement.objects.filter(user=uid)
        return Response({"results": AdvertisementFavouritesGetIdsSerializer(list, many=True).data})

    def delete(self, request, **kwargs):
        pk = kwargs['pk']
        try:
            instance = FavouriteAdvertisement.objects.get(advertsment=pk, user=request.user.id)
        except:
            return Response({"error": ""})

        instance.delete()
        uid = User.objects.get(username=request.user).id
        list = FavouriteAdvertisement.objects.filter(user=uid)
        return Response({"results": AdvertisementFavouritesGetIdsSerializer(list, many=True).data})


compareTypes = {
    "advertisement": "ad",
    "model": "model"
}


class CompareAPIView(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, **kwargs):
        type = request.query_params['type']

        if type not in compareTypes.values():
            return Response({"error": "this compare type isn't allowed"})
        if type == 'model':
            compares_list = Compare.objects.filter(user=request.user.id, type=type)
            generation_variants = CompareItemIdSerializer(compares_list, many=True).data
            compares_list = list(compares_list)
            cars = Car.objects
            data = []

            for gen_var in generation_variants:
                equipment = request.query_params.get(f'equipment-{gen_var}', None)
                if equipment is not None:
                    data.append(cars.get(equipment=equipment, generation_variant=gen_var))
                else:
                    data.append(cars.filter(generation_variant=gen_var).first())
            response = []
            for i in range(len(data)):
                response.append({
                    **CompareModelSerializer(compares_list[i]).data,
                    **CompareModelCarSerializer(data[i]).data
                })
            return Response(response)
        else:
            data = list(Compare.objects.filter(user=request.user.id, type=type))
            return Response(CompareAdvertisementSerializer(data, many=True).data)

    def post(self, request, **kwargs):
        pk = request.data['id']
        type = request.data['type']

        if type not in compareTypes.values():
            return Response({"error": "this compare type isn't allowed"})

        isModel = type == 'model'
        CompareElementList = GenerationVariant.objects if isModel else Advertisement.objects
        compareElKey = 'generation_variant_id' if isModel else 'advertisement_id'
        try:
            ad = CompareElementList.get(**{compareElKey: pk})
        except:
            return Response({"error": "there isn't such item for compare"})

        user = AuthUser.objects.get(id=request.user.id)

        try:
            already_added = Compare.objects.get(compare_item_id=pk, user=request.user.id)
        except:
            already_added = None

        if ((not isModel and ad.status_code.code == 'O') and ad.owner != user and already_added is None) or isModel:
            Compare.objects.create(
                user=user,
                compare_item_id=pk,
                type=type
            )
        else:
            return Response({"error": "can't "})

        uid = User.objects.get(username=request.user).id
        list = Compare.objects.filter(user=uid)
        return Response({"results": CompareItemsIdsSerialiazer(list, many=True).data})

    def delete(self, request, **kwargs):
        compare_item = kwargs['pk']
        type = request.query_params['type']
        if type not in compareTypes.values():
            return Response({"error": "this compare type isn't allowed"})
        try:
            instance = Compare.objects.get(compare_item_id=compare_item, user=request.user.id, type=type)
        except:
            return Response({"error": ""})

        instance.delete()
        uid = User.objects.get(username=request.user).id
        list = Compare.objects.filter(user=uid)
        return Response({"results": CompareItemsIdsSerialiazer(list, many=True).data})


class FavouriteAdvertisementIdsAPIView(generics.GenericAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, **kwargs):
        uid = User.objects.get(username=request.user).id
        list = FavouriteAdvertisement.objects.filter(user=uid)
        return Response({"results": AdvertisementFavouritesGetIdsSerializer(list, many=True).data})


class CompareIdsListAPIView(generics.GenericAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, **kwargs):
        uid = User.objects.get(username=request.user).id
        list = Compare.objects.filter(user=uid)
        return Response({"results": CompareItemsIdsSerialiazer(list, many=True).data})


class CompareByTypeAPIView(APIView):
    def post(self, request):
        type = request.data['type']
        elements = request.data['elements']
        elements_id = list(map(lambda el: el['compare_item_id'], elements))
        if type not in compareTypes.values():
            return Response({"error": "this compare type isn't allowed"})
        isModel = type == 'model'
        CompareElementList = Car.objects if isModel else Advertisement.objects
        compareElKey = 'car_id' if isModel else 'advertisement_id'
        data = CompareElementList.filter(**{f"{compareElKey}__in": elements_id})
        response_data = []
        characteristics_serializer = ModelCompareCharacteristicsSerializer if isModel else AdvertisementCompareCharacteristicsSerializer
        for i in range(data.count()):
            car = data[i] if isModel else data[i].car
            response_data.append({
                "id": elements[i]['id'],
                "compare_item_id": elements[i]['compare_item_id'],
                "photos": mock_photos,
                "characteristics": characteristics_serializer().get(data[i]),
                "car": CarSerializer().get_name_with_id(car),
                "type": "ad",
                "price": None if isModel else Price.objects.filter(advertisement=data[i]).latest('date').price
            })
        return Response(response_data)


class AuthorizationVIEW(generics.RetrieveAPIView):
    serializer_class = UserGetSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"data": UserGetSerializer(AuthUser.objects.get(id=request.user.id)).data})

    def patch(self, requst):
        user = AuthUser.objects.get(id=requst.user.id)
        serializer = AuthUserSerializer(user, data=requst.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response({"data": UserGetSerializer(user).data})


class AdvertisementRetrieveDeletePatchAPIView(generics.RetrieveAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementRetrieveSerializer

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = self.get_object()
        if request.user.id is not None and request.user.id != instance.owner:
            max_history_item = 10
            history = HistorySerializer(History.objects.filter(user_id=request.user.id), many=True).data

            if pk not in history:
                history_item_count = len(history)
                if history_item_count >= max_history_item:
                    history_item = History.objects.filter(user=request.user.id).earliest('date')
                    history_item.advertisement = Advertisement.objects.get(advertisement_id=pk)
                    history_item.date = datetime.now()
                    history_item.save()
                else:
                    user = AuthUser.objects.get(id=request.user.id)
                    History.objects.create(advertisement=instance, user=user, date=datetime.now())
            else:
                history_item = History.objects.get(user=request.user.id, advertisement=pk)
                history_item.date = datetime.now()
                history_item.save()

        return Response(self.get_serializer(instance).data)


class UserRetrieveAPIView(generics.RetrieveAPIView):
    queryset = AuthUser.objects.all()
    serializer_class = AnotherUserRetrieveSerializer


class CarModelGenerationsAPIView(APIView):
    def get(self, request, **kwargs):
        pk = kwargs.get('pk', None)
        if pk is not None:
            data = Generation.objects.filter(model_id=pk)
            return Response(GenerationOptionsSerializer(data, many=True).data)
        return Response({"err": "erer"})


class CarBrendModelsAPIView(APIView):
    def get(self, request, **kwargs):
        pk = kwargs.get('pk', None)
        if pk is not None:
            data = Model.objects.filter(brend_id=pk)
            return Response(ModelOptionsSerializer(data, many=True).data)
        return Response({"err": "erer"})


class CarGenerationEquipmentsAPIView(APIView):
    def get(self, request, **kwargs):
        pk = kwargs.get('pk', None)
        if pk is not None:
            data = Equipment.objects.filter(generation_id=pk)
            return Response(EquipmentOptionsSerializer(data, many=True).data)
        return Response({"err": "erer"})


class CarEquipmentsCarBodyTypesAPIView(APIView):
    def get(self, request, **kwargs):
        pk = kwargs.get('pk', None)
        if pk is not None:
            data = Car.objects.filter(equipment_id=pk)
            return Response(CarBodyTypesOptionsSerializer(data, many=True).data)
        return Response({"err": "erer"})


class CarIdAPIView(APIView):
    def get(self, request, **kwargs):
        equipment = request.query_params['equipment']
        generation_variant = request.query_params['generation_variant']
        data = Car.objects.get(equipment_id=equipment, generation_variant_id=generation_variant)
        return Response(data.car_id)


class CarSearchInfoAPIView(APIView):
    def get(self, request, **kwargs):
        pk = kwargs.get('pk', None)
        if pk is not None:
            try:
                data = Car.objects.get(car_id=pk)
            except:
                return Response({"err": "fsdf"})
            return Response(CarSearchInfoSerializer(data).data)
        return Response({"err": "erer"})


class AdvertisementsMeAPIView(APIView):
    permissions = [permissions.IsAuthenticated]
    queryset = Advertisement.objects.all()
    photos_manager = PhotosManager(AdvertisementCarPhotos, 'advertisement')

    def get(self, request):
        user = AuthUser.objects.get(id=request.user.id)
        data = Advertisement.objects.filter(owner=user)

        return Response(AdvertisementListSerializer(data, many=True).data)

    def post(self, request):
        serializer = AdvertisementCreateSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = AuthUser.objects.get(id=request.user.id)
            date = datetime.now()
            address_type = request.data['adress_type']
            address_guid = request.data['adress_guid']
            address_name = request.data['adress_name']

            try:
                address = Adress.objects.get(guid=address_guid)
            except:
                try:
                    if 'adress_parent_guid' in request.data.keys():
                        address_parent_guid = request.data['adress_parent_guid']
                        region = Adress.objects.get(parent__guid=address_parent_guid)

                    else:
                        region = None
                except:
                    address_parent_name = request.data['adress_parent_name']
                    address_parent_type = request.data['adress_parent_type']
                    address_parent_guid = request.data['adress_parent_guid']

                    region = Adress.objects.create(
                        type=address_parent_type,
                        guid=address_parent_guid,
                        name=address_parent_name
                    )
                address = Adress.objects.create(
                    type=address_type,
                    guid=address_guid,
                    name=address_name,
                    parent=region
                )
            try:
                car = Car.objects.get(car_id=request.data['car_id'])
            except:
                return Response({"error": "this car doesn't exist"})

            ad = Advertisement(
                owner=user,
                start_date=date,
                car=car,
                adress=address,
                status_code=Status.objects.get(code='O'),
                **serializer.validated_data
            )
            ad.save()
            p = Price(date=date, advertisement=ad, price=request.data['price'])
            p.save()

            self.photos_manager.parse_added(request, ad)

            return Response(ad.pk)
        return Response({"error": "wrong parameters"})

    def patch(self, request, **kwargs):

        user = AuthUser.objects.get(id=request.user.id)
        pk = kwargs.get('pk', None)

        if not pk:
            return Response({"error": "Method PUT not allowed"})
        try:
            instance = Advertisement.objects.get(advertisement_id=pk, owner=user)
        except:
            return Response({"error": "Objects doesn't exist"})

        if 'status' in request.data.keys():
            status_code = request.data['status']
            try:
                status = Status.objects.get(code=status_code)
            except:
                return Response({"error": "this code doesn't exist"})
            if status_code == 'O':
                instance.end_date = None
            if status_code == 'F':
                instance.end_date = datetime.now()
            instance.status_code = status

        if 'price' in request.data.keys():
            price_instance = Price.objects.filter(advertisement=pk).latest('date')
            last_price = CarPriceSerializer(price_instance).get_only_price()
            new_price_value = request.data.get('price')
            if last_price != new_price_value:
                # new_price = Price.objects.create(advertisement=instance, price=request.data['price'],
                #                                  date=datetime.now())
                price_instance.price = new_price_value
                price_instance.save()
                favs = FavouriteAdvertisement.objects.filter(advertsment=instance)
                users_from_favourites = FavouritesUserSerializer(favs, many=True).data
                for user in users_from_favourites:
                    data = AdvertisementRetrieveSerializer(instance).data
                    subject = "На объявление из избранных изменилась цена"
                    user_name = user['name']
                    from_email = 'settings.EMAIL_HOST_USER'
                    url = f"{settings.FRONTEND_URL}advertisement/{instance.pk}"
                    brend = data['name']['brend']['name']
                    model = data['name']['model']['name']
                    generation = data['name']['generation']['name']
                    car_name = f'{brend} {model} ({generation})'
                    engine_volume = data['car_characteristics']['engine']['volume']
                    engine_hp = data['car_characteristics']['engine']['hp']
                    engine_fuel = data['car_characteristics']['engine']['fuel']['ru_name']
                    engine = f'{engine_volume} л, {engine_fuel}, {engine_hp} л.с.'
                    html_content = render_to_string('email.html', {
                        "user_name": user_name,
                        "mileage": data['mileage'],
                        "engine": engine,
                        "url": url,
                        "date_of_production": data['date_of_production'],
                        "last_price": last_price,
                        "new_price_value": new_price_value,
                        "car_name": car_name
                    })
                    to = user['email']
                    msg = EmailMessage(subject, html_content, from_email, [to])
                    msg.content_subtype = "html"  # Main content is now text/html
                    msg.send()
        instance.save()
        serializer = AdvertisementCreateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.photos_manager.parse_added_and_deleted(request, instance)
        return Response({"data": "data"})

    def delete(self, request, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            return Response({"error": "Method PUT not allowed"})
        try:
            instance = Advertisement.objects.get(advertisement_id=pk)
        except:
            return Response({"error": "Objects doesn't exist"})
        instance.delete()
        return Response({"result": "success"})


class AdvertisementHistoryListAPIView(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        if request.user is not None:
            ads = History.objects.filter(user_id=request.user.id)
            return Response(HistoryListSerializer(ads, many=True).data)
        return Response({"error": "please authorize"})


class AdvertisementRecomendationsListAPIView(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        ads = Advertisement.objects.all()[:10]
        return Response(AdvertisementListSerializer(ads, many=True).data)


class AdvertisementListCreateAPIView(APIView):
    def post(self, request):
        sort = request.data['sort']
        filters = request.data['filters']
        data = Advertisement.objects.filter(status_code='O')

        if 'id' in request.data.keys() and request.data['id'] is not None:
            data.filter(advertisement_id__in=request.data['id'])

        if request.user.id is not None:
            user = AuthUser.objects.get(id=request.user.id)
            data = data.filter(~Q(owner=user))

        if filters is not None:
            f = Filtrator(data, filters)
            f.filter_by_min_max('engine.volume', 'car__equipment__engine__volume')
            f.filter_by_min_max('engine.horse_powers', 'car__equipment__engine__horse_power')
            f.filter_by_contains('engine.boost_type', 'car__equipment__engine__boost_type_code')
            f.filter_by_contains('engine.type', 'car__equipment__engine__boost_type_code')
            f.filter_by_contains('engine.cyllinder_arrangement_type',
                                 'car__equipment__engine__cyllinder_arrangement_type_code')
            f.filter_by_contains('engine.fuel_type', 'car__equipment__engine__fuel_type_code')
            f.filter_by_contains('engine.layout', 'car__equipment__generation__engine_layout_code')
            f.filter_by_min_max('date_of_production', 'date_of_production')
            f.filter_by_contains('transmission_type', 'car__equipment__transmission__type_code')
            f.filter_by_contains('car_drive_type', 'car__equipment__drive_type_code')
            f.filter_by_contains('carClass', 'car__equipment__generation__model__car_class_code')
            f.filter_by_contains('color', 'color')
            f.filter_by_value('in_taxi', 'in_taxi')
            f.filter_by_contains('ecological_class', 'car__generation_variant__generation__ecological_class_code')
            f.filter_by_contains('car_body_type', 'car__generation_variant__car_body_type_code')
            f.filter_by_min_max('to_100_acceleration', 'car__to_100_acceleration')
            f.filter_by_min_max('fuel_consumption', 'car__fuel_consumption')
            f.filter_by_min_max('fuel_tank', 'car__fuel_trunk_volume')
            f.filter_by_min_max('tank', 'car__max_trunk_volum')
            f.filter_by_min_max('width', 'car__width')
            f.filter_by_min_max('height', 'car__height')
            f.filter_by_min_max('clearance', 'car__clearence')
            f.filter_by_min_max('countOfSitPlaces', 'car__generation_variant__car_body_type_code__count_of_sit_places')
            f.filter_by_min_max('wheelSize', 'car__equipment__wheel_size')
            f.filter_by_contains('suspensionType', 'car__equipment__front_suspension_code')
            f.filter_by_contains('breakType', 'car__equipment__front_breaks_code')
            f.filter_by_min_max('mileage', 'mileage')
            f.filter_by_car('car')

            data = f.data
            if len(filters['tag']) > 0:
                car_tags = list(set([x.car for x in CarTag.objects.filter(tag_code__in=filters['tag']).all()]))
                data = data.filter(car__in=car_tags)

            if 'materials' in filters.keys() and len(filters['materials']) > 0:
                materials = filters['materials']
                equipments = list(
                    set([x.equipment for x in InteriorMaterial.objects.filter(material_code__in=materials)]))

                data = data.filter(car__equipment__in=equipments)

        if 'location' in request.data.keys():
            location = request.data['location']
            empty_query = Q()

            data = data.filter(
                (Q(adress__guid__in=location) if len(location) > 0 else empty_query) |
                (Q(adress__parent__guid__in=location) if len(location) > 0 else empty_query))

        if 'sort' in request.data.keys() and sort is not None and 'price' not in sort:
            data = data.order_by(sort)

        data = AdvertisementListSerializer(data, many=True).data
        if filters is not None and 'price' in filters.keys():
            price = filters['price']
            max_price = price['max']
            min_price = price['min']
            if max_price is not None:
                data = list(filter(lambda x: x['price'] <= max_price, data))
            if min_price is not None:
                data = list(filter(lambda x: x['price'] >= min_price, data))

        if sort is not None and 'price' in sort:
            if '-' in sort:
                data = list(sorted(data, key=lambda d: d['price'], reverse=True))
            else:
                data = list(sorted(data, key=lambda d: d['price']))
        has_pagination = 'limit' in request.query_params.keys() and 'offset' in request.query_params.keys()
        sliced = data
        if has_pagination:
            limit = int(request.query_params['limit'])
            offset = int(request.query_params['offset'])
            start = int(limit * offset)
            end = int((offset + 1) * limit)

            sliced = data[start:end]

        return Response({"count": len(list(data)), "results": sliced})

    def get(self, request, **kwargs):
        data = Advertisement.objects.filter(status_code='O')

        if request.user.id is not None:
            user = AuthUser.objects.get(id=request.user.id)
            data = data.filter(~Q(owner=user))
        filtrator = Filtrator(data, request.query_params)
        filtrator.filter_by_car('')
        data = filtrator.data

        if 'location' in request.query_params.keys():
            empty_query = Q()
            location = request.query_params.getlist('location')

            data = data.filter(
                (Q(adress__guid__in=location) if len(location) > 0 else empty_query) |
                (Q(adress__parent__guid__in=location) if len(location) > 0 else empty_query))
        return Response({"count": data.count()})


class Filtrator:
    data = []

    def __init__(self, objects, filters):
        self.data = objects
        self.filters = filters

    def filter_by_car(self, key):
        car = self.get_filter_by_complex_key(key)
        if car is not None:
            car = dict(car)
            generations = list(car['generations']) if 'generations' in car.keys() else []
            models = list(car['models']) if 'models' in car.keys() else []
            brends = list(car['brends']) if 'brends' in car.keys() else []
            ads = self.data
            empty_query = Q()
            self.data = ads.filter(
                (Q(car__equipment__generation__in=generations) if len(generations) > 0 else empty_query)
                | (Q(car__equipment__generation__model__in=models) if len(models) > 0 else empty_query) \
                | (Q(car__equipment__generation__model__brend__in=brends) if len(brends) > 0 else empty_query)
            )

    def filter_by_min_max(self, filter_key, column_key):
        current_filter = self.get_filter_by_complex_key(filter_key)

        if current_filter is not None:
            min_value = current_filter['min']
            max_value = current_filter['max']
            has_max = max_value is not None
            has_min = min_value is not None
            if has_min and has_max:
                self.data = self.data.filter(**self.get_filter_key(column_key, 'range', (min_value, float(max_value))))
            else:
                if has_max:
                    self.data = self.data.filter(**self.get_filter_key(column_key, 'lte', float(max_value)))
                if has_min:
                    self.data = self.data.filter(**self.get_filter_key(column_key, 'gte', float(min_value)))

    def filter_by_contains(self, filter_key, column_key):
        current_filter = self.get_filter_by_complex_key(filter_key)

        if current_filter is not None and len(current_filter):
            self.data = self.data.filter(**self.get_filter_key(column_key, 'in', current_filter))

    def filter_by_value(self, filter_key, column_key):
        current_filter = self.get_filter_by_complex_key(filter_key)
        if current_filter is not None:
            self.data = self.data.filter(**self.get_filter_key(column_key, '', current_filter))

    def get_filter_key(self, column, search_type, search_string):
        filter_key = column + '__' + search_type if len(search_type) > 0 else column
        return {filter_key: search_string}

    def get_filter_by_complex_key(self, complex_key):
        acc = self.filters
        keys = complex_key.split('.')
        if len(complex_key) == 0:
            return acc
        if keys[0] not in self.filters.keys():
            return None
        for key in keys:
            if acc[key] is None:
                return None
            acc = acc[key]
        return acc


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = AuthUser.objects.all()
    serializer_class = AdminUsersSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        sort = request.query_params.get('sort', None)
        query = request.query_params.get('query', None)
        if query is not None:
            words = query.split(' ')
            if len(words) == 2 and len(words[1] > 0):
                first, second = words
                queryset = queryset.filter(
                    Q(first_name__contains=first) | Q(last_name__contains=first) | Q(first_name__contains=second) | Q(last_name__contains=second))
            elif len(words) == 1:
                first = words[0]

                queryset = queryset.filter(Q(first_name__contains=first) | Q(last_name__contains=first))
        if sort is not None and 'total_ads' not in sort:
            queryset = queryset.order_by(sort)

        filtrator = Filtrator(queryset, request.query_params)
        filtrator.filter_by_contains('is_banned', 'is_banned')
        queryset = filtrator.data
        data = AdminUsersSerializer(queryset, many=True).data


        if sort is not None and 'total_ads' in sort:
            if '-' in sort:
                data = list(sorted(data, key=lambda d: d['total_ads'], reverse=True))
            else:
                data = list(sorted(data, key=lambda d: d['total_ads']))


        has_pagination = 'limit' in request.query_params.keys() and 'offset' in request.query_params.keys()
        sliced = data
        if has_pagination:
            limit = int(request.query_params['limit'])
            offset = int(request.query_params['offset'])
            start = int(limit * offset)
            end = int((offset + 1) * limit)

            sliced = data[start:end]

        return Response({"count": len(list(data)), "results": sliced})


class HandbookAPIView(APIView):
    models = {
        'DICTIONARY_ENGINE_POWER_SYSTEM': EnginePowerSystem,
        'DICTIONARY_ENGINE_TYPE': EngineType,
        'DICTIONARY_BOOST_TYPE': BoostType,
        'DICTIONARY_CAR_BODY_TYPE': CarBodyType,
        'DICTIONARY_CAR_CLASS': CarClass,
        'DICTIONARY_CYLLINDER_ARRANGEMENT_TYPE': CyllinderArrangement,
        'DICTIONARY_ENGINE_LAYOUT': EngineLayout,
        'DICTIONARY_ADVERTISEMENT_STATUS': Status,
        'DICTIONARY_COLOR': Color,
        'DICTIONARY_FUEL_TYPE': FuelType,
        'DICTIONARY_ECOLOGICAL_CLASS': EcologicalClass,
        'DICTIONARY_CAR_DRIVE': CarDrive,
        'DICTIONARY_TRANSMISSION_TYPE': TransmissionType,
        'DICTIONARY_SUSPENSION_TYPE': SuspensionType,
        'DICTIONARY_BREAK_TYPE': BreakType,
        'DICTIONARY_CAR_TAG': Tag,
        'DICTIONARY_MATERIAL': Material
    }
    serializers = {
        'DICTIONARY_BOOST_TYPE': BoostTypeSerializer,
        'DICTIONARY_CYLLINDER_ARRANGEMENT_TYPE': CyllinderArrangementSerializer,
        'DICTIONARY_ENGINE_POWER_SYSTEM': EnginePowerTypeSerializer,
        'DICTIONARY_ENGINE_TYPE': EngineTypeSerializer,
        'DICTIONARY_CAR_CLASS': CarClassSerializer,
        'DICTIONARY_ENGINE_LAYOUT': EngineLayoutSerializer,
        'DICTIONARY_FUEL_TYPE': FuelTypeSerializer,
        'DICTIONARY_ECOLOGICAL_CLASS': EcologicalClassSerializer,
        'DICTIONARY_CAR_DRIVE': CarDriveSerializer,
        'DICTIONARY_TRANSMISSION_TYPE': TransmissionTypeSerializer,
        'DICTIONARY_SUSPENSION_TYPE': SuspensionTypeSerializer,
        'DICTIONARY_BREAK_TYPE': BreakTypeSerializer,
        'DICTIONARY_CAR_TAG': TagSerializer,
        'DICTIONARY_MATERIAL': MaterialSerializer,
        'DICTIONARY_CAR_BODY_TYPE': CarBodyTypeSerializer,
        'DICTIONARY_COLOR': ColorSerializer,
        'DICTIONARY_ADVERTISEMENT_STATUS': AdvertisementStatusSerializer
    }

    def get_serializer(self, key):
        return self.serializers[key] if key in self.serializers.keys() else HandbookSerializer

    def get_list(self, key):
        return self.models[key].objects.all()

    def is_valid_key(self, key):
        return key in self.models.keys()

    def get(self, request):
        key = request.query_params['key']
        if self.is_valid_key(key):
            serializer = self.get_serializer(key)
            return Response({"data": serializer(self.get_list(key), many=True).data})
        return Response({"error": "handbook not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        key = request.query_params['key']

        if self.is_valid_key(key):
            serializer = self.get_serializer(key)(data=request.data)
            if serializer.is_valid(raise_exception=True):
                self.models[key].objects.create(**serializer.validated_data)

                return Response(serializer.validated_data)
        return Response({"error": "handbook not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        key = request.query_params['key']
        code = request.query_params['code']

        if self.is_valid_key(key):
            list = self.get_list(key)
            instance = list.get(code=code)


            if code != request.data['code']:

                serializer = self.get_serializer(key)(instance, data=request.data, partial=True)
                instance.delete()

                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.validated_data)
            else:
                serializer = self.get_serializer(key)(instance, data=request.data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.validated_data)

        return Response({"error": "handbook not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        key = request.query_params['key']
        code = request.query_params['code']

        if self.is_valid_key(key):
            list = self.get_list(key)
            try:
                instance = list.get(code=code)
                instance.delete()
                return Response({"result": "success"}, status=status.HTTP_200_OK)
            except:
                return Response({"error": "handbook not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "handbook not found"}, status=status.HTTP_404_NOT_FOUND)


class MyRewiewsListAPI(APIView):
    def get(self, request):
        list = Review.objects.filter(owner__id=request.user.id)
        return Response(ReviewListSerializer(list, many=True).data)


def get_paginated_response(self, data):
    page = self.paginate_queryset(data)
    if page is not None:
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    serializer = self.get_serializer(data, many=True)
    return Response({"results": serializer.data})


class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    permissions = [permissions.IsAuthenticatedOrReadOnly]
    photos_manager = PhotosManager(ReviewPhoto, 'review')

    def get_serializer_class(self):
        if self.action == 'list':
            return ReviewListSerializer
        if self.action == 'retrieve':
            return ReviewRetrieveSerializer
        if self.action in ('create', 'patch'):
            return ReviewCreateSerializer
        return ReviewSerializer

    def list(self, request, *args, **kwargs):
        data = self.get_queryset()
        points = ("comfort_point", "reliable_point", "contrallabilty_point",
                  "safety_point", "economic_point", "cross_country_point")

        sort = request.query_params.get('sort', None)

        def get_object_from_query(key):
            min = request.query_params.get(f'{key}[min]', None)
            max = request.query_params.get(f'{key}[max]', None)

            if min is not None or max is not None:
                return {
                    "min": float(min),
                    "max": float(max)
                }
            return None

        filters = {}
        for point in points:
            filters[point] = get_object_from_query(point)

        generations = request.query_params.getlist('generations')
        models = request.query_params.getlist('models')
        brends = request.query_params.getlist('brends')
        ads = data
        empty_query = Q()
        data = ads.filter(
            (Q(car__in=generations) if len(generations) > 0 else empty_query)
            | (Q(car__model__in=models) if len(models) > 0 else empty_query) \
            | (Q(car__model__brend__in=brends) if len(brends) > 0 else empty_query)
        )

        f = Filtrator(data, filters)
        for point in points:
            f.filter_by_min_max(point, point)
        data = f.data


        if sort is not None and 'score' not in sort:
            data = data.order_by(sort)

        data = self.get_serializer(data, many=True).data

        max_score = request.query_params.get('score[max]', None)
        min_score = request.query_params.get('score[min]', None)




        if max_score is not None:
            max_score = float(max_score)
            data = list(filter(lambda x: x['score'] <= max_score, data))
        if min_score is not None:
            min_score = float(min_score)
            data = list(filter(lambda x: x['score'] >= min_score, data))

        if sort is not None and 'score' in sort:
            if '-' in sort:
                data = list(sorted(data, key=lambda d: d['score'], reverse=True))
            else:
                data = list(sorted(data, key=lambda d: d['score']))
        has_pagination = 'limit' in request.query_params.keys() and 'offset' in request.query_params.keys()
        sliced = data
        if has_pagination:
            limit = int(request.query_params['limit'])
            offset = int(request.query_params['offset'])
            start = int(limit * offset)
            end = int((offset + 1) * limit)

            sliced = data[start:end]

        return Response({"count": len(list(data)), "results": sliced})

        page = self.paginate_queryset(data)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(data, many=True)
        return Response({"results": serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                car = Generation.objects.get(generation_id=request.data['car'])
            except:
                return Response({"err": "this car doesn't exist"})

            new_review = Review.objects.create(
                **serializer.validated_data,
                owner=AuthUser.objects.get(id=request.user.id),
                date=datetime.now(),
                car=car
            )

            self.photos_manager.parse_added(request, new_review)

            return Response(new_review.review_id)
        return Response({"error": serializer.errors})

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():

            serializer.save()

        self.photos_manager.parse_added_and_deleted(request, instance)

        return Response({"result": "success"})

    def delete(self, request):
        instance = self.get_object()
        if (AuthUser.objects.get(id=request.user.id) != instance.owner):
            return Response({"error": "you can't delete"})
        instance.delete()
        return Response({"data": "success"})


class CarGetFullNameAPIView(generics.RetrieveAPIView):
    serializer_class = CarFullNameSerializer
    queryset = Generation.objects.all()


class ReviewInfoAPIView(APIView):
    def get(self, request):
        data = Review.objects
        car = request.query_params

        generations = list(car['generations']) if 'generations' in car.keys() else []
        models = list(car['models']) if 'models' in car.keys() else []
        brends = list(car['brends']) if 'brends' in car.keys() else []

        filter_by_generation = len(generations) > 0
        filter_by_model = len(models) > 0
        filter_by_brend = len(brends) > 0

        if filter_by_generation:
            data = data.filter(car__equipment__generation=generations[0])
        elif filter_by_model:
            data = data.filter(car__equipment__generation__model=models[0])
        elif filter_by_brend:
            data = data.filter(car__equipment__generation__model__brend=brends[0])

        keys = ("comfort_point", "reliable_point", "contrallabilty_point", "safety_point", "economic_point",
                "cross_country_point")
        d = {"sum": {}, "count": {}}
        for review in list(data.all()):
            for k in keys:
                point = getattr(review, k)
                if point is not None:
                    if k in d.keys():
                        d["sum"][k] += point
                        d["count"][k] += 1
                    else:
                        d["sum"][k] = point
                        d["count"][k] = 1

        results = {}
        total = 0
        for k in keys:
            average_point = d["sum"][k] / d["count"][k]
            results[k] = average_point
            total += average_point

        total = total / len(keys)
        name = {"brend": None, "generation": None, "model": None}
        if filter_by_generation:
            generation = Generation.objects.get(generation_id=generations[0])
            generation_name = generation.name
            model_name = generation.model.name
            brend_name = generation.model.brend.name
            name = {"brend": brend_name, "generation": generation_name, "model": model_name}
        if filter_by_model:
            model = Model.objects.get(model_id=models[0])
            model_name = model.name
            brend_name = model.brend.name
            name = {"brend": brend_name, "model": model_name}
        if filter_by_brend:
            brend = Brend.objects.get(brend_id=brends[0])
            name = {"brend": brend.name}
        return Response({
            "total": total,
            "name": name,
            **results,
        })


class CarRetrieveAPIView(generics.GenericAPIView):
    queryset = Car.objects.all()

    def get(self, request):
        query = request.query_params
        if query:
            has_equipment = 'equipment' in query.keys()
            generation_variant = query['generation']

            generation = GenerationVarGen(GenerationVariant.objects.get(generation_variant_id=generation_variant)).data[
                'generation']

            equipment_instance = Equipment.objects.filter(generation=generation).first()

            if has_equipment:
                equipment = query['equipment']
                instance = Car.objects.get(equipment=equipment, generation_variant=generation_variant)
            else:
                instance = Car.objects.get(equipment=equipment_instance, generation_variant=generation_variant)

            return Response(CarCharacteristicsSerializer(instance).data)
        return Response()


class CarBrendRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Brend.objects.all()
    serializer_class = CarBrendRetrieveSerializer


class CarModelRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Model.objects.all()
    serializer_class = CarModelRetrieveSerializer


class CarGenerationRetrieveAPIView(generics.RetrieveAPIView):
    queryset = GenerationVariant.objects.all()
    serializer_class = CarGenerationRetrieveSerializer


class CarGenerationEuipmentsAndGenerationVariantsn(APIView):
    def get(self, request, **kwargs):
        pk = kwargs.get('pk', None)
        if pk is not None:
            equipments = Equipment.objects.filter(generation_id=pk)
            generation_variants = GenerationVariant.objects.filter(generation_id=pk)

            return Response({
                "generation_variants": GenerationVariantOptionsSerializer(generation_variants, many=True).data,
                "equipments": EquipmentOptionsSerializer(equipments, many=True).data
            })
        return Response({"err": "erer"})


class CarPriceAPIView(APIView):
    def get(self, request, **kwargs):
        pk = request.query_params.get('car_id', None)
        mileage = int(request.query_params.get('mileage', None))
        date_of_production = int(request.query_params.get('date_of_production', None))
        if pk is not None and mileage is not None and date_of_production is not None:
            mileage_dispersion_radius = 20000
            mileage_range = (max(0, mileage - mileage_dispersion_radius), mileage + mileage_dispersion_radius)
            prices = Price.objects.filter(advertisement__car=pk,
                                          advertisement__date_of_production=date_of_production,
                                          advertisement__mileage__in=mileage_range)
            if prices.count() == 0:
                prices = Price.objects.filter(advertisement__car=pk,
                                              advertisement__date_of_production=date_of_production)
            if prices.count() == 0:
                prices = Price.objects.filter(advertisement__car=pk)
            try:
                min_price = CarPriceSerializer(prices.earliest('price')).get_only_price()
                max_price = CarPriceSerializer(prices.latest('price')).get_only_price()
            except:
                min_price = None
                max_price = None

            return Response(
                {
                    "min": min_price,
                    "max": max_price
                }
            )
        return Response({"err": "erer"})


class AuthActivateAPIView(APIView):
    permissions = [permissions.AllowAny]

    def post(self, request):
        send_account_confirmation_mail(request.user.id)
        return Response({"result": "success"})

    def get(self, request, **kwargs):
        pk = kwargs.get('pk', None)
        if pk is not None:
            user_id = urlsafe_base64_decode(force_str(pk))
            user = AuthUser.objects.get(id=user_id)
            user.active = True
            user.save()
            return redirect(f'{settings.FRONTEND_URL}init?activated=True')
        return Response({"result": "error"})


class ResetPasswordAPIView(APIView):
    def get(self, request):
        code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        subject = "Восстановление пароля"
        from_email = 'settings.EMAIL_HOST_USER'
        html_content = f'<h2>Для того чтобы восстановить пароль введите код подтверждения<h2><h3>{code}<h3>'
        to = request.query_params.get('email', None)
        if to is not None:
            try:
                user = AuthUser.objects.get(username=to)
                msg = EmailMessage(subject, html_content, from_email, [to])
                msg.content_subtype = "html"  # Main content is now text/html
                msg.send()
                return Response({"code": code})
            except:
                return Response({"error": "erorr"}, status.HTTP_404_NOT_FOUND)
        return Response({"error": "erorr"}, status.HTTP_404_NOT_FOUND)

    def post(self, request):
        new_password = request.data['password']
        user_email = request.data['email']

        # try:
        user = User.objects.get(username=user_email)
        user.set_password(new_password)
        user.save()
        return Response({"result": "success"})
        # except:
        #     return Response({ "error": "erorr" }, status.HTTP_404_NOT_FOUND)


class ChatUsersAPIVIew(APIView):
    def post(self, request):
        data = request.data['users']
        users = AuthUser.objects.filter(id__in=data)
        return Response(UserGetSerializer(users, many=True).data)


class ChatCarsAPIVIew(APIView):
    def post(self, request):
        data = request.data['cars']
        cars = Generation.objects.filter(generation_id__in=data)
        return Response(ChatGenerationSerializer(cars, many=True).data)


def get_paginated_and_sorted(self, queryset, request, query_key="name"):
    sort = request.query_params.get('sort', None)
    query = request.query_params.get('query', None)
    if query is not None:
        data = {f'{query_key}__contains': query}
        queryset = queryset.filter(**data)
    if sort is not None:
        queryset = queryset.order_by(sort)
    return get_paginated_response(self, queryset)


def get_list(self, request, key, query_key="name"):
    id = request.query_params.get(key, None)
    queryset = self.get_queryset()
    if id is not None:
        data = {key: id}
        queryset = queryset.filter(**data)

    return get_paginated_and_sorted(self, queryset, request, query_key)


class GenerationViewSet(viewsets.ModelViewSet):
    queryset = Generation.objects.all()
    serializer_class = GenerationSerializer

    def get_serializer_class(self):
        if self.action in ('create', 'patch', 'update'):
            return GenerationCreateUpdateSerializer
        return GenerationSerializer

    def list(self, request, *args, **kwargs):
        return get_list(self, request, 'model')


class BrendViewSet(viewsets.ModelViewSet):
    queryset = Brend.objects.all()
    serializer_class = BrendSerializer

    def get_serializer_class(self):
        if self.action in ('create', 'patch', 'update'):
            return BrendCreateUpdateSerializer
        return BrendSerializer


class EquipmentsViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer

    def get_serializer_class(self):
        if self.action in ('create', 'patch', 'update'):
            return EquipmentCreateUpdateSerializer
        return EquipmentSerializer

    def list(self, request, *args, **kwargs):
        return get_list(self, request, 'generation')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            equipment = Equipment.objects.create(**serializer.validated_data)
            colors = request.data.get('colors', [])
            materials = request.data.get('materials', [])
            for m in materials:
                material = Material.objects.get(code=m)
                InteriorMaterial.objects.create(equipment=equipment, material_code=material)
            for c in colors:
                color = Color.objects.get(code=c)
                EquipmentColor.objects.create(equipment=equipment, color_code=color)

            return Response({"result": "success"}, status=status.HTTP_200_OK)

        return Response({"error": "error"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        current_colors = EquipmentColorSerializerCode(EquipmentColor.objects.filter(equipment=instance), many=True).data
        current_materials = InteriorMaterialCodeSerializer(InteriorMaterial.objects.filter(equipment=instance),
                                                           many=True).data
        colors = request.data.get('colors', [])
        materials = request.data.get('materials', [])
        new_colors = []
        new_materials = []
        deleted_colors = []
        deleted_materials = []



        for c in current_colors:
            if c not in colors:
                deleted_colors.append(c)
        for c in current_materials:
            if c not in materials:
                deleted_materials.append(c)
        for c in colors:
            if c not in current_colors:
                new_colors.append(c)
        for c in materials:
            if c not in current_materials:
                new_materials.append(c)


        for m in new_materials:
            material = Material.objects.get(code=m)
            InteriorMaterial.objects.create(equipment=instance, material_code=material)
        for c in new_colors:
            color = Color.objects.get(code=c)
            EquipmentColor.objects.create(equipment=instance, color_code=color)
        for m in deleted_materials:
            InteriorMaterial.objects.get(equipment=instance, material_code=m).delete()
        for c in deleted_colors:
            EquipmentColor.objects.get(equipment=instance, color_code=c).delete()

        return Response({"result": "success"}, status=status.HTTP_200_OK)


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()


class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action in ('create', 'patch', 'update'):
            return ModelCreateUpdateSerializer
        return ModelSerializer

    def list(self, request, *args, **kwargs):
        return get_list(self, request, 'brend')


class GenerationVariantViewSet(viewsets.ModelViewSet):
    queryset = GenerationVariant.objects.all()
    serializer_class = GenerationVariantSerializer
    photos_manager = PhotosManager(GenerationVariantPhoto, 'generation_variant')

    def get_serializer_class(self):
        if self.action in ('create', 'patch', 'update'):
            return GenerationVaraintCreateUpdateSerializer
        return GenerationVariantSerializer

    def list(self, request, *args, **kwargs):
        return get_list(self, request, 'generation', 'car_body_type_code__ru_name')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = GenerationVariant.objects.create(**serializer.validated_data)
        self.photos_manager.parse_added_and_deleted(request, instance)
        return Response({"result": "success"}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.photos_manager.parse_added_and_deleted(request, instance)
        return Response({"result": "success"}, status=status.HTTP_200_OK)


class ConcreteCarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = ConcreteCarSerializer

    def get_serializer_class(self):
        if self.action in ('create', 'patch', 'update'):
            return ConcreteCarCreateUpdateSerializer
        return ConcreteCarSerializer

    def list(self, request, *args, **kwargs):
        generation_variant = request.query_params.get('generation_variant', None)
        equipment = request.query_params.get('equipment', None)
        generation = request.query_params.get('generation', None)
        queryset = self.get_queryset()

        if generation is not None:
            queryset = queryset.filter(generation_variant__generation=generation)
        if generation_variant is not None:
            queryset = queryset.filter(generation_variant=generation_variant)
        if equipment is not None:
            queryset = queryset.filter(equipment=equipment)

        return get_paginated_and_sorted(self, queryset, request)


def get_list_with_options(self, request, query_key="name"):
    list_type = request.query_params.get('type', None)
    sort = request.query_params.get('sort', None)
    query = request.query_params.get('query', None)
    queryset = self.get_queryset()

    if query is not None:
        data = {f'{query_key}__contains': query}
        queryset = queryset.filter(**data)

    if sort is not None:
        queryset = queryset.order_by(sort)

    page = self.paginate_queryset(queryset)

    if list_type == 'options':
        serializer = self.serializer_option_class
    else:
        serializer = self.serializer_class

    if page is not None:
        serializer = serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    serializer = serializer(queryset, many=True)
    return Response({"results": serializer.data})



def get_list_with_options_for_filters(self, request, queryset, query_key="name"):
    list_type = request.query_params.get('type', None)
    sort = request.query_params.get('sort', None)
    query = request.query_params.get('query', None)

    if query is not None:
        data = {f'{query_key}__contains': query}
        queryset = queryset.filter(**data)

    if sort is not None:
        queryset = queryset.order_by(sort)

    page = self.paginate_queryset(queryset)

    if list_type == 'options':
        serializer = self.serializer_option_class
    else:
        serializer = self.serializer_class

    if page is not None:
        serializer = serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    serializer = serializer(queryset, many=True)
    return Response({"results": serializer.data})


class ProducersViewSet(viewsets.ModelViewSet):
    queryset = Producer.objects.all()
    serializer_class = ProducerSerializer
    serializer_option_class = ProducerOptionSerializer

    def get_serializer_class(self):
        if self.action in ('create', 'patch', 'update'):
            return ProducerCreateUpdateSerializer
        return ProducerSerializer

    def list(self, request, *args, **kwargs):
        return get_list_with_options(self, request)


class EnginesViewSet(viewsets.ModelViewSet):
    queryset = Engine.objects.all()
    serializer_class = EngineSerializer
    serializer_option_class = EngineOptionSerializer

    def get_serializer_class(self):
        if self.action in ('create', 'patch', 'update'):
            return EngineCreateUpdateSerializer
        return EngineSerializer

    def list(self, request, *args, **kwargs):
        filtrator = Filtrator(self.get_queryset(), request.query_params)
        filtrator.filter_by_value('producer_id', 'producer__producer_id')
        filtrator.filter_by_value('type_code', 'type_code__code')

        return get_list_with_options_for_filters(self, request, filtrator.data)


class TransmissionViewSet(viewsets.ModelViewSet):
    queryset = Transmission.objects.all()
    serializer_class = TransmissionSerializer
    serializer_option_class = TransmissionOptionSerializer

    def get_serializer_class(self):
        if self.action in ('create', 'patch', 'update'):
            return TransmissionCreateUpdateSerializer
        return TransmissionSerializer

    def list(self, request, *args, **kwargs):

        filtrator = Filtrator(self.get_queryset(), request.query_params)
        filtrator.filter_by_value('producer_id', 'producer__producer_id')
        filtrator.filter_by_value('type_code', 'type_code__code')

        return get_list_with_options_for_filters(self, request, filtrator.data)


class TestApiView(APIView):
    queryset = Car.objects.all()

    def post(self, request, **kwargs):
        all_keys = (
            'engine', 'car_body_type', 'sit_place', "trank_volume", "to_100", "clearance", "drive", "fuel_consumption",
            "brend")
        min_max_keys = ('price', 'fuel_consumption', 'to_100', 'clearance', 'sit_place', 'trank_volume',)
        multiple_keys = ('car_body_type', 'brend', 'drive')

        accessors = {
            "engine": "equipment__engine__type_code__code",
            "car_body_type": "generation_variant__car_body_type_code__code",
            "sit_place": "generation_variant__car_body_type_code__count_of_sit_places",
            "trank_volume": "max_trunk_volum",
            "to_100": "to_100_acceleration",
            "clearance": "clearence",
            "drive": "equipment__drive_type_code",
            "fuel_consumption": "fuel_consumption",
            "brend": "generation_variant__generation__model__brend__brend_id"
        }

        def exclude_keys(exclude_keys):
            return [key for key in all_keys if key not in exclude_keys]

        def filter_by_keys(keys):
            filtrator = Filtrator(Car.objects.all(), request.data)

            for key in keys:

                if key in min_max_keys:
                    filtrator.filter_by_min_max(key, accessors[key])
                elif key in multiple_keys:
                    filtrator.filter_by_contains(key, accessors[key])
                elif key == 'desire':
                    desires = request.data['desire']
                    cars_reviews = list(TestCarReviewHelpSerializer(Car.objects.all(), many=True).data)
                    for d in desires:
                        cars_reviews = filter(lambda x: x[d] > 3.5, cars_reviews)
                    cars = [x['car_id'] for x in cars_reviews]
                    filtrator.data = filtrator.data.filter(car_id__in=cars)
                else:
                    filtrator.filter_by_value(key, accessors[key])
            return filtrator.data

        query = Car.objects.all()



        high = filter_by_keys(all_keys) \
               | filter_by_keys(exclude_keys(['desire'])) \
                | filter_by_keys(['brend', 'car_body_type', 'engine', 'desire']) \
                | filter_by_keys(exclude_keys(['brend'])) \
                | filter_by_keys(exclude_keys(['desire', 'brend']))

        medium = filter_by_keys(exclude_keys(['fuel_consumption', "trank_volume", "sit_place"])) \
                 | filter_by_keys(['brend', 'car_body_type', 'engine']) \
                 | filter_by_keys(['car_body_type', 'clearance', 'desire'])

        low = filter_by_keys(exclude_keys(['fuel_consumption', "trank_volume", "sit_place", 'desire', 'brend'])) \
              | filter_by_keys(['desire']) \
              | filter_by_keys(['brend', 'car_body_type'])

        # high = filter_by_keys(['brend'])
        #
        #
        # medium =  filter_by_keys(['engine'])
        #
        # low = filter_by_keys(exclude_keys(['fuel_consumption', "trank_volume", "sit_place", 'desire', 'brend'])) \
        #       | filter_by_keys(['drive']) \
        #       | filter_by_keys(['car_body_type'])

        high_cars = high.values_list('car_id').distinct()
        medium_cars = medium.values_list('car_id').distinct()
        low_cars = low.values_list('car_id').distinct()

        low = list(CarTestSerializer(Car.objects.filter(Q(car_id__in=low_cars),~Q(car_id__in=high_cars), ~Q(car_id__in=medium_cars)), many=True, context={"type": 0}).data)
        medium = list(CarTestSerializer(Car.objects.filter(Q(car_id__in=medium_cars), ~Q(car_id__in=high_cars)), many=True, context={"type": 1}).data)
        high = list(CarTestSerializer(Car.objects.filter(car_id__in=high_cars), many=True, context={"type": 2}).data)
        results = high + medium + low

        if 'price' in request.data:
            max_price = request.data['price']['max']
            min_price = request.data['price']['min']
            if max_price is not None:
                results = list(filter(lambda x: x['price']['max'] <= max_price, results))
            # if min_price is not None:
            #     results = list(filter(lambda x: x['price']['min'] >= min_price, results))
        return Response(results)


class MostPopularBrendsAPIVIew(APIView):
    def get(self, request):
        count = int(request.query_params.get('count', 10))
        queryset = PopularBrendSerializer(Brend.objects.all(), many=True).data
        queryset = list(sorted(queryset, key=lambda d: d['count'], reverse=True))[:count]
        return Response(queryset)
