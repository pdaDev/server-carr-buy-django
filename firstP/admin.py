from django.contrib import admin
from .models import Engine, EngineType, FuelType, Producer, Brend,\
    Tag, CarClass, Model, Advertisement, City, Generation, Equipment, \
    EcologicalClass, BoostType, EnginePowerSystem, EngineLayout, Area,\
    Region, Country, Car, CyllinderArrangement, \
    SuspensionType, BreakType, TransmissionType, Transmission, CarDrive, \
    Status, CarBodyType, Price, FavouriteAdvertisement


admin.site.register(Engine)
admin.site.register(FavouriteAdvertisement)
admin.site.register(EngineType)
admin.site.register(FuelType)
admin.site.register(Producer)
admin.site.register(Brend)
admin.site.register(Tag)
admin.site.register(CarClass)
admin.site.register(Model)
admin.site.register(Advertisement)
admin.site.register(City)
admin.site.register(Generation)
admin.site.register(Equipment)
admin.site.register(EcologicalClass)
admin.site.register(BoostType)
admin.site.register(EnginePowerSystem)
admin.site.register(EngineLayout)
admin.site.register(Area)
admin.site.register(Region)
admin.site.register(Car)
admin.site.register(Country)
admin.site.register(CyllinderArrangement)
admin.site.register(SuspensionType)
admin.site.register(BreakType)
admin.site.register(Transmission)
admin.site.register(TransmissionType)
admin.site.register(CarDrive)
admin.site.register(Status)
admin.site.register(CarBodyType)
admin.site.register(Price)