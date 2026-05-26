from datetime import datetime
import flet as ft
from src .database import DB
from src .state import AppState
from src .components .header import build_header
from src .ui_helpers import show_message ,image_src_for_preview ,user_safe_error
_BRANDS =['Toyota','BMW','Mercedes','Audi','Volkswagen','Ford','Hyundai','Kia','Honda','Nissan','Інша']
_COLORS =[('White','Білий',ft .Colors .WHITE ),('Black','Чорний',ft .Colors .BLACK ),('Silver','Срібний',ft .Colors .BLUE_GREY_300 ),('Gray','Сірий',ft .Colors .GREY_600 ),('Blue','Синій',ft .Colors .BLUE_700 ),('Red','Червоний',ft .Colors .RED_700 ),('Green','Зелений',ft .Colors .GREEN_700 )]

def _section (title :str ,*controls )->ft .Column :
    return ft .Column (controls =[ft .Text (title ,size =12 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .BLUE_GREY_600 ),*controls ],spacing =8 )

def _labeled_slider (label :str ,slider :ft .Slider ,value_text :ft .Text )->ft .Column :
    return ft .Column (controls =[ft .Row (controls =[ft .Text (label ,size =13 ,color =ft .Colors .BLUE_GREY_800 ),value_text ],alignment =ft .MainAxisAlignment .SPACE_BETWEEN ),slider ],spacing =4 )

class AddCarView :

    def __init__ (self ,page :ft .Page ):
        self ._page =page
        self ._pending_photos :list [tuple [str |None ,bytes |None ,str ]]=[]
        self ._photo_status_text :ft .Text |None =None
        self ._photo_previews :ft .Row |None =None

    def build (self )->ft .View :
        if not AppState .is_admin ():
            return ft .View (route ='/admin/add-car',controls =[ft .Text ('Доступ заборонено',size =22 ,color =ft .Colors .RED_600 )])
        header =build_header (self ._page ,title ='Нове авто',show_back =True )
        brand_dd =ft .Dropdown (label ='Марка *',options =[ft .DropdownOption (key =b ,text =b )for b in _BRANDS ],value ='Toyota',border_radius =10 ,border_color =ft .Colors .BLUE_GREY_200 )
        brand_custom =ft .TextField (label ='Вкажіть марку',visible =False ,border_radius =10 ,border_color =ft .Colors .BLUE_GREY_200 ,hint_text ='наприклад Lexus')

        def on_brand_change (e ):
            brand_custom .visible =brand_dd .value =='Інша'
            self ._page .update ()
        brand_dd .on_change =on_brand_change
        model =ft .TextField (label ='Модель *',prefix_icon =ft .Icons .CAR_RENTAL ,hint_text ='наприклад Camry',border_radius =10 ,border_color =ft .Colors .BLUE_GREY_200 ,focused_border_color =ft .Colors .DEEP_PURPLE_700 )
        year_display =ft .Text ('2023',size =18 ,weight =ft .FontWeight .W_700 ,color =ft .Colors .DEEP_PURPLE_800 )
        year_picker =ft .DatePicker (value =datetime (2023 ,6 ,1 ),first_date =datetime (1990 ,1 ,1 ),last_date =datetime (datetime .now ().year +1 ,12 ,31 ),date_picker_mode =ft .DatePickerMode .YEAR ,help_text ='Рік випуску авто',confirm_text ='OK',cancel_text ='Скасувати')

        def _year_from_picker (val )->int |None :
            if val is None :
                return None
            if hasattr (val ,'year'):
                return int (val .year )
            return None

        def on_year_picked (e ):
            y =_year_from_picker (year_picker .value )
            if y is not None :
                year_display .value =str (y )
                self ._page .update ()
        year_picker .on_change =on_year_picked
        year_row =ft .Container (content =ft .Row (controls =[ft .OutlinedButton (content =ft .Row (controls =[ft .Icon (ft .Icons .CALENDAR_MONTH ,size =18 ),ft .Text ('Обрати рік',size =13 )],spacing =8 ,tight =True ),on_click =lambda _ :self ._page .show_dialog (year_picker )),year_display ],spacing =16 ,vertical_alignment =ft .CrossAxisAlignment .CENTER ),padding =ft .Padding (12 ,10 ,12 ,10 ),border =ft .Border .all (1 ,ft .Colors .BLUE_GREY_200 ),border_radius =10 )
        price_value =ft .Text ('$50 / день',size =13 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .DEEP_PURPLE_700 )
        price_slider =ft .Slider (min =10 ,max =250 ,divisions =48 ,value =50 ,label ='{value}',on_change =lambda e :self ._update_slider_label (price_value ,f'${int (e .control .value or 0 )} / день'))
        seats_value =ft .Text ('5 місць',size =13 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .DEEP_PURPLE_700 )
        seats_slider =ft .Slider (min =2 ,max =9 ,divisions =7 ,value =5 ,label ='{value}',on_change =lambda e :self ._update_slider_label (seats_value ,f'{int (e .control .value or 0 )} місць'))
        mileage_value =ft .Text ('15 000 км',size =13 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .DEEP_PURPLE_700 )
        mileage_slider =ft .Slider (min =0 ,max =200000 ,divisions =40 ,value =15000 ,label ='{value}',on_change =lambda e :self ._update_slider_label (mileage_value ,f'{int (e .control .value or 0 ):,} км'.replace (',',' ')))
        plate =ft .TextField (label ='Номер *',prefix_icon =ft .Icons .BADGE ,hint_text ='AA 1234 KK',border_radius =10 ,border_color =ft .Colors .BLUE_GREY_200 ,capitalization =ft .TextCapitalization .CHARACTERS )
        color_rg =ft .RadioGroup (value ='White',content =ft .Row (spacing =10 ,run_spacing =8 ,wrap =True ,controls =[ft .Row (controls =[ft .Radio (value =key ,label =label ),ft .Container (width =18 ,height =18 ,bgcolor =swatch ,border_radius =9 ,border =ft .Border .all (1 ,ft .Colors .BLUE_GREY_300 ))],spacing =4 ,tight =True )for key ,label ,swatch in _COLORS ]))
        transmission_rg =ft .RadioGroup (value ='Automatic',content =ft .Row (controls =[ft .Radio (value ='Automatic',label ='Автомат'),ft .Radio (value ='Manual',label ='Механіка')],spacing =24 ))
        fuel_rg =ft .RadioGroup (value ='Gasoline',content =ft .Column (controls =[ft .Row (controls =[ft .Radio (value ='Gasoline',label ='Бензин'),ft .Radio (value ='Diesel',label ='Дизель')],spacing =24 ),ft .Row (controls =[ft .Radio (value ='Hybrid',label ='Гібрид'),ft .Radio (value ='Electric',label ='Електро')],spacing =24 )],spacing =4 ))
        premium_switch =ft .Switch (label ='Преміум клас',value =False ,active_color =ft .Colors .DEEP_PURPLE_700 ,label_text_style =ft .TextStyle (size =13 ,color =ft .Colors .BLUE_GREY_800 ))
        insured_cb =ft .Checkbox (label ='Застраховано',value =True ,label_style =ft .TextStyle (size =13 ,color =ft .Colors .BLUE_GREY_800 ))
        ac_cb =ft .Checkbox (label ='Кондиціонер',value =True ,label_style =ft .TextStyle (size =13 ,color =ft .Colors .BLUE_GREY_800 ))
        description =ft .TextField (label ='Опис',multiline =True ,min_lines =3 ,max_lines =6 ,border_radius =10 ,border_color =ft .Colors .BLUE_GREY_200 )
        error_text =ft .Text ('',color =ft .Colors .RED_600 ,size =13 ,visible =False )
        self ._photo_status_text =ft .Text ('Фото не обрано',size =12 ,color =ft .Colors .BLUE_GREY_500 )
        self ._photo_previews =ft .Row (spacing =8 ,wrap =True )
        file_picker =ft .FilePicker ()

        async def pick_photos (_ ):
            try :
                files =await file_picker .pick_files (dialog_title ='Оберіть фото авто',file_type =ft .FilePickerFileType .IMAGE ,allow_multiple =True ,with_data =True )
            except Exception as ex :
                show_message (self ._page ,user_safe_error (ex ,'Не вдалося відкрити вибір файлів.'),error =True )
                return
            if not files :
                return
            for f in files :
                path ,data ,name =(f .path ,f .bytes ,f .name or 'image.jpg')
                if not path and (not data ):
                    continue
                self ._pending_photos .append ((path ,data ,name ))
                prev =image_src_for_preview (path ,data ,name )
                self ._photo_previews .controls .append (ft .Container (content =ft .Image (src =prev ,width =70 ,height =70 ,fit =ft .BoxFit .COVER ,border_radius =ft .BorderRadius (6 ,6 ,6 ,6 )),border_radius =ft .BorderRadius (6 ,6 ,6 ,6 ),clip_behavior =ft .ClipBehavior .HARD_EDGE ))
            n =len (self ._pending_photos )
            self ._photo_status_text .value =f'Обрано фото: {n }'
            self ._page .update ()
        pick_btn =ft .Button (content =ft .Row (controls =[ft .Icon (ft .Icons .ADD_PHOTO_ALTERNATE ,color =ft .Colors .WHITE ,size =18 ),ft .Text ('Додати фото',color =ft .Colors .WHITE ,size =13 )],spacing =8 ),style =ft .ButtonStyle (bgcolor =ft .Colors .INDIGO_700 ,shape =ft .RoundedRectangleBorder (radius =10 ),padding =ft .Padding (20 ,12 ,20 ,12 )),on_click =pick_photos )

        async def save_car (_ ):
            error_text .visible =False
            errors =[]
            if brand_dd .value =='Інша':
                brand_val =(brand_custom .value or '').strip ()
            else :
                brand_val =(brand_dd .value or '').strip ()
            if not brand_val :
                errors .append ('Вкажіть марку')
            if not model .value or not model .value .strip ():
                errors .append ('Вкажіть модель')
            if not plate .value or not plate .value .strip ():
                errors .append ('Вкажіть номерний знак')
            y =_year_from_picker (year_picker .value )or 0
            try :
                y =int (year_display .value )if not y else y
                if y <1990 or y >datetime .now ().year +1 :
                    raise ValueError
            except (ValueError ,TypeError ):
                errors .append ('Некоректний рік')
            p =float (price_slider .value or 0 )
            if p <=0 :
                errors .append ('Некоректна ціна')
            seats_v =int (seats_slider .value or 5 )
            mileage_v =int (mileage_slider .value or 0 )
            if errors :
                error_text .value ='\n'.join (errors )
                error_text .visible =True
                self ._page .update ()
                return
            extras =[]
            if insured_cb .value :
                extras .append ('застраховано')
            if ac_cb .value :
                extras .append ('кондиціонер')
            desc =(description .value or '').strip ()
            if extras :
                suffix ='Опції: '+', '.join (extras )
                desc =f'{desc }\n{suffix }'.strip ()if desc else suffix
            try :
                car_data ={'brand':brand_val ,'model':model .value .strip (),'year':y ,'price':p ,'seats':seats_v ,'transmission':transmission_rg .value ,'fuel':fuel_rg .value ,'plate':plate .value .strip ().upper (),'color':color_rg .value or 'White','mileage':mileage_v ,'description':desc ,'photos':[],'added_by':AppState .current_user ['email'],'is_premium':bool (premium_switch .value )}
                new_car =DB .add_car (car_data )
                for path ,data ,name in self ._pending_photos :
                    if data is not None :
                        DB .add_photo_to_car (new_car ['id'],data =data ,filename_hint =name )
                    elif path :
                        DB .add_photo_to_car (new_car ['id'],path )
            except Exception as ex :
                show_message (self ._page ,user_safe_error (ex ),error =True )
                return
            show_message (self ._page ,f"Авто «{new_car ['brand']} {new_car ['model']}» збережено.")
            await self ._page .push_route ('/home')
        save_btn =ft .Button (content =ft .Text ('Зберегти',size =15 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .WHITE ),style =ft .ButtonStyle (bgcolor =ft .Colors .DEEP_PURPLE_800 ,shape =ft .RoundedRectangleBorder (radius =10 ),padding =ft .Padding (0 ,14 ,0 ,14 )),expand =True ,on_click =save_car )
        form_card =ft .Container (content =ft .Column (controls =[ft .Text ('Дані авто',size =16 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .BLUE_GREY_900 ),ft .Divider (height =12 ,color =ft .Colors .BLUE_GREY_100 ),_section ('Основне',brand_dd ,brand_custom ,model ),_section ('Рік випуску *',year_row ),_section ('Ціна та місткість',_labeled_slider ('Ціна ($/день) *',price_slider ,price_value ),_labeled_slider ('Кількість місць',seats_slider ,seats_value )),_section ('Номер',plate ),_section ('Колір',color_rg ),_section ('Коробка передач',transmission_rg ),_section ('Тип палива',fuel_rg ),_section ('Пробіг',_labeled_slider ('Пробіг (км)',mileage_slider ,mileage_value )),_section ('Додатково',premium_switch ,ft .Row (controls =[insured_cb ,ac_cb ],spacing =24 ,wrap =True )),_section ('Опис',description ),ft .Divider (height =12 ,color =ft .Colors .BLUE_GREY_100 ),ft .Text ('Фотографії',size =14 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .BLUE_GREY_900 ),ft .Row (controls =[pick_btn ,self ._photo_status_text ],spacing =12 ,vertical_alignment =ft .CrossAxisAlignment .CENTER ),self ._photo_previews ,ft .Divider (height =12 ,color =ft .Colors .BLUE_GREY_100 ),error_text ,ft .Row (controls =[save_btn ])],spacing =14 ,scroll =ft .ScrollMode .AUTO ),bgcolor =ft .Colors .WHITE ,border_radius =16 ,padding =ft .Padding (20 ,20 ,20 ,20 ),shadow =ft .BoxShadow (spread_radius =0 ,blur_radius =12 ,color =ft .Colors .BLACK12 ,offset =ft .Offset (0 ,2 )))
        return ft .View (route ='/admin/add-car',padding =0 ,bgcolor =ft .Colors .with_opacity (0.07 ,ft .Colors .DEEP_PURPLE_900 ),services =[file_picker ,year_picker ],controls =[ft .Column (spacing =0 ,expand =True ,controls =[header ,ft .Container (content =ft .Column (controls =[form_card ],scroll =ft .ScrollMode .AUTO ,expand =True ),expand =True ,padding =ft .Padding (16 ,14 ,16 ,14 ))])])

    def _update_slider_label (self ,text :ft .Text ,value :str ):
        text .value =value
        if text .page :
            text .update ()
