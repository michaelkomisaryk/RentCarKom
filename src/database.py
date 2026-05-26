import json
import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path
DB_PATH =Path (__file__ ).parent .parent /'data'/'db.json'
ASSETS_PATH =Path (__file__ ).parent .parent /'assets'/'cars'
_DEFAULT_USERS =[{'id':'u-admin-001','name':'Admin','email':'admin@rentcarkom.com','password':'Admin123!','role':'admin','created_at':'2024-01-01T00:00:00'},{'id':'u-manager-001','name':'Manager','email':'manager@rentcarkom.com','password':'Manager123!','role':'manager','created_at':'2024-01-01T00:00:00'}]
_DEFAULT_CARS =[{'id':'car-001','brand':'Toyota','model':'Camry','year':2022 ,'price':45 ,'seats':5 ,'transmission':'Automatic','fuel':'Gasoline','plate':'AA 1234 KK','color':'White','mileage':32000 ,'description':'Comfortable mid-size sedan, perfect for city and highway driving.','photos':[],'is_rented':False ,'added_by':'admin@rentcarkom.com','rating':4.6 ,'created_at':'2024-06-15T10:00:00','is_premium':False },{'id':'car-002','brand':'BMW','model':'3 Series','year':2023 ,'price':95 ,'seats':5 ,'transmission':'Automatic','fuel':'Gasoline','plate':'BB 5678 KK','color':'Black','mileage':12000 ,'description':'Premium executive sedan with sporty handling and luxury interior.','photos':[],'is_rented':False ,'added_by':'admin@rentcarkom.com','rating':4.9 ,'created_at':'2025-01-10T12:00:00','is_premium':True },{'id':'car-003','brand':'Ford','model':'Explorer','year':2022 ,'price':75 ,'seats':7 ,'transmission':'Automatic','fuel':'Gasoline','plate':'CC 9012 KK','color':'Silver','mileage':28000 ,'description':'Spacious SUV ideal for family trips and off-road adventures.','photos':[],'is_rented':False ,'added_by':'admin@rentcarkom.com','rating':4.3 ,'created_at':'2024-03-20T08:00:00','is_premium':False },{'id':'car-004','brand':'Mercedes','model':'E-Class','year':2023 ,'price':110 ,'seats':5 ,'transmission':'Automatic','fuel':'Diesel','plate':'DD 3456 KK','color':'Gray','mileage':8000 ,'description':'Elegant luxury sedan with cutting-edge technology and supreme comfort.','photos':[],'is_rented':False ,'added_by':'admin@rentcarkom.com','rating':4.8 ,'created_at':'2025-02-01T14:00:00','is_premium':True },{'id':'car-005','brand':'Volkswagen','model':'Passat','year':2021 ,'price':50 ,'seats':5 ,'transmission':'Manual','fuel':'Diesel','plate':'EE 7890 KK','color':'Blue','mileage':55000 ,'description':'Reliable and fuel-efficient family sedan with generous trunk space.','photos':[],'is_rented':False ,'added_by':'admin@rentcarkom.com','rating':4.1 ,'created_at':'2023-11-05T09:00:00','is_premium':False },{'id':'car-006','brand':'Hyundai','model':'Tucson','year':2023 ,'price':60 ,'seats':5 ,'transmission':'Automatic','fuel':'Hybrid','plate':'FF 1122 KK','color':'Red','mileage':15000 ,'description':'Modern compact SUV with advanced safety features and hybrid efficiency.','photos':[],'is_rented':False ,'added_by':'admin@rentcarkom.com','rating':4.5 ,'created_at':'2024-09-12T11:00:00','is_premium':False },{'id':'car-007','brand':'Audi','model':'A4','year':2022 ,'price':88 ,'seats':5 ,'transmission':'Automatic','fuel':'Gasoline','plate':'GG 3344 KK','color':'Dark Blue','mileage':21000 ,'description':'Sporty premium sedan with quattro all-wheel drive and refined interior.','photos':[],'is_rented':False ,'added_by':'admin@rentcarkom.com','rating':4.7 ,'created_at':'2024-12-01T16:00:00','is_premium':True },{'id':'car-008','brand':'Kia','model':'Sportage','year':2023 ,'price':55 ,'seats':5 ,'transmission':'Automatic','fuel':'Hybrid','plate':'HH 5566 KK','color':'Green','mileage':9000 ,'description':'Stylish and practical crossover with great value and modern tech.','photos':[],'is_rented':False ,'added_by':'admin@rentcarkom.com','rating':4.4 ,'created_at':'2024-08-22T13:00:00','is_premium':False }]

class DB :
    _data :dict ={}

    @classmethod
    def _load (cls )->dict :
        DB_PATH .parent .mkdir (parents =True ,exist_ok =True )
        if DB_PATH .exists ():
            with open (DB_PATH ,'r',encoding ='utf-8')as f :
                return json .load (f )
        return {'users':list (_DEFAULT_USERS ),'cars':list (_DEFAULT_CARS ),'rentals':[]}

    @classmethod
    def _save (cls ):
        with open (DB_PATH ,'w',encoding ='utf-8')as f :
            json .dump (cls ._data ,f ,ensure_ascii =False ,indent =2 )

    @classmethod
    def init (cls ):
        cls ._data =cls ._load ()
        cls .migrate_photo_paths ()
        cls .migrate_car_metadata ()
        cls ._save ()

    @classmethod
    def migrate_car_metadata (cls ):
        changed =False
        now =datetime .now ().isoformat ()
        for car in cls .get_cars ():
            if 'rating'not in car :
                price =float (car .get ('price',50 ))
                car ['rating']=round (min (5.0 ,3.8 +price /120 ),1 )
                changed =True
            if 'created_at'not in car :
                year =int (car .get ('year',2022 ))
                car ['created_at']=f'{year }-06-01T10:00:00'
                changed =True
            if 'is_premium'not in car :
                car ['is_premium']=float (car .get ('price',0 ))>=85
                changed =True
            if not car .get ('created_at'):
                car ['created_at']=now
                changed =True
        if changed :
            cls ._save ()

    @classmethod
    def _get (cls )->dict :
        if not cls ._data :
            cls .init ()
        return cls ._data

    @classmethod
    def get_users (cls )->list :
        return cls ._get ()['users']

    @classmethod
    def get_user_by_email (cls ,email :str )->dict |None :
        return next ((u for u in cls .get_users ()if u ['email']==email .strip ().lower ()),None )

    @classmethod
    def login (cls ,email :str ,password :str )->dict |None :
        user =cls .get_user_by_email (email .strip ().lower ())
        if user and user ['password']==password :
            return user
        return None

    @classmethod
    def register (cls ,name :str ,email :str ,password :str )->tuple [bool ,str ]:
        from src .auth_validation import validate_registration
        ok ,msg =validate_registration (name ,email ,password )
        if not ok :
            return (False ,msg )
        email =email .strip ().lower ()
        if cls .get_user_by_email (email ):
            return (False ,'Цей email уже зареєстрований.')
        new_user ={'id':f'u-{uuid .uuid4 ().hex [:8 ]}','name':name .strip (),'email':email ,'password':password ,'role':'client','created_at':datetime .now ().isoformat ()}
        cls ._get ()['users'].append (new_user )
        cls ._save ()
        return (True ,'Реєстрація успішна')

    @classmethod
    def get_cars (cls )->list :
        return cls ._get ()['cars']

    @classmethod
    def get_car (cls ,car_id :str )->dict |None :
        return next ((c for c in cls .get_cars ()if c ['id']==car_id ),None )

    @classmethod
    def add_car (cls ,data :dict )->dict :
        car ={'id':f'car-{uuid .uuid4 ().hex [:6 ]}','brand':data .get ('brand',''),'model':data .get ('model',''),'year':int (data .get ('year',2023 )),'price':float (data .get ('price',0 )),'seats':int (data .get ('seats',5 )),'transmission':data .get ('transmission','Automatic'),'fuel':data .get ('fuel','Gasoline'),'plate':data .get ('plate',''),'color':data .get ('color',''),'mileage':int (data .get ('mileage',0 )),'description':data .get ('description',''),'photos':data .get ('photos',[]),'is_rented':False ,'added_by':data .get ('added_by',''),'rating':float (data .get ('rating',4.5 )),'created_at':data .get ('created_at')or datetime .now ().isoformat (),'is_premium':bool (data .get ('is_premium',float (data .get ('price',0 ))>=85 ))}
        cls ._get ()['cars'].append (car )
        cls ._save ()
        return car

    @classmethod
    def update_car (cls ,car_id :str ,fields :dict ):
        cars =cls ._get ()['cars']
        for i ,c in enumerate (cars ):
            if c ['id']==car_id :
                cars [i ].update (fields )
                cls ._save ()
                return True
        return False

    @classmethod
    def delete_car (cls ,car_id :str )->bool :
        data =cls ._get ()
        before =len (data ['cars'])
        data ['cars']=[c for c in data ['cars']if c ['id']!=car_id ]
        if len (data ['cars'])<before :
            cls ._save ()
            return True
        return False

    @classmethod
    def add_photo_to_car (cls ,car_id :str ,src_path :str |None =None ,*,data :bytes |None =None ,filename_hint :str |None =None )->str |None :
        car =cls .get_car (car_id )
        if not car :
            return None
        dest_dir =ASSETS_PATH /car_id
        dest_dir .mkdir (parents =True ,exist_ok =True )
        allowed ={'.jpg','.jpeg','.png','.gif','.webp','.bmp'}
        if data is not None :
            name =filename_hint or 'image.jpg'
            ext =Path (name ).suffix .lower ()or '.jpg'
            if ext not in allowed :
                ext ='.jpg'
            filename =f'{uuid .uuid4 ().hex [:8 ]}{ext }'
            dest =dest_dir /filename
            dest .write_bytes (data )
        elif src_path :
            ext =Path (src_path ).suffix .lower ()or '.jpg'
            if ext not in allowed :
                ext ='.jpg'
            filename =f'{uuid .uuid4 ().hex [:8 ]}{ext }'
            dest =dest_dir /filename
            shutil .copy2 (src_path ,dest )
        else :
            return None
        relative =f'cars/{car_id }/{filename }'
        car ['photos'].append (relative )
        cls ._save ()
        return relative

    @classmethod
    def migrate_photo_paths (cls ):
        changed =False
        for car in cls .get_cars ():
            old =list (car .get ('photos')or [])
            new_photos =[]
            for p in old :
                s =str (p ).replace ('\\','/')
                if s .startswith ('cars/'):
                    new_photos .append (s )
                    continue
                marker ='/cars/'
                if marker in s :
                    new_photos .append ('cars/'+s .split (marker ,1 )[1 ])
                else :
                    new_photos .append (s )
            if new_photos !=old :
                car ['photos']=new_photos
                changed =True
        if changed :
            cls ._save ()

    @classmethod
    def get_rentals (cls )->list :
        return cls ._get ()['rentals']

    @classmethod
    def get_rentals_for_car (cls ,car_id :str )->list :
        return [r for r in cls .get_rentals ()if r ['car_id']==car_id ]

    @classmethod
    def get_rentals_for_user (cls ,user_id :str )->list :
        return [r for r in cls .get_rentals ()if r ['user_id']==user_id ]

    @classmethod
    def create_rental (cls ,car_id :str ,user :dict ,days :int ,renter_name :str ,*,start_date :datetime |None =None ,end_date :datetime |None =None )->tuple [bool ,str ]:
        car =cls .get_car (car_id )
        if not car :
            return (False ,'Car not found')
        if car ['is_rented']:
            return (False ,'Car is already rented')
        now =datetime .now ()
        if start_date is not None and end_date is not None :
            start_day =start_date .date ()if isinstance (start_date ,datetime )else start_date
            end_day =end_date .date ()if isinstance (end_date ,datetime )else end_date
            if end_day <start_day :
                return (False ,'Дата закінчення має бути не раніше дати початку')
            days =(end_day -start_day ).days +1
            start =datetime .combine (start_day ,datetime .min .time ())
            end =datetime .combine (end_day ,datetime .max .time ()).replace (microsecond =0 )
        else :
            if days <1 :
                return (False ,'Rental must be at least 1 day')
            start =now
            end =datetime (now .year ,now .month ,now .day +days -1 ,23 ,59 ,59 )if days >0 else now
        rental ={'id':f'r-{uuid .uuid4 ().hex [:8 ]}','car_id':car_id ,'car_brand':car ['brand'],'car_model':car ['model'],'car_plate':car ['plate'],'user_id':user ['id'],'user_email':user ['email'],'renter_name':renter_name .strip ()or user ['name'],'start_datetime':start .isoformat (),'end_datetime':end .isoformat (),'days':days ,'price_per_day':car ['price'],'total_price':round (car ['price']*days ,2 ),'status':'active','created_at':now .isoformat ()}
        cls ._get ()['rentals'].append (rental )
        cls .update_car (car_id ,{'is_rented':True })
        return (True ,rental ['id'])

    @classmethod
    def complete_rental (cls ,rental_id :str )->bool :
        rentals =cls ._get ()['rentals']
        for r in rentals :
            if r ['id']==rental_id :
                r ['status']='completed'
                r ['end_datetime']=datetime .now ().isoformat ()
                cls .update_car (r ['car_id'],{'is_rented':False })
                cls ._save ()
                return True
        return False

    @classmethod
    def cancel_rental (cls ,rental_id :str )->bool :
        rentals =cls ._get ()['rentals']
        for r in rentals :
            if r ['id']==rental_id :
                r ['status']='cancelled'
                cls .update_car (r ['car_id'],{'is_rented':False })
                cls ._save ()
                return True
        return False
