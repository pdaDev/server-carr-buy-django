import base64

from django.db.models import Q, Avg, F
from rest_framework import serializers
from .models import *
from django.db.models import Avg, Max, Min
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer

mock_photos = [
    'https://i.trse.ru/2018/11/30b8b9a9554e6e763c7cfcbadfa7a9e6.jpg',
    'https://kuznitsaspb.ru/wp-content/uploads/6/3/e/63e69cf6a03b2922ba6473c6059ef3e1.jpeg',
    'https://carsweek.ru/upload/uf/2b9/2b90865ed370edc30d410e41c8f59e00.jpg',
    'https://1gai.ru/uploads/posts/2015-05/1432580276_16.jpg',
    'https://i.trse.ru/2018/10/c4ca4238a0b923820dcc509a6f75849b-13.jpg',
    'https://kuznitsaspb.ru/wp-content/uploads/6/b/6/6b67dcc5fcf14751abb44d54e0fb8e78.jpeg',
    'https://img3.akspic.ru/attachments/originals/7/4/6/5/35647-bmw-lichnyj_roskoshnyj_avtomobil-sportivnyj_avtomobil-sportkar-predstavitelskij_avtomobil-3000x2000.jpg',
]


class AdminUsersSerializer(serializers.ModelSerializer):
    total_ads = serializers.SerializerMethodField()
    closed_ads = serializers.SerializerMethodField()
    opened_ads = serializers.SerializerMethodField()
    booked_ads = serializers.SerializerMethodField()
    class Meta:
        model = AuthUser
        fields = ('is_banned', "first_name", "id", "last_name",
                  "last_login", "email", "username", 'date_joined',
                  'total_ads', 'closed_ads', 'booked_ads', 'opened_ads'
                  )
    def get_total_ads(self, obj):
        return Advertisement.objects.filter(owner__id=obj.id).count()

    def get_opened_ads(self, obj):
        return Advertisement.objects.filter(owner__id=obj.id,  status_code__code='O').count()
    def get_booked_ads(self, obj):
        return Advertisement.objects.filter(owner__id=obj.id, status_code__code='B').count()
    def get_closed_ads(self, obj):
        return Advertisement.objects.filter(owner__id=obj.id,  status_code__code='F').count()







class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'


class ModelOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ('model_id', 'name')


class GenerationOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = ('generation_id', 'name')


class AdressSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=10, allow_null=False)
    name = serializers.CharField(max_length=50, allow_null=False)
    guid = serializers.CharField(max_length=36, allow_null=False)


class EquipmentOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ('equipment_id', 'name')


class CarBodyTypesOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationVariant

    def to_representation(self, instance):
        return CarBodyTypeSerializer(instance.car_body_type_code).data


class CarColorOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentColor

    def to_representation(self, instance):
        return ColorSerializer(instance.color_code).data


class CarSearchInfoSerializer(serializers.ModelSerializer):
    colors = serializers.SerializerMethodField()
    generation = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = ('colors', 'generation', 'price')

    def get_colors(self, obj):
        # data = EquipmentColor.objects.filter(equipment=obj.equipment)
        # return CarColorOptionsSerializer(data, many=True).data
        return ColorSerializer(Color.objects.all(), many=True).data

    def get_generation(self, obj):
        return {
            "start_date": obj.equipment.generation.start_date,
            "end_date": obj.equipment.generation.end_date
        }

    def get_price(self, obj):
        prices = Price.objects.filter(advertisement__car=obj)
        try:
            min_price = CarPriceSerializer(prices.earliest('price')).get_only_price()
            max_price = CarPriceSerializer(prices.latest('price')).get_only_price()
        except:
            min_price = None
            max_price = None
        return {
            "min": min_price,
            "max": max_price
        }


class ProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"



class CarBodyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBodyType
        fields = '__all__'
class EngineTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngineType
        fields = '__all__'
class CyllinderArrangementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CyllinderArrangement
        fields = '__all__'
class EnginePowerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnginePowerSystem
        fields = '__all__'
class BoostTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoostType
        fields = '__all__'
class CarClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarClass
        fields = '__all__'
class EngineLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngineLayout
        fields = '__all__'
class FuelTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FuelType
        fields = '__all__'
class EcologicalClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcologicalClass
        fields = '__all__'
class CarDriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarDrive
        fields = '__all__'
class TransmissionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransmissionType
        fields = '__all__'
class SuspensionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspensionType
        fields = '__all__'
class BreakTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakType
        fields = '__all__'
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'



class HandbookCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=12)

    def to_representation(self, instance):
        return instance.code

class HandbookSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=12)
    ru_name = serializers.CharField(max_length=100)
    ru_description = serializers.CharField(max_length=500, allow_null=True, allow_blank=True)
    eng_name = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    eng_description = serializers.CharField(max_length=500, allow_null=True, allow_blank=True)

    def get_short_name(self):
        return {
            "ru_name": self.data['ru_name'],
            "eng_name": self.data['eng_name'],
        }

    def get_code(self):
        return self.data['code']

class BrendSerializer(serializers.ModelSerializer):
    producer = ProducerSerializer()
    class Meta:
        model = Brend
        fields = '__all__'

class CarPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'

    def get_only_price(self):
        return self.data['price']


class EngineSerializerWithNameProducer(serializers.ModelSerializer):
    fuel_type_code = HandbookSerializer(read_only=True)
    power_system_type_code = HandbookSerializer(read_only=True)
    type_code = HandbookSerializer(read_only=True)
    cyllinder_arrangement_type_code = HandbookSerializer(read_only=True)
    boost_type_code = HandbookSerializer(read_only=True)
    producer = serializers.SerializerMethodField()

    class Meta:
        model = Engine
        fields = (
            'volume', 'horse_power', 'type_code', 'name', 'torgue', 'fuel_type_code', 'cyllinder_arrangement_type_code',
            'count_of_cyllinders', 'count_of_clapans_on_cyllinder', 'boost_type_code', 'power_system_type_code',
            'compression_ration', 'engine_id',
            'cyllinder_diameter', 'producer', 'count_of_electro_engines', 'electro_horse_powers')

    def get_producer(self, obj):
        return obj.producer.name


class EngineSerializer(serializers.ModelSerializer):
    fuel_type_code = HandbookSerializer(read_only=True)
    power_system_type_code = HandbookSerializer(read_only=True)
    type_code = HandbookSerializer(read_only=True)
    cyllinder_arrangement_type_code = HandbookSerializer(read_only=True)
    boost_type_code = HandbookSerializer(read_only=True)
    producer = ProducerSerializer(read_only=True)

    class Meta:
        model = Engine
        fields = (
        'volume', 'horse_power', 'type_code', 'name', 'torgue', 'fuel_type_code', 'cyllinder_arrangement_type_code',
        'count_of_cyllinders', 'count_of_clapans_on_cyllinder', 'boost_type_code', 'power_system_type_code',
        'compression_ration', 'engine_id',
        'cyllinder_diameter', 'producer', 'count_of_electro_engines', 'electro_horse_powers')



    # def to_representation(self, instance):
    #     rep = super(EngineSerializer, self).to_representation(instance)
    #     rep['type'] = instance.type.name
    #     rep['fuel_type'] = instance.fuel_type.name
    #     return rep


class AdvertisementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = ('color', 'mileage', 'owners_count', 'in_taxi', 'date_of_production', 'description')





class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = '__all__'

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'

# class ColorSerializer(serializers.Serializer):
#     code = serializers.CharField(max_length=12)
#     ru_name = serializers.CharField(max_length=100)
#     eng_name = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
#     color = serializers.CharField(max_length=25)


class AdvertisementStatusSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=12)
    ru_name = serializers.CharField(max_length=100)
    eng_name = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)

class TransmissionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransmissionType
        fields = '__all__'

class TransmissionSerializer(serializers.ModelSerializer):
    type_code = HandbookSerializer(read_only=True)
    producer = serializers.SerializerMethodField()
    class Meta:
        model = Transmission
        fields = ('__all__')
    def get_producer(self, obj):
        return {
            "name": obj.producer.name,
            "id": obj.producer.producer_id        }






class ModelSerializer(serializers.ModelSerializer):
    # brend = BrendSerializer(read_only=True)
    car_class_code = HandbookSerializer(read_only=True)

    class Meta:
        model = Model
        fields = '__all__'


class ProducerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = ('producer_id', 'name')


class TransmissionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transmission
        fields = ('transmission_id', 'name')


class EngineOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Engine
        fields = ('engine_id', 'name')


class GenerationVariantSerializer(serializers.ModelSerializer):
    photos = serializers.SerializerMethodField()
    car_body_type_code = CarBodyTypeSerializer(read_only=True)

    class Meta:
        model = GenerationVariant
        fields = '__all__'

    def get_photos(self, obj):
        return PhotoRetrieveSerializer(GenerationVariantPhoto.objects.filter(generation_variant_id=obj.generation_variant_id), many=True).data

class GenerationSerializer(serializers.ModelSerializer):
    # model = ModelSerializer(read_only=True)
    ecological_class_code = HandbookSerializer(read_only=True)
    engine_layout_code = HandbookSerializer(read_only=True)

    class Meta:
        model = Generation
        fields = '__all__'


class EquipmentColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentColor
        fields = '__all__'

    def to_representation(self, instance):
        return ColorSerializer(instance.color_code).data


class ConcreteCarSerializer(serializers.ModelSerializer):
    car_body_type = serializers.SerializerMethodField()
    equipment = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = '__all__'

    def get_equipment(self, obj):
        return {
            "id": obj.equipment.equipment_id,
            "name": obj.equipment.name
        }

    def get_car_body_type(self, obj):
        return CarBodyTypeSerializer(obj.generation_variant.car_body_type_code).data


class InteriorMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteriorMaterial
        fields = '__all__'

    def to_representation(self, instance):
        return HandbookSerializer(instance.material_code).data

class EquipmentSerializer(serializers.ModelSerializer):
    # generation = GenerationSerializer(read_only=True)
    engine = serializers.SerializerMethodField()
    transmission = serializers.SerializerMethodField()
    drive_type_code = HandbookSerializer(read_only=True)
    front_suspension_code = HandbookSerializer(read_only=True)
    front_breaks_code = HandbookSerializer(read_only=True)
    colors = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()

    def get_colors(self, obj):
        return EquipmentColorSerializer(EquipmentColor.objects.filter(equipment=obj), many=True).data

    def get_materials(self, obj):
        return InteriorMaterialSerializer(InteriorMaterial.objects.filter(equipment=obj), many=True).data

    def get_transmission(self, obj):
        return {
            "id": obj.transmission.transmission_id,
            "name": obj.transmission.name,
            "type": HandbookSerializer(obj.transmission.type_code).data
        }

    def get_engine(self, obj):
        engine = obj.engine

        return {
            "id": engine.engine_id,
            "fuel": HandbookSerializer(engine.fuel_type_code).get_short_name(),
            "volume": engine.volume,
            "hp": engine.horse_power,
            "type": HandbookSerializer(engine.type_code).get_short_name(),
        }


    class Meta:
        model = Equipment
        fields = "__all__"


class EquipmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = "__all__"

    def to_representation(self, instance):
        return {
            "id": instance.equipment_id,
            "name": instance.name
        }


class CarFullNameSerializer(serializers.ModelSerializer):
    model = serializers.SerializerMethodField()
    brend = serializers.SerializerMethodField()
    generation = serializers.SerializerMethodField()

    class Meta:
        model = Generation
        fields = ('model', 'brend', 'generation')

    def get_model(self, obj):
        return {
            "id": obj.model.model_id,
            "name": obj.model.name
        }

    def get_generation(self, obj):
        return {
            "id": obj.generation_id,
            "name": obj.name,
            "start": obj.start_date,
            "end": obj.end_date
        }

    def get_brend(self, obj):
        return {
            "id": obj.model.brend.brend_id,
            "name": obj.model.brend.name
        }


class CarCharacteristicsSerializer(serializers.ModelSerializer):
    equipments = serializers.SerializerMethodField()
    info = serializers.SerializerMethodField()
    car = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = ('equipments', 'info', 'car', 'equipment')

    def get_equipments(self, obj):
        generation = obj.equipment.generation
        return EquipmentListSerializer(Equipment.objects.filter(generation=generation), many=True).data

    def get_full_name(self, obj):
        return CarFullNameSerializer(obj.equipment.generation).data

    def get_car(self, car):
        return self.get_full_name(car)

    def get_info(self, car):
        equipment = car.equipment
        generation = equipment.generation
        model = generation.model
        engine = equipment.engine
        transmission = equipment.transmission
        return {
            "common": {
                "car_class": HandbookSerializer(model.car_class_code).get_code(),
                "doors_count": car.generation_variant.car_body_type_code.count_of_doors,
                "places_count": car.generation_variant.car_body_type_code.count_of_sit_places,
                "car_body_type": HandbookSerializer(car.generation_variant.car_body_type_code).data
            },
            "sizes": {
                "length": car.length,
                "width": car.width,
                "height": car.height,
                "clearance": car.clearence,
                "wheel_size": equipment.wheel_size
            },
            "volume_and_weight": {
                "trunk_volume": f"{car.min_trunk_volume}/{car.max_trunk_volum}",
                "fuel_tank_volume": car.fuel_trunk_volume,
                "weight": car.weight
            },
            "transmission": {
                "type": HandbookSerializer(transmission.type_code).data,
                "count_of_gears": transmission.count_of_gears,
                "drive_type": HandbookSerializer(equipment.drive_type_code).data
            },
            "suspension_and_breaks": {
                # "front_suspension": HandbookSerializer(equipment.front_suspension_code).data,
                "front_breaks": HandbookSerializer(equipment.front_breaks_code).data,
            },
            "performance_indicators": {
                "max_speed": car.max_speed,
                "fuel_consumption": car.fuel_consumption,
                "fuel": HandbookSerializer(engine.fuel_type_code).data,
                "ecological_class": HandbookSerializer(generation.ecological_class_code).data,
                "acceleration": car.to_100_acceleration
            },
            "engine": EngineSerializerWithNameProducer(engine).data
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('password', 'email', 'username', 'first_name', 'last_name')

    def save(self):
        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name']
        )
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class UserGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuthUser
        fields = ("id", "first_name", "last_name", "avatar", "phone_number",
                  "email", "date_joined", "active", "is_superuser", 'is_banned')



    def get_short_info(self):
        return {
            "id": self.data['id'],
            "first_name": self.data["first_name"],
            "last_name": self.data["last_name"],
            "avatar": self.data["avatar"],
        }

class AnotherUserRetrieveSerializer(serializers.ModelSerializer):
    advertisements = serializers.SerializerMethodField()
    class Meta:
        model = AuthUser
        fields = ("id", "first_name", "last_name", "avatar", "phone_number",
                  "email", "date_joined", "advertisements")

    def get_advertisements(self, obj):
        ads = Advertisement.objects.filter(owner=obj.id, status_code='O')
        return AdvertisementListSerializer(ads, many=True).data


class AdvertisementCreatePatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = "__all__"


class AdvertisementRetrieveSerializer(serializers.ModelSerializer):
    owner = UserGetSerializer(read_only=True)
    photos = serializers.SerializerMethodField()
    car_characteristics = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()
    review = serializers.SerializerMethodField()
    color = ColorSerializer(read_only=True)
    status_code = StatusSerializer(read_only=True)

    class Meta:
        model = Advertisement
        fields = ("advertisement_id", "color", "mileage", "in_taxi", "date_of_production",
                  "start_date", "owner", "description", "car_characteristics", "photos", "name", "price", "rate",
                  "review", "car_id", "status_code")

    def get_photos(self, obj):
        return PhotoRetrieveSerializer(AdvertisementCarPhotos.objects.filter(advertisement=obj), many=True).data

    def get_name(self, obj):
        return CarSerializer().get_name_with_id(obj.car)

    def get_review(self, obj):
        model = obj.car.equipment.generation.model
        try:
            review = Review.objects.filter(car__equipment__generation__model=model, owner=obj.owner).latest("date")
            return ReviewRetrieveSerializer(review).data
        except:
            return None

    def get_rate(self, obj):
        model = obj.car.equipment.generation.model
        reviews = ReviewListSerializer(Review.objects.filter(car__equipment__generation__model=model), many=True).data
        total = 0

        for review in reviews:
            total += review['score']
        return None if total == 0 else round(total / len(reviews), 2)

    def get_price(self, obj):
        prices = Price.objects.filter(advertisement=obj.advertisement_id)
        return {
            "prices": CarPriceSerializer(prices, many=True).data,
            "latest": CarPriceSerializer(prices.latest('date')).get_only_price()
        }

    def get_car_characteristics(self, obj):
        engine = obj.car.equipment.engine

        return {
            "drive": HandbookSerializer(obj.car.equipment.drive_type_code).data,
            "engine": {
                "fuel": HandbookSerializer(engine.boost_type_code).data,
                "volume": engine.volume,
                "hp": engine.horse_power
            },
            "car_body_type": CarBodyTypeSerializer(obj.car.generation_variant.car_body_type_code).data,
            "transmission": HandbookSerializer(obj.car.equipment.transmission.type_code).data
        }


class AdvertisementListSerializer(serializers.ModelSerializer):
    # car = CarSerializer(read_only=True)
    name = serializers.SerializerMethodField()
    car_body_type = serializers.SerializerMethodField()
    engine = serializers.SerializerMethodField()
    transmission = serializers.SerializerMethodField()
    drive = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    status_code = HandbookSerializer()
    address = serializers.SerializerMethodField()
    equipment_name = serializers.SerializerMethodField()

    class Meta:
        model = Advertisement
        fields = ("date_of_production", "in_taxi", "mileage", "name",
                  "car_body_type", "engine", "transmission", "drive",
                  "advertisement_id", "photos", "price", "start_date",
                  "owner", 'status_code', 'address', 'equipment_name')

    def get_equipment_name(self, obj):
        return obj.car.equipment.name
    def get_address(self, obj):
        if obj.adress is not None:
            return AdressSerializer(obj.adress).data
        return None

    def get_status(self, obj):
        return StatusSerializer(obj.status_code).get_code()

    def get_photos(self, obj):
        return PhotoListSerializer(AdvertisementCarPhotos.objects.filter(advertisement=obj), many=True).data

    def get_owner(self, obj):
        return UserGetSerializer(obj.owner).get_short_info()

    def get_price(self, obj):
        models = Price.objects.filter(advertisement_id=obj.advertisement_id)
        max_date = models.latest('date').date
        model = models.filter(date=max_date)[0].price

        return model

    def get_transmission(self, obj):
        return HandbookSerializer(obj.car.equipment.transmission.type_code).get_short_name()

    def get_drive(self, obj):
        return HandbookSerializer(obj.car.equipment.drive_type_code).get_short_name()

    def get_engine(self, obj):
        engine = obj.car.equipment.engine

        return {
            "fuel": HandbookSerializer(engine.type_code).get_short_name(),
            "volume": engine.volume,
            "hp": engine.horse_power
        }

    def get_name(self, obj):
        return CarSerializer().get_name(obj.car)

    def get_car_body_type(self, obj):
        cbt = obj.car.generation_variant.car_body_type_code
        return {
            "ru_name": cbt.ru_name,
            "eng_name": cbt.eng_name
        }


class HistoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteAdvertisement
        fields = "__all__"

    def to_representation(self, instance):
        return AdvertisementListSerializer(instance.advertisement).data


class AdvertisementFavouritesGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteAdvertisement
        fields = "__all__"

    def to_representation(self, instance):
        return AdvertisementListSerializer(instance.advertsment).data


class HistoryRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = "__all__"


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = "__all__"

    def to_representation(self, instance):
        return AdvertisementListSerializer(instance.advertisement).data['advertisement_id']


class AdvertisementFavouritesGetIdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouriteAdvertisement
        fields = "__all__"

    def to_representation(self, instance):
        return AdvertisementListSerializer(instance.advertsment).data['advertisement_id']


class ReviewListSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    car = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ("title", "date", "score", "message", "photos", "owner", "review_id", "car")

    def get_message(self, obj):
        return obj.message[:200] + '...'

    def get_car(self, obj):
        return CarFullNameSerializer(obj.car).data

    def get_score(self, obj):
        points = (obj.comfort_point, obj.reliable_point, obj.contrallabilty_point,
                  obj.safety_point, obj.economic_point, obj.cross_country_point)
        existed_points = list(filter(lambda x: x is not None, points))
        average = 0
        for point in existed_points:
            average += point
        return round(average / len(existed_points), 1)

    def get_photos(self, obj):
        return PhotoListSerializer(ReviewPhoto.objects.filter(review=obj), many=True).data

    def get_owner(self, obj):
        return UserGetSerializer(obj.owner).get_short_info()

    # def to_representation(self, instance):
    #     re


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

    def get_name(self, obj):
        return {
            "brend": obj.equipment.generation.model.brend.name,
            "model": obj.equipment.generation.model.name,
            "generation": obj.equipment.generation.name,
        }

    def get_name_with_id(self, obj):
        return {
            "brend": {
                "id": obj.equipment.generation.model.brend.brend_id,
                "name": obj.equipment.generation.model.brend.name
            },
            "model": {
                "id": obj.equipment.generation.model.model_id,
                "name": obj.equipment.generation.model.name
            },
            "generation": {
                "id": obj.equipment.generation.generation_id,
                "name": obj.equipment.generation.name
            },
            "generation_variant": obj.generation_variant.generation_variant_id
        }



class PhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField()

    def to_representation(self, instance):
        return instance.photo

class PhotoSerializerURL(serializers.ModelSerializer):
    class Meta:
        model = GenerationVariantPhoto
        fields = '__all__'


class BrendModelsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = '__all__'

    def to_representation(self, instance):
        photo_instance = GenerationVariantPhoto.objects.filter(
            generation_variant__generation__model=instance
        ).first()
        if photo_instance:
            photo = PhotoSerializerURL(photo_instance).data['photo']
        else:
            photo = None



        return {
            "id": instance.model_id,
            "advertisement_count": Advertisement.objects.filter(
                car__equipment__generation__model=instance.model_id).count(),
            "name": instance.name,
            "photo": photo
        }


class CarBrendRetrieveSerializer(serializers.ModelSerializer):
    models = serializers.SerializerMethodField()
    producer = ProducerSerializer(read_only=True)

    class Meta:
        model = Brend
        fields = '__all__'



    def get_models(self, obj):
        return BrendModelsListSerializer(Model.objects.filter(brend_id=obj.brend_id), many=True).data


class ModelGenerationVariantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationVariant,
        fields = '__all__'

    def to_representation(self, instance):
        try:
            photo = PhotoSerializerURL(GenerationVariantPhoto.objects.get(generation_variant=instance)).data['photo']
        except:
            photo = None
        return {
            "id": instance.generation_variant_id,
            "photo": photo,
            "car_body_type": CarBodyTypeSerializer(instance.car_body_type_code).data
        }

class CompareItemIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compare
        fields = ("type", "compare_item_id")
    def to_representation(self, instance):
        return instance.compare_item_id

class CompareItemsIdsSerialiazer(serializers.ModelSerializer):
    class Meta:
        model = Compare
        fields = ("type", "compare_item_id")


class AdvertisementCompareCharacteristicsSerializer(serializers.Serializer):
    def get(self, ad):
        common_data = CarCharacteristicsSerializer().get_info(ad.car)
        return {
            **common_data,
            "common": {
                **common_data['common'],
                "mileage": ad.mileage,
                "date_of_production": ad.date_of_production
            }
        }


class ModelCompareCharacteristicsSerializer(serializers.Serializer):
    def get(self, car):
        return CarCharacteristicsSerializer().get_info(car)


class CompareModelCarSerializer(serializers.ModelSerializer):
    car = serializers.SerializerMethodField()
    characteristics = serializers.SerializerMethodField()
    equipment = serializers.SerializerMethodField()
    class Meta:
        model = Car
        fields = ('car', 'characteristics', 'equipment')
    def get_car(self, obj):
        return CarSerializer().get_name_with_id(obj)
    def get_characteristics(self, obj):
        return CarCharacteristicsSerializer().get_info(obj)
    def get_equipment(self, obj):
        equipments = EquipmentListSerializer(Equipment.objects.filter(generation=obj.equipment.generation), many=True).data
        return {
            "equipments": equipments,
            "current": obj.equipment_id
        }


class CompareModelSerializer(serializers.ModelSerializer):
    photos = serializers.SerializerMethodField()
    class Meta:
        model = Compare
        fields = ("id", "compare_item_id", "type", "photos")

    def get_photos(self, obj):
        return PhotoListSerializer(GenerationVariantPhoto.objects.filter(generation_variant_id=obj.compare_item_id), many=True).data

class ReviewPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("comfort_point", "reliable_point", "contrallabilty_point",
                  "safety_point", "economic_point", "cross_country_point")

class TestCarReviewHelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = "__all__"

    def to_representation(self, instance):
        points = ("comfort_point", "reliable_point", "contrallabilty_point",
                  "safety_point", "economic_point", "cross_country_point")
        result = {}
        query = Review.objects.filter(car=instance.equipment.generation)
        count = query.count()
        query = list(ReviewPointsSerializer(query, many=True).data)
        for point in points:
            result[point] = 0
            if count > 0:
                for r in query:
                    result[point] = result[point] + r[point]
                result[point] = result[point] / count
        result['car_id'] = instance.car_id
        return result



class CompareAdvertisementSerializer(serializers.ModelSerializer):
    car = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    characteristics = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    average_price = serializers.SerializerMethodField()
    rate = serializers.SerializerMethodField()


    class Meta:
        model = Compare
        fields = ("id", "compare_item_id", "type", "car", "photos", "characteristics", "rate", 'price', 'owner', 'average_price')

    def get_rate(self, obj):
        car = Advertisement.objects.get(advertisement_id=obj.compare_item_id).car.generation_variant.generation

        reviews = ReviewListSerializer(Review.objects.filter(car=car), many=True).data
        total = 0

        for review in reviews:
            total += review['score']
        return None if total == 0 else round(total / len(reviews), 2)

    def get_average_price(self, obj):
        mileage_dispersion_radius = 20000
        date_of_production_dispersion_radius = 3
        advertisement = Advertisement.objects.get(advertisement_id=obj.compare_item_id)
        mileage = advertisement.mileage
        date_of_production = advertisement.date_of_production
        car = advertisement.car
        mileage_range = (max(0,  mileage - mileage_dispersion_radius), mileage + mileage_dispersion_radius)
        date_of_production_range = (date_of_production - date_of_production_dispersion_radius, date_of_production + date_of_production_dispersion_radius )
        prices = Price.objects.filter(advertisement__car=car,
                                      advertisement__date_of_production=date_of_production,
                                      advertisement__mileage__in=mileage_range)
        if prices.count() == 0:
            prices = Price.objects.filter(advertisement__car=car,
                                          advertisement__date_of_production__in=date_of_production_range)
        if prices.count() == 0:
            prices = Price.objects.filter(advertisement__car=car)

        return prices.aggregate(Avg('price'))['price__avg']


    def get_owner(self, obj):
        ad = Advertisement.objects.get(advertisement_id=obj.compare_item_id)
        return UserGetSerializer(ad.owner).data

    def get_price(self, obj):
        return Price.objects.filter(advertisement_id=obj.compare_item_id).latest('date').price

    def get_car(self, obj):
        car = Advertisement.objects.get(advertisement_id=obj.compare_item_id).car
        return CarSerializer().get_name_with_id(car)

    def get_photos(self, obj):
        ad = Advertisement.objects.get(advertisement_id=obj.compare_item_id)
        return PhotoListSerializer(AdvertisementCarPhotos.objects.filter(advertisement=ad), many=True).data

    def get_characteristics(self, obj):
        ad = Advertisement.objects.get(advertisement_id=obj.compare_item_id)
        return AdvertisementCompareCharacteristicsSerializer().get(ad)


class ModelGenerationsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = "__all__"

    def to_representation(self, instance):
        return {
            "id": instance.generation_id,
            "name": instance.name,
            "end_date": instance.end_date,
            "start_date": instance.start_date,
            "variants": ModelGenerationVariantListSerializer(
                GenerationVariant.objects.filter(generation_id=instance.generation_id), many=True).data
        }




def get_min_max_price(fk, obj):
    data = {fk: obj}

    prices = Price.objects.filter(**data)

    try:
        min_price = CarPriceSerializer(prices.earliest('price')).get_only_price()
        max_price = CarPriceSerializer(prices.latest('price')).get_only_price()
    except:
        min_price = None
        max_price = None

    return {
        "min": min_price,
        "max": max_price
    }

class CarModelRetrieveSerializer(serializers.ModelSerializer):
    car = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    generations = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    advertisements = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Model
        fields = ('car', 'photos', 'generations', 'reviews', 'advertisements', 'price')

    def get_photos(self, obj):
        return PhotoListSerializer(GenerationVariantPhoto.objects.filter(generation_variant__generation__model=obj), many=True).data
    def get_generations(self, obj):
        return ModelGenerationsListSerializer(Generation.objects.filter(model=obj.model_id).order_by('end_date'), many=True).data
    def get_car(self, obj):
        return {
            "model": {
                "id": obj.model_id,
                "name": obj.name
            },
            "brend": {
                "id": obj.brend.brend_id,
                "name": obj.brend.name
            }
        }


    def get_reviews(self, obj):
        list = Review.objects.filter(car__model=obj)
        data = ReviewListSerializer(list[:6], many=True).data

        return {
            "count": list.count(),
            "results": data
        }

    def get_price(self, obj):
        return get_min_max_price('advertisement__car__equipment__generation__model', obj)

    def get_advertisements(self, obj):
        list = Advertisement.objects.filter(car__generation_variant__generation__model=obj)
        data = AdvertisementListSerializer(list[:6], many=True).data
        return {
            "count": list.count(),
            "results": data
        }


class EquipmentListEnginesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'
    def to_representation(self, instance):
        return EngineSerializer(instance).data

class CarGenerationRetrieveSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    car = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    characteristics = serializers.SerializerMethodField()
    advertisements = serializers.SerializerMethodField()

    class Meta:
        model = GenerationVariant
        fields = "__all__"

    def get_advertisements(self, obj):
        list = Advertisement.objects.filter(car__generation_variant=obj)
        data = AdvertisementListSerializer(list[:6], many=True).data
        return {
            "count": list.count(),
            "results": data
        }

    def get_car(self, obj):
        return CarCharacteristicsSerializer().get_full_name(
            Car.objects.filter(equipment__generation=obj.generation_id).first())

    def get_photos(self, obj):
        return PhotoListSerializer(
                GenerationVariantPhoto.objects.filter(generation_variant=obj),
                                       many=True).data
    def get_characteristics(self, obj):
        generation = obj.generation
        equipements = EquipmentSerializer(Equipment.objects.filter(generation=generation), many=True).data

        return {
            "equipments": equipements,
            "car_body_type": CarBodyTypeSerializer(obj.car_body_type_code).data,
            "class": CarClassSerializer(obj.generation.model.car_class_code).data
        }

    def get_price(self, obj):
        prices = Price.objects.filter(advertisement__car__equipment__generation=obj.generation_id)
        try:
            min_price = CarPriceSerializer(prices.earliest('price')).get_only_price()
            max_price = CarPriceSerializer(prices.latest('price')).get_only_price()
        except:
            min_price = None
            max_price = None

        return {
            "min": min_price,
            "max": max_price
        }

    def get_reviews(self, obj):
        list = Review.objects.filter(car=obj.generation)
        reviews = ReviewListSerializer(list, many=True).data
        total = 0
        for review in reviews:
            total += review['score']
        rate = None if total == 0 else round(total / len(reviews), 2)

        return {
            "count": list.count(),
            "results": reviews[:6],
            "rate": rate
        }


class PhotoRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewPhoto
        fields = ('photo', 'id')


class PhotoListSerializer(serializers.Serializer):
    class Meta:
        model = ReviewPhoto
        fields = ('photo', 'id')

    def to_representation(self, instance):
        return PhotoRetrieveSerializer(instance).data['photo']


class ReviewRetrieveSerializer(serializers.ModelSerializer):
    score_point = serializers.SerializerMethodField()
    car = serializers.SerializerMethodField()
    other_reviews = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('title', 'date', 'review_id', 'owner', 'car', 'message', 'score_point', 'other_reviews', 'photos')

    def get_owner(self, obj):
        return UserGetSerializer(obj.owner).get_short_info()

    def get_photos(self, obj):
        try:
            photos = PhotoRetrieveSerializer(ReviewPhoto.objects.filter(review=obj), many=True).data
        except:
            photos = []

        return photos

    def get_score_point(self, obj):
        points = (obj.comfort_point, obj.reliable_point, obj.contrallabilty_point,
                  obj.safety_point, obj.economic_point, obj.cross_country_point)
        existed_points = list(filter(lambda x: x is not None, points))
        average = 0
        for point in existed_points:
            average += point
        return {
            "comfort_point": obj.comfort_point,
            "reliable_point": obj.reliable_point,
            "contrallabilty_point": obj.contrallabilty_point,
            "safety_point": obj.safety_point,
            "economic_point": obj.economic_point,
            "cross_country_point": obj.cross_country_point,
            "total": round(average / len(existed_points), 1)
        }

    def get_other_reviews(self, obj):
        list = Review.objects.filter(Q(car=obj.car), ~Q(review_id=obj.review_id))
        data = ReviewListSerializer(list[:6], many=True).data

        return {
            "count": list.count(),
            "results": data
        }
    def get_car(selfs, obj):
        return CarFullNameSerializer(obj.car).data




class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("message", "comfort_point", "reliable_point", "contrallabilty_point",
                  "safety_point", "economic_point", "cross_country_point", "title"
                  )

    def validate(self, obj):
        points = (obj['comfort_point'], obj['reliable_point'], obj['contrallabilty_point'],
                  obj['safety_point'], obj['economic_point'], obj['cross_country_point'])
        existed_points = list(filter(lambda x: x is not None, points))
        for point in existed_points:
            if point > 5:
                raise serializers.ValidationError("point must be less 5")
        return obj


class FavouritesUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = FavouriteAdvertisement
        fields = '__all__'

    def to_representation(self, instance):
        seriazlizer = UserGetSerializer(instance.user)
        return {
            "email": seriazlizer.data['email'],
            "name": f"{seriazlizer.data['last_name']} {seriazlizer.data['first_name']}"
        }


class GenerationVariantOptionsSerializer(serializers.ModelSerializer):
    car_body_type_code = CarBodyTypeSerializer(read_only=True)

    class Meta:
        model = GenerationVariant
        fields = ('generation_variant_id', 'car_body_type_code')


class ChatGenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation

    def to_representation(self, instance):
        return {
            "generation": {
                "id": instance.generation_id,
                "name": instance.name
            },
            "model": {
                "id": instance.model.model_id,
                "name": instance.model.name
            },
            "brend": {
                "id": instance.model.brend.brend_id,
                "name": instance.model.brend.name
            }
        }


class ProducerCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producer
        fields = '__all__'


class TransmissionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transmission
        fields = '__all__'


class EngineCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Engine
        fields = '__all__'


class BrendCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brend
        fields = '__all__'


class ModelCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = '__all__'


class GenerationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Generation
        fields = '__all__'


class EquipmentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'


class GenerationVaraintCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationVariant
        fields = '__all__'


class ConcreteCarCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'




class EquipmentColorSerializerCode(serializers.ModelSerializer):
    class Meta:
        model = EquipmentColor
        fields = '__all__'

    def to_representation(self, instance):
        return instance.color_code.code


class InteriorMaterialCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteriorMaterial
        fields = '__all__'

    def to_representation(self, instance):
        return instance.material_code.code

class GenerationVarGen(serializers.ModelSerializer):
    class Meta:
        model = GenerationVariant
        fields = ('generation', )


class CarTestSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    equipment = serializers.SerializerMethodField()
    car_body_type = serializers.SerializerMethodField()
    match_status = serializers.SerializerMethodField()
    class Meta:
        model = Car
        fields = ('name', 'car_id', 'price', 'photos', 'equipment', 'car_body_type', 'match_status')

    def get_match_status(self, obj):
        return self.context.get("type")

    def get_equipment(self, obj):
        return obj.equipment.name

    def get_car_body_type(self, obj):
        return CarBodyTypeSerializer(obj.generation_variant.car_body_type_code).data
    def get_name(self, obj):
        return CarSerializer().get_name_with_id(obj)

    def get_photos(self, obj):
        return PhotoListSerializer(
            GenerationVariantPhoto.objects.filter(generation_variant=obj.generation_variant),
            many=True).data
    def get_price(self, obj):
        prices = Price.objects.filter(advertisement__car__equipment__generation=obj.generation_variant.generation_id)
        try:
            min_price = CarPriceSerializer(prices.earliest('price')).get_only_price()
            max_price = CarPriceSerializer(prices.latest('price')).get_only_price()
        except:
            min_price = None
            max_price = None

        return {
            "min": min_price,
            "max": max_price
        }


class PopularBrendSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    class Meta:
        model = Brend
        fields = '__all__'
    def get_count(self, obj):
        return Advertisement.objects.filter(car__generation_variant__generation__model__brend=obj, status_code='O').count()