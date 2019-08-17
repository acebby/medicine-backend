from django.shortcuts import render

from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Doctor, Patient, Medicine
from .serializers import DoctorSerializer, PatientSerializer, MedicineSerializer

from google.cloud import vision

import os
import re
import io

from functools import reduce

from ImageUpload.models import UploadedImage

# Create your views here.

@api_view(['GET', 'POST'])
def doc_list(request):
    if request.method == 'GET':
        all_docs            = Doctor.objects.all()
        all_serialized_docs = DoctorSerializer(all_docs, many=True)
        return Response(all_serialized_docs.data)
    elif request.method == 'POST':
        print(request.data)
        serializer = DoctorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'DELETE'])
def single_doc(request, pk):
    try:
        sampleItem = Doctor.objects.get(pk=pk)
    except Doctor.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = DoctorSerializer(sampleItem)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        sampleItem.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'POST'])
def patient_list(request):
    if request.method == 'GET':
        all_docs            = Patient.objects.all()
        all_serialized_docs = PatientSerializer(all_docs, many=True)
        return Response(all_serialized_docs.data)
    elif request.method == 'POST':
        print(request.data)
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'DELETE'])
def single_patient(request, pk):
    try:
        sampleItem = Patient.objects.get(pk=pk)
    except Patient.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PatientSerializer(sampleItem)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        sampleItem.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'POST'])
def medicine_list(request):
    if request.method == 'GET':
        all_docs            = Medicine.objects.all()
        all_serialized_docs = MedicineSerializer(all_docs, many=True)
        return Response(all_serialized_docs.data)
    elif request.method == 'POST':
        print(request.data)
        serializer = MedicineSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # all_docs            = Medicine.objects.all()
                # all_serialized_docs = MedicineSerializer(all_docs, many=True)
                # print(all_serialized_docs.data)

                all_docs = Medicine.objects.get(name = request.data['name'])
                print(all_docs)
                print("LOL\n\n\n\n\nLOL")
                print(serializer)
                print("LOL\n\n\n\n\nLOL")
                
                all_docs.name = request.data['name']
                print(all_docs)
                all_docs.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
                
            except Medicine.DoesNotExist:
                # if(serializer not in all_serialized_docs.data):
                
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                # else:
            #     print("LOL")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

client = vision.ImageAnnotatorClient()

@api_view(['GET'])
def med_info(request, pk):
    if request.method == 'GET':
        try:
            img = UploadedImage.objects.get(pk=pk)
        except UploadedImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        image_name = str(img.image)
        with io.open(os.path.join('media/', image_name), 'rb') as img_file:
            content = img_file.read()
        image = vision.types.Image(content=content)
        res = client.text_detection(image=image)
        #text = pytesseract.image_to_string(os.path.join('media/', image_name))
        text = res.text_annotations[0].description
        print(text)
        all_list_of_words = re.split(' |, |\*|\n', text)
        # filter_meds = Medicine.objects.none()
        print(all_list_of_words)

        list_of_words = []
        avg_word_len = sum(map(len, all_list_of_words))/len(all_list_of_words)
        for word in all_list_of_words:
            if len(word) >= avg_word_len:
                list_of_words.append(word)

        print(list_of_words)
        filter_meds = Medicine.objects.filter(reduce(lambda x, y: x | y, [Q(name__icontains=word) for word in list_of_words]))
        print(filter_meds)
        if filter_meds.exists():
            serial_filter_meds = MedicineSerializer(filter_meds, many=True)
            return Response(serial_filter_meds.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

def doc_site(request):
    return render(request, 'Doctor_website/index.html')

def assign_prescription(request):
    return render(request, 'Doctor_website/single-blog.html')