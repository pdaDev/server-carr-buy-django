# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Advertisement(models.Model):
    advertisement_id = models.PositiveIntegerField(primary_key=True)
    car = models.ForeignKey('Car', models.DO_NOTHING)
    color = models.CharField(max_length=15)
    mileage = models.PositiveIntegerField()
    owners_count = models.PositiveIntegerField(blank=True, null=True)
    in_taxi = models.IntegerField(blank=True, null=True)
    date_of_production = models.DateField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    status_code = models.ForeignKey('Status', models.DO_NOTHING, db_column='status_code')
    owner = models.ForeignKey('AuthUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Advertisement'


class AdvertisementCarPhotos(models.Model):
    advertisement = models.ForeignKey(Advertisement, models.DO_NOTHING)
    photo_url = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'Advertisement_car_photos'


class Area(models.Model):
    area_id = models.SmallAutoField(primary_key=True)
    region = models.ForeignKey('Region', models.DO_NOTHING)
    ru_name = models.CharField(max_length=100)
    eng_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Area'


class BoostType(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Boost_type'


class BreakType(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Break_type'


class Brend(models.Model):
    brend_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    producer = models.ForeignKey('Producer', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Brend'


class Car(models.Model):
    car_id = models.AutoField(primary_key=True)
    length = models.PositiveSmallIntegerField()
    height = models.PositiveSmallIntegerField()
    width = models.PositiveSmallIntegerField()
    wheel_base = models.PositiveSmallIntegerField()
    clearence = models.PositiveSmallIntegerField()
    min_trunk_volume = models.PositiveSmallIntegerField()
    max_trunk_volum = models.PositiveSmallIntegerField()
    fuel_trunk_volume = models.PositiveSmallIntegerField(blank=True, null=True)
    car_body_type_code = models.ForeignKey('CarBodyType', models.DO_NOTHING, db_column='car_body_type_code')
    weight = models.PositiveSmallIntegerField()
    max_speed = models.PositiveSmallIntegerField()
    to_100_acceleration = models.FloatField()
    fuel_consumption = models.FloatField(blank=True, null=True)
    battery_volume = models.PositiveSmallIntegerField(blank=True, null=True)
    equipment = models.ForeignKey('Equipment', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Car'


class CarBodyType(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(max_length=30)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    icon = models.CharField(max_length=200, blank=True, null=True)
    count_of_doors = models.PositiveIntegerField()
    count_of_sit_places = models.PositiveIntegerField()
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Car_body_type'


class CarClass(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Car_class'


class CarDrive(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Car_drive'


class CarPhoto(models.Model):
    car = models.OneToOneField(Car, models.DO_NOTHING, primary_key=True)
    photo_url = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'Car_photo'
        unique_together = (('car', 'photo_url'),)


class CarTag(models.Model):
    car = models.OneToOneField(Car, models.DO_NOTHING, primary_key=True, related_query_name='car_tag')
    tag_code = models.ForeignKey('Tag', models.DO_NOTHING, db_column='tag_code')


    class Meta:
        managed = False
        db_table = 'Car_tag'
        unique_together = (('car', 'tag_code'),)


class City(models.Model):
    city_id = models.SmallAutoField(primary_key=True)
    area = models.ForeignKey(Area, models.DO_NOTHING)
    ru_name = models.CharField(max_length=50)
    eng_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'City'


class Color(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    rgba = models.CharField(max_length=20, blank=True, null=True)
    ru_name = models.CharField(max_length=30)
    hex = models.CharField(max_length=7)
    eng_name = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Color'


class Country(models.Model):
    country_id = models.SmallAutoField(primary_key=True)
    code = models.CharField(max_length=5)
    ru_full_name = models.CharField(max_length=60)
    short_name = models.CharField(max_length=30, blank=True, null=True)
    flag = models.CharField(max_length=200, blank=True, null=True)
    eng_full_name = models.CharField(max_length=60, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Country'


class CyllinderArrangement(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Cyllinder_arrangement'


class EcologicalClass(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Ecological_class'


class Engine(models.Model):
    engine_id = models.AutoField(primary_key=True)
    volume = models.FloatField(blank=True, null=True)
    horse_power = models.PositiveSmallIntegerField(blank=True, null=True)
    type_code = models.ForeignKey('EngineType', models.DO_NOTHING, db_column='type_code')
    name = models.CharField(max_length=100)
    torgue = models.PositiveSmallIntegerField(blank=True, null=True)
    fuel_type_code = models.ForeignKey('FuelType', models.DO_NOTHING, db_column='fuel_type_code')
    cyllinder_arrangement_type_code = models.ForeignKey(CyllinderArrangement, models.DO_NOTHING, db_column='cyllinder_arrangement_type_code', blank=True, null=True)
    count_of_cyllinders = models.PositiveIntegerField(blank=True, null=True)
    count_of_clapans_on_cyllinder = models.PositiveIntegerField(blank=True, null=True)
    boost_type_code = models.ForeignKey(BoostType, models.DO_NOTHING, db_column='boost_type_code', blank=True, null=True)
    power_system_type_code = models.ForeignKey('EnginePowerSystem', models.DO_NOTHING, db_column='power_system_type_code', blank=True, null=True)
    compression_ration = models.PositiveSmallIntegerField(blank=True, null=True)
    cyllinder_diameter = models.FloatField(blank=True, null=True)
    producer = models.ForeignKey('Producer', models.DO_NOTHING, blank=True, null=True)
    count_of_electro_engines = models.PositiveIntegerField(blank=True, null=True)
    electro_horse_powers = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Engine'


class EngineLayout(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Engine_layout'


class EnginePowerSystem(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Engine_power_system'


class EngineType(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Engine_type'


class Equipment(models.Model):
    equipment_id = models.AutoField(primary_key=True)
    engine = models.ForeignKey(Engine, models.DO_NOTHING)
    drive_type_code = models.ForeignKey(CarDrive, models.DO_NOTHING, db_column='drive_type_code')
    wheel_size = models.PositiveIntegerField()
    transmission = models.ForeignKey('Transmission', models.DO_NOTHING)
    front_suspension_code = models.ForeignKey('SuspensionType', models.DO_NOTHING, db_column='front_suspension_code')
    front_breaks_code = models.ForeignKey(BreakType, models.DO_NOTHING, db_column='front_breaks_code')
    model = models.ForeignKey('Model', models.DO_NOTHING)
    generation = models.ForeignKey('Generation', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Equipment'


class EquipmentColor(models.Model):
    equipment = models.OneToOneField(Equipment, models.DO_NOTHING, primary_key=True)
    color_code = models.ForeignKey(Color, models.DO_NOTHING, db_column='color_code')

    class Meta:
        managed = False
        db_table = 'Equipment_color'
        unique_together = (('equipment', 'color_code'),)


class FavouriteAdvertisement(models.Model):
    advertsment = models.OneToOneField(Advertisement, models.DO_NOTHING, primary_key=True)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Favourite_advertisement'
        unique_together = (('advertsment', 'user'),)


class FuelType(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    en_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Fuel_type'


class Generation(models.Model):
    generation_id = models.AutoField(primary_key=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    name = models.CharField(max_length=20)
    engine_layout_code = models.ForeignKey(EngineLayout, models.DO_NOTHING, db_column='engine_layout_code', blank=True, null=True)
    ecological_class_code = models.ForeignKey(EcologicalClass, models.DO_NOTHING, db_column='ecological_class_code', blank=True, null=True)
    model = models.ForeignKey('Model', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Generation'


class InteriorMaterial(models.Model):
    equipment = models.OneToOneField(Equipment, models.DO_NOTHING, primary_key=True)
    material_code = models.ForeignKey('Material', models.DO_NOTHING, db_column='material_code')

    class Meta:
        managed = False
        db_table = 'Interior_material'
        unique_together = (('equipment', 'material_code'),)


class Material(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Material'


class Model(models.Model):
    model_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    car_class_code = models.ForeignKey(CarClass, models.DO_NOTHING, db_column='car_class_code')
    brend = models.ForeignKey(Brend, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Model'


class Price(models.Model):
    advertisement = models.OneToOneField(Advertisement, models.DO_NOTHING, primary_key=True)
    date = models.DateTimeField()
    price = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'Price'
        unique_together = (('advertisement', 'date'),)


class Producer(models.Model):
    producer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    logo = models.CharField(max_length=200, blank=True, null=True)
    date_of_found = models.DateField(blank=True, null=True)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    country = models.ForeignKey(Country, models.DO_NOTHING, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Producer'


class Region(models.Model):
    region_id = models.SmallAutoField(primary_key=True)
    country = models.ForeignKey(Country, models.DO_NOTHING)
    ru_name = models.CharField(max_length=50)
    code = models.PositiveIntegerField()
    eng_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Region'


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=3000, blank=True, null=True)
    date = models.DateField()
    car = models.ForeignKey(Car, models.DO_NOTHING)
    owner = models.ForeignKey('AuthUser', models.DO_NOTHING)
    comfort_point = models.PositiveIntegerField()
    reliable_point = models.PositiveIntegerField()
    contrallabilty_point = models.PositiveIntegerField()
    safety_point = models.PositiveIntegerField()
    economic_point = models.PositiveIntegerField()
    cross_country_point = models.PositiveIntegerField()
    title = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Review'


class ReviewPhoto(models.Model):
    review = models.OneToOneField(Review, models.DO_NOTHING, primary_key=True)
    photo_url = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'Review_photo'
        unique_together = (('review', 'photo_url'),)


class Status(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=30)
    eng_name = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Status'


class SuspensionType(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    eu_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Suspension_type'


class Tag(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    eng_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Tag'


class Transmission(models.Model):
    transmission_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type_code = models.ForeignKey('TransmissionType', models.DO_NOTHING, db_column='type_code')
    count_of_gears = models.PositiveIntegerField()
    count_of_clutches = models.PositiveIntegerField()
    has_dry_clutch = models.IntegerField()
    producer_id = models.PositiveIntegerField()

    class Meta:
        managed = False
        db_table = 'Transmission'


class TransmissionType(models.Model):
    code = models.CharField(primary_key=True, max_length=15)
    ru_name = models.CharField(unique=True, max_length=100)
    ru_description = models.CharField(max_length=500, blank=True, null=True)
    en_name = models.CharField(max_length=100, blank=True, null=True)
    eng_description = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Transmission_type'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
