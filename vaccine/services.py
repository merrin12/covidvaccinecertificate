import requests
def get_list():
    request_header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "origin": "https://selfregistration.cowin.gov.in",
        "referer": "https://selfregistration.cowin.gov.in/",
    }
    beneficiaries = requests.get("https://cdn-api.co-vin.in/api/v2/appointment/beneficiaries", headers=request_header)
    if beneficiaries.status_code == 200:
        beneficiaries = beneficiaries.json()["beneficiaries"]
        beneficiaryl=[]
        for i in range(len(beneficiaries['beneficiaries'])):
            beneficiaryl.append(beneficiaries[beneficiaries][i])
        return beneficiaryl