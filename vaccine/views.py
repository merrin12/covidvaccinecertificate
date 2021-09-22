from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
import os,sys
import requests
import mimetypes
from django.views.generic import TemplateView
from .services import get_list
# Create your views here.
global Id
from wsgiref.util import FileWrapper
from hashlib import sha256

import PyPDF2
from PyPDF2 import PdfFileReader
#from PyPDF2.pdf import PageObject
import fitz
#import cv2
from PIL import Image

def home(request):
    if request.method == 'POST':
        mobile = request.POST['mobile']

        request_header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            "origin": "https://selfregistration.cowin.gov.in",
            "referer": "https://selfregistration.cowin.gov.in/",
        }
        if not mobile:
            print("\n")
            print("Mobile Number cannot be empty. Please Try Again...")
            os.system("pause")
            print("\n")
            sys.exit()
            #messages.error(request,"Mobile Number cannot be empty")
            #return render(request,'formotp.html')


        valid_token = False
        while not valid_token:

            data = {
                    "mobile": mobile,
                    "secret": "U2FsdGVkX1+z/4Nr9nta+2DrVJSv7KS6VoQUSQ1ZXYDx/CJUkWxFYG6P3iM/VW+6jLQ9RDQVzp/RcZ8kbT41xw==",
                    }
            txnId = requests.post(url="https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP", json=data, headers=request_header)

            if txnId.status_code == 200:
                print("\n")
                print("Successfully Requested OTP for the Mobile Number")
                valid_token = True
                Id = txnId.json()["txnId"]
                with open("file.txt","w") as f:
                    f.write(Id)
                return redirect('beneficiarylist/')

            elif txnId.status_code == 400:
                messages.error("Bad Request")
                valid_token = True
                return redirect('/')
            elif txnId.status_code == 401:
                messages.error("Unauthenticated Access")
                valid_token = True
                return redirect('/')
            elif txnId.status_code == 500:
                messages.error("Internal Server Error")
                valid_token = True
                return redirect('/')

    return render(request,'formotp.html');

def beneficiarylist(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        print(otp)
        request_header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            "origin": "https://selfregistration.cowin.gov.in",
            "referer": "https://selfregistration.cowin.gov.in/",
            }
        with open("file.txt","r") as fp:
            Id=fp.read()
        if otp:
            data = {
            "otp": sha256(str(otp).encode("utf-8")).hexdigest(),
            "txnId": Id,
            }
            print(f"Validating OTP. Please Wait...")

            token = requests.post(
                url="https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp",
                json=data,
                headers=request_header,
            )
            if token.status_code == 200:
                token = token.json()["token"]
                with open("tokenfile.txt","w") as f1:
                    f1.write(token)

                #return token
                return redirect('table/')
            elif token.status_code == 400:
                messages.error(request,"Bad Request")
                return redirect('/')
            elif token.status_code == 401:
                messages.error(request,"Unauthenticated Access")
                return redirect('/')
            elif token.status_code == 500:
                messages.error(request,"Internal Server Error")
                return redirect('/')

    return render(request,'formverify.html')


def table(request):
    request_header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "origin": "https://selfregistration.cowin.gov.in",
        "referer": "https://selfregistration.cowin.gov.in/",
    }
    with open("tokenfile.txt","r")as f2:
        token=f2.read()
    request_header["Authorization"] = f"Bearer {token}"
    beneficiaries=requests.get("https://cdn-api.co-vin.in/api/v2/appointment/beneficiaries", headers=request_header)
    print(beneficiaries.status_code)
    beneficiaries = beneficiaries.json()["beneficiaries"]

    return render(request,'table.html',{'beneficiaries':beneficiaries})

def certificatedownload(request,pk):
    request_header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "origin": "https://selfregistration.cowin.gov.in",
        "referer": "https://selfregistration.cowin.gov.in/",
    }

    with open("tokenfile.txt", "r")as f2:
        token = f2.read()
    request_header["Authorization"] = f"Bearer {token}"
    certificate = requests.get(
        f"https://cdn-api.co-vin.in/api/v2/registration/certificate/download?beneficiary_reference_id={pk}",
        headers=request_header)
    print(certificate)
    print(certificate.status_code)
    if certificate.status_code == 200:
        print("Success")
        with open("hello.pdf", "wb") as f:
            f.write(certificate.content)
        input1 = PdfFileReader(open('hello.pdf', 'rb'))
        page1 = input1.getPage(0)
        page1.cropBox.lowerLeft = [0, 275]
        page1.cropBox.upperRight = [600, 820]
        writer = PyPDF2.PdfFileWriter()
        writer.addPage(page1)
        with open("details.pdf", "wb") as file:
            writer.write(file)
            file.close()
        pdffile = "details.pdf"
        doc = fitz.open(pdffile)
        page = doc.loadPage(0)
        pix = page.getPixmap()
        output = "details.jpg"
        pix.writePNG(output)
        input2 = PdfFileReader(open('hello.pdf', 'rb'))
        page2 = input2.getPage(0)
        page2.cropBox.lowerLeft = [352, 27]
        page2.cropBox.upperRight = [584, 260]
        writer = PyPDF2.PdfFileWriter()
        writer.addPage(page2)
        with open("qr.pdf", "wb") as file:
            writer.write(file)
            file.close()

        pdffile = "qr.pdf"
        doc = fitz.open(pdffile)
        page = doc.loadPage(0)  # number of page
        pix = page.getPixmap()
        output = "qr.jpg"
        pix.writePNG(output)
        img = Image.open("qr.jpg", 'r')
        img = img.resize((400, 400))
        img1 = Image.open("details.jpg", 'r')
        img_w, img_h = img.size
        background = Image.new('RGBA', (1062, 576), (255, 255, 255, 255))
        background.paste(img1, (40, 40))
        background.paste(img, (620, 125))
        # background.save('out.png')
        background = background.convert('RGB')
        background.save('final.pdf')

        f = open('final.pdf', "rb")
        response = HttpResponse(FileWrapper(f), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=resume.pdf'
        f.close()
        return response

    elif certificate.status_code == 400:
        messages.error(request,"Bad Request")
    elif certificate.status_code == 401:
        messages.error(request,"Unauthenticated Access")
    elif certificate.status_code == 500:
        messages.error(request,"Internal Server error")

    return render(request,'success.html')
