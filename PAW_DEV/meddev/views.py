from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm,  DeviceForm, UserProfileForm, UploadCSVForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from .models import Device, Room, Rental
from datetime import datetime, timedelta
import csv
from django.http import HttpResponse

def homepage(request):
    # template = loader.get_template('home.html')
    context = {}
    return render(request,"home.html",context)

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.success(request, ('There Was An Error Loggin In ...'))
            return redirect('login_user')
    else:
        return render(request,"authenticate/login.html",{})

def logout_user(request):
    logout(request)
    messages.success(request, ('You Were Logged Out'))
    return redirect('home')

def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username,password=password)
            login(request,user)
            messages.success(request,('Registration Succesful'))
            return redirect('home')
        else:
            messages.success(request,('This user is already registered'))
            return redirect('register_user')
    else:
        form = RegisterForm()
    context = {'form':form}
    return render(request,'authenticate/register.html',context)

# create a new device
def devices(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            # Handle regular device form submission
            device_form = DeviceForm(request.POST)
            if device_form.is_valid():
                device_form.save()
                messages.success(request, 'Device added successfully.')
                return redirect('devices')
            else:
                messages.error(request, 'Form is not valid. Please check the data.')
        device_form = DeviceForm()
        room_list = Room.objects.all()
        device_list = Device.objects.all()
        context_dict = {
            'devices': device_list,
            'device_form': device_form,
            'room_list': room_list,
        }
        return render(request, 'devices.html', context_dict)
    else:
        messages.error(request, 'You are not authenticated. Please log in.')
        return redirect('home')

def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({'message': 'Please upload a CSV file.'}, status=400)
        
        try:
            devices_created = 0
            devices_updated = 0
            devices_skipped = 0
            
            # Process CSV file
            csv_data = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(csv_data)
            header = next(reader)  # Skip header
            
            for row in reader:
                if len(row) < 5:
                    devices_skipped += 1
                    continue
                
                name = row[0]
                num_used = int(row[1])
                max_uses = int(row[2])
                available = bool(int(row[3]))  # Convert to boolean
                description = row[4]
                
                # Check if device already exists by name
                device, created = Device.objects.update_or_create(
                    name=name,
                    defaults={
                        'num_used': num_used,
                        'max_uses': max_uses,
                        'available': available,
                        'description': description,
                    }
                )
                
                if created:
                    devices_created += 1
                else:
                    devices_updated += 1
            
            return JsonResponse({
                'message': f'CSV upload successful. Created: {devices_created}, Updated: {devices_updated}, Skipped: {devices_skipped}.'
            })
        
        except Exception as e:
            return JsonResponse({'message': f'Error processing CSV file: {e}'}, status=500)
    
    else:
        return JsonResponse({'message': 'No CSV file found.'}, status=400)

def delete_device(request, device_id):
    device = get_object_or_404(Device, pk=device_id)
    if request.method == 'POST':
        device.delete()
        return redirect('devices')  
    else:
        pass

def borrow_device(request, device_id):
    device = get_object_or_404(Device, pk=device_id)
    rooms = Room.objects.all()  
    
    if request.method == 'POST':
        room_id = request.POST.get('room')
        room = get_object_or_404(Room, pk=room_id)
        user = request.user
        return_time = datetime.now() + timedelta(days=1)  

        rental = Rental.objects.create(
            room_id=room,
            device_id=device,
            user_id=user,
            return_time=return_time
        )
        device.available = False
        device.save()

        return redirect('devices') 
    else:
        pass

@login_required
def user_devices(request):
    if request.method == "POST":
        pass
    else:
        user_rentals = Rental.objects.filter(user_id=request.user).select_related('device_id', 'room_id')
        user_devices = [{'device': rental.device_id, 'return_time': rental.return_time} for rental in user_rentals]
        context_dict = {'user_devices': user_devices}
        return render(request, 'user_devices.html', context_dict)
    
@login_required
def return_device(request, device_id):
    rental = get_object_or_404(Rental, device_id=device_id, user_id=request.user)
    
    device = rental.device_id
    device.num_used += 1
    device.available = True
    device.save()
    rental.delete()
    messages.success(request, 'Device returned successfully.')
    return redirect('user_devices')

def autoclave_device(request, device_id):
    device = get_object_or_404(Device, pk=device_id)
    if request.method == 'POST':
        device.num_used = 0
        device.save()
        messages.success(request, f'Device {device.name} has been autoclaved and usage count reset.')
        return redirect('devices')
    else:
        pass

@login_required
def user_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('user_profile')
        else:
            messages.success(request, 'User with this username or email already exists')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=user)
    
    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'user_profile.html', context)

@login_required
def search_results(request):
    query = request.GET.get('q')
    devices = Device.objects.filter(name__icontains=query) if query else []
    rooms = Room.objects.filter(room_number__icontains=query) if query else []
    rentals = Rental.objects.filter(device_id__name__icontains=query) if query else []
    room_list = Room.objects.all()
    
    context = {
        'query': query,
        'devices': devices,
        'rooms': rooms,
        'rentals': rentals,
        'room_list': room_list,
    }
    return render(request, 'search_results.html', context)

def export_devices_csv(request):
    # Tworzenie odpowiedzi HTTP z odpowiednim typem nagłówka
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="devices.csv"'
    response.write('\ufeff'.encode('utf8'))
    # Tworzenie obiektu writer do pisania do pliku CSV
    writer = csv.writer(response)
    writer.writerow(['Name', 'Num Used', 'Max Uses', 'Available', 'Description'])

    # Pobieranie wszystkich urządzeń i zapisywanie ich w pliku CSV
    devices = Device.objects.all()
    for device in devices:
        writer.writerow([device.name, device.num_used, device.max_uses, device.available, device.description])

    return response

# def upload_csv(request):
#     if request.method == 'POST':
#         form = UploadCSVForm(request.POST, request.FILES)
#         if form.is_valid():
#             csv_file = request.FILES['csv_file']
#             decoded_file = csv_file.read().decode('utf-8').splitlines()
#             reader = csv.DictReader(decoded_file)
#             try:
#                 for row in reader:
#                     Device.objects.create(
#                         name=row['Name'],
#                         num_used=row['Num Used'],
#                         max_uses=row['Max Uses'],
#                         available=row['Available'].lower() == 'true',
#                         description=row['Description']
#                     )
#                 return JsonResponse({'message': 'Devices imported successfully.'}, status=200)
#             except Exception as e:
#                 return JsonResponse({'error': f'Error processing CSV file: {e}'}, status=500)
#         else:
#             return JsonResponse({'error': 'Invalid form submission.'}, status=400)

#     form = UploadCSVForm()
#     return render(request, 'devices.html', {'form': form})


