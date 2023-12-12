from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.serializers import average_buySerializer,transactionSerializer
from api.models import average_buy,company,transaction
import datetime
# Create your views here.

def get_company_id(company_name):
    companies=company.objects.all()
    for i in companies:
        if i.company_name==company_name:
            company_id=i.id
            return company_id
    return None

@api_view(['POST'])
def transaction(request):
    company_id=get_company_id(request.data['company'])
    if company_id is None:
        return Response({"error":"compnay does not exist"})

    if request.data['trade_type']!='SELL' and request.data['trade_type']!='BUY' and 'SPLIT' not in request.data['trade_type']:
        return Response({"error":"Check Trade Type"})
    try:
        if 'SPLIT' in request.data['trade_type']:
            int(request.data['trade_type'].split()[-1].split(':')[-1])
    except Exception as e:
        return Response({"error":"Check SPLIT Trade type format"})

    if request.data['trade_type']=='SELL':
        all_records=average_buy.objects.filter(company=company_id).order_by('-date').values()
        if len(all_records)>0:
            if all_records[0]['balance_quantity']>=request.data['quantity']:
                pass
            else:
                return Response({"error":"Sell Quantity more than buy quantity"})
        else:
            return Response({"error":"Sell Quantity more than buy quantity"})
    
    request.data['company']=company_id
    serializer=transactionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors)

@api_view(['POST'])
def get_details(request):
    date=request.data['date']
    company_id=get_company_id(request.data['company'])
    if company_id is None:
        return Response({"error":"compnay does not exist"})
    python_date=datetime.datetime.strptime(date,'%Y-%m-%d').date()
    all_records=average_buy.objects.filter(company=company_id).order_by('-date').values()

    if len(all_records)!=0:
        for i in all_records:
            if python_date>=i['date']:
                filter_date=i['date']
                break
        date_data=average_buy.objects.filter(company=company_id,date=filter_date)
        serializer=average_buySerializer(date_data,many=True)
        serializer.data[0]['date']=date
        return Response(serializer.data)
    else:
        return Response({"Error":"No Data Available"})

