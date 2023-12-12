from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class company(models.Model):
    company_name=models.CharField(max_length=255)
    def __str__(self) -> str:
        return self.company_name

class transaction(models.Model):
    date=models.DateField()
    company=models.ForeignKey(company,on_delete=models.CASCADE)
    trade_type=models.CharField(max_length=255)
    quantity=models.IntegerField()
    price=models.FloatField()
    balance_quantity=models.IntegerField(blank=True,null=True)

class average_buy(models.Model):
    date=models.DateField()
    company=models.ForeignKey(company,on_delete=models.CASCADE)
    average_price=models.FloatField()
    balance_quantity=models.IntegerField()


@receiver(post_save,sender=transaction)
def transaction_post_save(sender,instance,created,*args,**kwargs):
    
    if instance.trade_type=='BUY':
        obj=transaction.objects.filter(company=instance.company,trade_type__in= ['BUY','SELL'])
        if len(obj)==1:
            instance.balance_quantity=instance.quantity
            transaction.objects.filter(pk=instance.id).update(balance_quantity=instance.balance_quantity)
            average_price=instance.price
            entry=average_buy(date=instance.date,company=instance.company,average_price=round(average_price,2),balance_quantity=instance.balance_quantity)
            entry.save()

        else:
            all_records=average_buy.objects.filter(company=instance.company).order_by('-date').values()
            current_balance=all_records[0]['balance_quantity']
            instance.balance_quantity=current_balance+instance.quantity
            transaction.objects.filter(pk=instance.id).update(balance_quantity=instance.balance_quantity)
            ##avg price update
            obj=transaction.objects.filter(company=instance.company)
            sold_quantity=0
            for i in obj:
                if 'SPLIT' in i.trade_type:
                    split=int(i.trade_type.split()[-1].split(':')[-1])
                    sold_quantity=sold_quantity*split
                elif i.trade_type=='SELL':
                    sold_quantity=sold_quantity+i.quantity
            lst_price=[]
            lst_quantity=[]
            split=1

            for i in reversed(obj):
                if 'SPLIT' in i.trade_type:
                    transaction_split=int(i.trade_type.split()[-1].split(':')[-1])
                    split=transaction_split*split
                elif i.trade_type=='BUY':
                    if sold_quantity>=i.quantity*split:
                        sold_quantity=sold_quantity-i.quantity*split
                    else:
                        holding_quantity=i.quantity*split-sold_quantity
                        lst_price.append(i.price/split)
                        lst_quantity.append(holding_quantity)
            total_price=0
            for i in range(len(lst_quantity)):
                total_price=total_price+(lst_quantity[i]*lst_price[i])
            if sum(lst_quantity)==0:
                average_price=0
            else:
                average_price=total_price/sum(lst_quantity)
            

            average_buy_obj=average_buy.objects.filter(date=instance.date,company=instance.company)
            if len(average_buy_obj)!=0:
                average_buy.objects.filter(date=instance.date).update(average_price=round(average_price,2))
                average_buy.objects.filter(date=instance.date).update(balance_quantity=instance.balance_quantity)
            else:
                entry=average_buy(date=instance.date,company=instance.company,average_price=round(average_price,2),balance_quantity=instance.balance_quantity)
                entry.save()
            
        

    
    elif instance.trade_type=='SELL':
        obj=transaction.objects.filter(company=instance.company,trade_type__in=['BUY','SELL'])
        all_records=average_buy.objects.filter(company=instance.company).order_by('-date').values()
        current_balance=all_records[0]['balance_quantity']
        instance.balance_quantity=current_balance-instance.quantity
        transaction.objects.filter(pk=instance.id).update(balance_quantity=instance.balance_quantity)
        ##avg price update
        obj=transaction.objects.filter(company=instance.company)
        sold_quantity=0
        for i in obj:
            if 'SPLIT' in i.trade_type:
                split=int(i.trade_type.split()[-1].split(':')[-1])
                sold_quantity=sold_quantity*split
            elif i.trade_type=='SELL':
                sold_quantity=sold_quantity+i.quantity
        lst_price=[]
        lst_quantity=[]
        split=1

        for i in reversed(obj):
            if 'SPLIT' in i.trade_type:
                transaction_split=int(i.trade_type.split()[-1].split(':')[-1])
                split=transaction_split*split
            elif i.trade_type=='BUY':
                if sold_quantity>=i.quantity*split:
                    sold_quantity=sold_quantity-i.quantity*split
                else:
                    holding_quantity=i.quantity*split-sold_quantity
                    lst_price.append(i.price/split)
                    lst_quantity.append(holding_quantity)
        total_price=0
        for i in range(len(lst_quantity)):
            total_price=total_price+(lst_quantity[i]*lst_price[i])
        if sum(lst_quantity)==0:
            average_price=0
        else:
            average_price=total_price/sum(lst_quantity)
        

        average_buy_obj=average_buy.objects.filter(date=instance.date,company=instance.company)
        if len(average_buy_obj)!=0:
            average_buy.objects.filter(date=instance.date).update(average_price=round(average_price,2))
            average_buy.objects.filter(date=instance.date).update(balance_quantity=instance.balance_quantity)
        else:
            entry=average_buy(date=instance.date,company=instance.company,average_price=round(average_price,2),balance_quantity=instance.balance_quantity)
            entry.save()
    
    
    elif 'SPLIT' in instance.trade_type:
        obj=transaction.objects.filter(company=instance.company)
        if len(obj)>1:
            split=int(instance.trade_type.split()[-1].split(':')[-1])
            average_buy_obj=average_buy.objects.filter(date=instance.date,company=instance.company)
            if len(average_buy_obj)!=0:
                for i in average_buy_obj:
                    average_buy.objects.filter(date=instance.date).update(average_price=round((i.average_price)/split,2))
                    average_buy.objects.filter(date=instance.date).update(balance_quantity=round((i.balance_quantity)*split,2))
            else:
                all_records=average_buy.objects.order_by('-date').values()
                average_price=all_records[0]['average_price']/split
                balance_quantity=all_records[0]['balance_quantity']*split
                entry=average_buy(date=instance.date,company=instance.company,average_price=round(average_price,2),balance_quantity=balance_quantity)
                entry.save()







