from django.contrib import admin
from .models import Device, Room, Rental

# Register your models here.

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_used', 'max_uses', 'available', 'description')
    search_fields = ('name', 'description')
    list_filter = ('available',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'description')
    search_fields = ('room_number', 'description')
    list_filter = ('room_number',)

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'device_name', 'user_id', 'return_time')
    search_fields = ('room_id__room_number', 'device_id__name', 'user_id__username')
    list_filter = ('return_time',)