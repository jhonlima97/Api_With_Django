from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from django.views import View
from .models import Company
import json
import re
from datetime import datetime
from urllib.parse import urlparse

# Class-based view  ---class
# functions-based views   --def
class CompanyView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def validations(self, data):
        errors = {}
        # Validar que no haya campos vacíos
        required_fields = ['name', 'website', 'foundation', 'status']
        for field in required_fields:
            value = data.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors[field] = "Este campo es requerido."
            elif field == 'name' and not re.match("^[a-zA-Z ]*$", value):
                errors['name'] = "El campo 'name' solo debe contener letras y espacios."
                
        # Validar el campo 'website' (URL)
        if 'website' in data:
            try:
                website = data['website']
                result = urlparse(website)
                if not all([result.scheme, result.netloc]):
                    errors['website'] = "El campo 'website' debe ser una URL válida."
            except ValueError:
                errors['website'] = "El campo 'website' debe ser una URL válida."

        # Validar el campo 'foundation' (años)
        if 'foundation' in data:
            try:
                foundation = int(data['foundation'])
                current_year = datetime.now().year
                if not (1900 <= foundation <= current_year):
                    errors['foundation'] = "La 'foundation' debe ser un año entre 1900 y el año actual."
            except ValueError:
                errors['foundation'] = "El campo 'foundation' debe ser un año válido."

        # Validar el campo 'status'
        if 'status' in data:
            try:
                status = bool(data['status'])
            except ValueError:
                errors['status'] = "El campo 'status' debe ser True o False."

        return errors

    # CRUD completo para una API
    def get(self, request, id=None):
        if id is not None:  # Si se proporciona un ID específico
            try:
                id = int(id)
                if not (1 <= id <= 999):
                    return JsonResponse({'message': "El id debe ser un entero de 1 al 999."}, status=406)

                company = Company.objects.get(id=id)
                datos = {'message': "Success", 'company': {
                    'id': company.id, 
                    'name': company.name,
                    'web': company.website, 
                    'status': company.status}}
                return JsonResponse(datos)
            except ValueError:
                return JsonResponse({'message': "El id debe ser entero."}, status=406)
            except Company.DoesNotExist:
                return JsonResponse({'message': "Company not found..."}, status=404)
            except Exception as e:
                return JsonResponse({'message': str(e)}, status=500)
        
        # Si no se proporciona un ID específico o no se puede procesar, devolver todas las empresas
        companies = list(Company.objects.values())
        if len(companies) > 0:
            datos = {'companies': companies}
            return JsonResponse(datos)
        else:
            return JsonResponse({'message': "Companies not found..."}, status=404)

    def post(self, request):
        # Cargar los datos del JSON
        jd = json.loads(request.body)

        # Validar los datos de la compañía
        validation_errors = self.validations(jd)
        if validation_errors:
            return JsonResponse({'errors': validation_errors}, status=400)

        # Crear el objeto Company si todas las validaciones pasan
        try:
            Company.objects.create(name=jd['name'], website=jd['website'], foundation=jd['foundation'], status=jd['status'])
            return JsonResponse({'message': "Company creada exitosamente."}, status=201)
        except Exception as e:
            print(e)  # Imprimir la excepción para depuración
            return JsonResponse({'message': f"No se pudo crear la Company: {str(e)}"}, status=500)
        
    def put(self, request, id): 
        jd = json.loads(request.body.decode('utf-8'))

        # Validar los datos de la compañía
        validation_errors = self.validations(jd)
        if validation_errors:
            return JsonResponse({'errors': validation_errors}, status=400)

        try:
            id = int(id)
        except ValueError:
            return JsonResponse({'message': "El id debe ser entero."}, status=400)

        companies = list(Company.objects.filter(id=id).values())
        if len(companies) > 0:
            company = Company.objects.get(id=id)
            company.name       = jd['name']
            company.website    = jd['website']
            company.foundation = jd['foundation']
            company.status     = jd['status']
            company.save()
            datos = {'message': "Company actualizada exitosamente."}
            return JsonResponse(datos, status=201)
        else:
            return JsonResponse({'message': "Company not found..."}, status=404)
        
    def delete(self, request, id):
        # Validar que el ID es un número entero
        if not str(id).isdigit():
            return JsonResponse({'message': "El ID debe ser un número entero."}, status=400)
        id = int(id)
        if not 1 <= id <= 999:
            return JsonResponse({'message': "El id debe ser un entero de 1 al 999."}, status=406)
        try:
            company = Company.objects.get(id=id)
            company.delete()
            return JsonResponse({'message': "Company eliminada correctamente"}, status=200)
        except Company.DoesNotExist:
            return JsonResponse({'message': "El ID no existe"}, status=404)
