import asyncio
from datetime import datetime ,timedelta
import flet as ft
from src .database import DB
from src .state import AppState
from src .components .header import build_header
from src .ui_helpers import image_src_for_flet ,show_message ,user_safe_error

class CarDetailView :

    def __init__ (self ,page :ft .Page ,car_id :str ):
        self ._page =page
        self ._car_id =car_id

    def _get_car (self )->dict |None :
        return DB .get_car (self ._car_id )

    def build (self )->ft .View :
        car =self ._get_car ()
        if car is None :
            return ft .View (route =f'/car/{self ._car_id }',controls =[ft .Text ('Car not found',size =20 ,color =ft .Colors .RED_500 )])
        header =build_header (self ._page ,title =f"{car ['brand']} {car ['model']}",show_back =True )
        file_picker =ft .FilePicker ()
        _PHOTO_H =240
        photos =car .get ('photos',[])
        photo_index_ref =[0 ]

        def _apply_gallery_photo (idx :int ):
            if not photos :
                gallery_image .image =None
                gallery_image .content =ft .Column (controls =[ft .Icon (ft .Icons .DIRECTIONS_CAR_OUTLINED ,size =80 ,color =ft .Colors .GREY_500 ),ft .Text ('Фото ще немає',color =ft .Colors .GREY_500 ,size =13 )],horizontal_alignment =ft .CrossAxisAlignment .CENTER ,alignment =ft .MainAxisAlignment .CENTER )
                gallery_image .bgcolor =ft .Colors .GREY_200
                return
            src =image_src_for_flet (photos [idx ])or photos [idx ]
            gallery_image .content =None
            gallery_image .bgcolor =None
            gallery_image .image =ft .DecorationImage (src =src ,fit =ft .BoxFit .COVER ,alignment =ft .Alignment .CENTER )
        gallery_image =ft .Container (height =_PHOTO_H ,expand =True ,border_radius =14 ,clip_behavior =ft .ClipBehavior .HARD_EDGE ,bgcolor =ft .Colors .GREY_200 )
        _apply_gallery_photo (0 )
        photo_counter =ft .Text (f'1 / {len (photos )}'if photos else '',size =12 ,color =ft .Colors .GREY_500 )

        def prev_photo (e ):
            if not photos :
                return
            photo_index_ref [0 ]=(photo_index_ref [0 ]-1 )%len (photos )
            _apply_gallery_photo (photo_index_ref [0 ])
            photo_counter .value =f'{photo_index_ref [0 ]+1 } / {len (photos )}'
            self ._page .update ()

        def next_photo (e ):
            if not photos :
                return
            photo_index_ref [0 ]=(photo_index_ref [0 ]+1 )%len (photos )
            _apply_gallery_photo (photo_index_ref [0 ])
            photo_counter .value =f'{photo_index_ref [0 ]+1 } / {len (photos )}'
            self ._page .update ()
        nav_row =ft .Row (controls =[ft .IconButton (icon =ft .Icons .CHEVRON_LEFT ,on_click =prev_photo ,disabled =len (photos )<2 ,icon_color =ft .Colors .GREY_700 ),photo_counter ,ft .IconButton (icon =ft .Icons .CHEVRON_RIGHT ,on_click =next_photo ,disabled =len (photos )<2 ,icon_color =ft .Colors .GREY_700 )],alignment =ft .MainAxisAlignment .CENTER ,spacing =4 )
        dots_row =ft .Container ()
        if len (photos )>1 :
            dots_row =ft .Row (controls =[ft .Container (width =8 if i ==0 else 6 ,height =8 if i ==0 else 6 ,bgcolor =ft .Colors .GREY_700 if i ==0 else ft .Colors .GREY_400 ,border_radius =4 )for i in range (len (photos ))],alignment =ft .MainAxisAlignment .CENTER ,spacing =4 )

        def info_row (icon ,label :str ,value :str ):
            return ft .Row (controls =[ft .Icon (icon ,size =18 ,color =ft .Colors .GREY_500 ),ft .Text (label ,size =13 ,color =ft .Colors .GREY_600 ,width =110 ),ft .Text (value ,size =13 ,weight =ft .FontWeight .W_500 ,color =ft .Colors .GREY_900 )],spacing =8 )
        status_color =ft .Colors .RED_400 if car ['is_rented']else ft .Colors .GREEN_600
        status_label ='Currently Rented'if car ['is_rented']else 'Available for Rent'
        status_chip =ft .Container (content =ft .Text (status_label ,size =12 ,weight =ft .FontWeight .BOLD ,color =ft .Colors .WHITE ),bgcolor =status_color ,border_radius =6 ,padding =ft .Padding (10 ,4 ,10 ,4 ))
        active_rental_section =ft .Container (visible =False )
        active_rentals =[r for r in DB .get_rentals_for_car (self ._car_id )if r ['status']=='active']
        if active_rentals and AppState .is_manager_or_admin ():
            r =active_rentals [0 ]
            active_rental_section =ft .Container (content =ft .Column (controls =[ft .Text ('Active Rental',size =14 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .ORANGE_800 ),ft .Text (f"Renter: {r ['renter_name']} ({r ['user_email']})",size =13 ),ft .Text (f"From: {r ['start_datetime'][:16 ].replace ('T',' ')}",size =13 ),ft .Text (f"Until: {r ['end_datetime'][:16 ].replace ('T',' ')}",size =13 ),ft .Text (f"Total: ${r ['total_price']}",size =13 ,weight =ft .FontWeight .BOLD ),ft .Row (controls =[ft .Button (content =ft .Text ('Mark Completed',color =ft .Colors .WHITE ,size =12 ),style =ft .ButtonStyle (bgcolor =ft .Colors .GREEN_700 ,shape =ft .RoundedRectangleBorder (radius =8 )),on_click =lambda e ,rid =r ['id']:self ._complete_rental (rid )),ft .Button (content =ft .Text ('Cancel Rental',color =ft .Colors .WHITE ,size =12 ),style =ft .ButtonStyle (bgcolor =ft .Colors .RED_700 ,shape =ft .RoundedRectangleBorder (radius =8 )),on_click =lambda e ,rid =r ['id']:self ._cancel_rental (rid ))],spacing =8 )],spacing =4 ),bgcolor =ft .Colors .ORANGE_50 ,border_radius =10 ,padding =ft .Padding (12 ,12 ,12 ,12 ),border =ft .Border .all (1 ,ft .Colors .ORANGE_200 ),visible =True )
        today =datetime .now ().replace (hour =0 ,minute =0 ,second =0 ,microsecond =0 )
        default_end =today +timedelta (days =1 )
        max_rent_date =datetime (today .year +2 ,12 ,31 )

        def _fmt_date (dt :datetime |None )->str :
            if not dt :
                return '—'
            d =dt .date ()if isinstance (dt ,datetime )else dt
            return d .strftime ('%d.%m.%Y')

        def _days_label (n :int )->str :
            if n %10 ==1 and n %100 !=11 :
                return f'{n } день'
            if n %10 in (2 ,3 ,4 )and n %100 not in (12 ,13 ,14 ):
                return f'{n } дні'
            return f'{n } днів'
        start_display =ft .Text (_fmt_date (today ),size =16 ,weight =ft .FontWeight .W_700 ,color =ft .Colors .DEEP_PURPLE_800 )
        end_display =ft .Text (_fmt_date (default_end ),size =16 ,weight =ft .FontWeight .W_700 ,color =ft .Colors .DEEP_PURPLE_800 )
        initial_days =(default_end .date ()-today .date ()).days +1
        rental_summary =ft .Text (f"{_days_label (initial_days )} · ${car ['price']*initial_days :.2f}",size =13 ,color =ft .Colors .BLUE_GREY_700 )

        def _recalc_rental_summary ():
            s ,e =(start_picker .value ,end_picker .value )
            if s :
                start_display .value =_fmt_date (s )
            if e :
                end_display .value =_fmt_date (e )
            if s and e :
                sd =s .date ()if isinstance (s ,datetime )else s
                ed =e .date ()if isinstance (e ,datetime )else e
                days =max (0 ,(ed -sd ).days +1 )
                total =car ['price']*days if days >0 else 0
                rental_summary .value =f'{_days_label (days )} · ${total :.2f}'
            self ._page .update ()
        start_picker =ft .DatePicker (value =today ,first_date =today ,last_date =max_rent_date ,help_text ='Дата початку оренди',confirm_text ='OK',cancel_text ='Скасувати',on_change =lambda _ :_recalc_rental_summary ())
        end_picker =ft .DatePicker (value =default_end ,first_date =today ,last_date =max_rent_date ,help_text ='Дата закінчення оренди',confirm_text ='OK',cancel_text ='Скасувати',on_change =lambda _ :_recalc_rental_summary ())

        def _date_pick_row (label :str ,display :ft .Text ,picker :ft .DatePicker )->ft .Container :
            return ft .Container (content =ft .Column (controls =[ft .Text (label ,size =12 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .BLUE_GREY_600 ),ft .Row (controls =[ft .OutlinedButton (content =ft .Row (controls =[ft .Icon (ft .Icons .CALENDAR_MONTH ,size =18 ),ft .Text ('Обрати',size =13 )],spacing =8 ,tight =True ),on_click =lambda _ ,p =picker :self ._page .show_dialog (p )),display ],spacing =16 ,vertical_alignment =ft .CrossAxisAlignment .CENTER )],spacing =6 ),padding =ft .Padding (12 ,10 ,12 ,10 ),border =ft .Border .all (1 ,ft .Colors .BLUE_GREY_200 ),border_radius =10 )
        renter_name_field =ft .TextField (label ='ПІБ орендаря *',prefix_icon =ft .Icons .PERSON_OUTLINE ,border_radius =8 ,border_color =ft .Colors .GREY_400 ,value =AppState .current_user ['name']if AppState .is_logged_in ()else '')
        rental_error =ft .Text ('',color =ft .Colors .RED_600 ,size =13 ,visible =False )

        def on_rent (_ ):
            rental_error .visible =False
            if not AppState .is_logged_in ():
                rental_error .value ='Увійдіть, щоб орендувати авто'
                rental_error .visible =True
                self ._page .update ()
                return
            name =(renter_name_field .value or '').strip ()
            if not name :
                rental_error .value ='Вкажіть ПІБ орендаря'
                rental_error .visible =True
                self ._page .update ()
                return
            s ,e =(start_picker .value ,end_picker .value )
            if not s or not e :
                rental_error .value ='Оберіть дати початку та закінчення оренди'
                rental_error .visible =True
                self ._page .update ()
                return
            sd =s .date ()if isinstance (s ,datetime )else s
            ed =e .date ()if isinstance (e ,datetime )else e
            days =(ed -sd ).days +1
            if days <1 :
                rental_error .value ='Некоректний період оренди'
                rental_error .visible =True
                self ._page .update ()
                return
            try :
                ok ,result =DB .create_rental (self ._car_id ,AppState .current_user ,days ,name ,start_date =s ,end_date =e )
            except Exception as ex :
                rental_error .value =user_safe_error (ex ,'Помилка оформлення оренди.')
                rental_error .visible =True
                self ._page .update ()
                return
            if ok :

                async def confirm_ok (e ):
                    self ._page .pop_dialog ()
                    await self ._page .push_route ('/home')
                self ._page .show_dialog (ft .AlertDialog (title =ft .Text ('Оренду підтверджено! 🎉'),content =ft .Text (f"Авто: {car ['brand']} {car ['model']}\nНомер: {car .get ('plate','—')}\nОрендар: {name }\nЗ: {_fmt_date (s )}  →  До: {_fmt_date (e )}\nДнів: {days }\nРазом: ${car ['price']*days :.2f}\n\nID оренди: {result }"),actions =[ft .TextButton ('OK',on_click =confirm_ok )]))
            else :
                rental_error .value =result
                rental_error .visible =True
                self ._page .update ()
        can_rent =not car ['is_rented']
        rent_btn =ft .Button (content =ft .Text ('Rent This Car'if can_rent else 'Currently Unavailable',color =ft .Colors .WHITE ,size =14 ,weight =ft .FontWeight .W_600 ),style =ft .ButtonStyle (bgcolor =ft .Colors .GREY_800 if can_rent else ft .Colors .GREY_400 ,shape =ft .RoundedRectangleBorder (radius =10 ),padding =ft .Padding (0 ,14 ,0 ,14 )),expand =True ,on_click =on_rent if can_rent else None ,disabled =not can_rent )
        rental_section =ft .Container (content =ft .Column (controls =[ft .Text ('Оформити оренду',size =15 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .GREY_800 ),renter_name_field ,_date_pick_row ('Дата початку *',start_display ,start_picker ),_date_pick_row ('Дата закінчення *',end_display ,end_picker ),rental_summary ,rental_error ,ft .Row (controls =[rent_btn ])],spacing =10 ),bgcolor =ft .Colors .WHITE ,border_radius =12 ,padding =ft .Padding (16 ,16 ,16 ,16 ),border =ft .Border .all (1 ,ft .Colors .GREY_200 ))
        if not AppState .is_logged_in ():
            rental_section =ft .Container (content =ft .Column (controls =[ft .Icon (ft .Icons .LOCK_OUTLINE ,size =32 ,color =ft .Colors .GREY_400 ),ft .Text ('Log in to rent this car',color =ft .Colors .GREY_500 ,size =14 ),ft .TextButton (content ='Увійти / Зареєструватися',on_click =lambda e :asyncio .ensure_future (self ._page .push_route ('/login')))],horizontal_alignment =ft .CrossAxisAlignment .CENTER ,spacing =8 ),bgcolor =ft .Colors .WHITE ,border_radius =12 ,padding =ft .Padding (20 ,20 ,20 ,20 ),alignment =ft .Alignment (0 ,0 ))
        admin_section =ft .Container (visible =False )
        if AppState .is_admin ():

            async def pick_photos (_ ):
                try :
                    files =await file_picker .pick_files (dialog_title ='Оберіть фото',file_type =ft .FilePickerFileType .IMAGE ,allow_multiple =True ,with_data =True )
                except Exception as ex :
                    show_message (self ._page ,user_safe_error (ex ,'Не вдалося відкрити вибір файлів.'),error =True )
                    return
                if not files :
                    return
                added =0
                for f in files :
                    try :
                        if f .bytes is not None :
                            result =DB .add_photo_to_car (self ._car_id ,data =f .bytes ,filename_hint =f .name or 'image.jpg')
                        elif f .path :
                            result =DB .add_photo_to_car (self ._car_id ,f .path )
                        else :
                            result =None
                        if result :
                            added +=1
                    except Exception as ex :
                        show_message (self ._page ,user_safe_error (ex ,'Помилка збереження фото.'),error =True )
                        return
                if added :
                    show_message (self ._page ,f'Додано фото: {added }')
                    await self ._page .push_route (f'/car/{self ._car_id }')
                else :
                    show_message (self ._page ,'Файли не містять даних. Спробуйте інше зображення або інший браузер.',error =True )

            async def delete_car_click (e ):

                async def confirm_delete (e ):
                    self ._page .pop_dialog ()
                    DB .delete_car (self ._car_id )
                    self ._page .show_dialog (ft .SnackBar (content =ft .Text ('Car deleted',color =ft .Colors .WHITE ),bgcolor =ft .Colors .GREEN_700 ))
                    await self ._page .push_route ('/home')
                self ._page .show_dialog (ft .AlertDialog (title =ft .Text ('Delete car?'),content =ft .Text (f"Delete {car ['brand']} {car ['model']}? This cannot be undone."),actions =[ft .TextButton ('Cancel',on_click =lambda e :self ._page .pop_dialog ()),ft .TextButton ('Delete',style =ft .ButtonStyle (color =ft .Colors .RED_600 ),on_click =confirm_delete )]))
            admin_section =ft .Container (content =ft .Column (controls =[ft .Text ('Admin Controls',size =14 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .GREY_700 ),ft .Row (controls =[ft .Button (content =ft .Row (controls =[ft .Icon (ft .Icons .ADD_PHOTO_ALTERNATE ,color =ft .Colors .WHITE ,size =16 ),ft .Text ('Add Photos',color =ft .Colors .WHITE ,size =13 )],spacing =6 ),style =ft .ButtonStyle (bgcolor =ft .Colors .BLUE_700 ,shape =ft .RoundedRectangleBorder (radius =8 )),on_click =pick_photos ),ft .Button (content =ft .Row (controls =[ft .Icon (ft .Icons .DELETE_OUTLINE ,color =ft .Colors .WHITE ,size =16 ),ft .Text ('Delete Car',color =ft .Colors .WHITE ,size =13 )],spacing =6 ),style =ft .ButtonStyle (bgcolor =ft .Colors .RED_700 ,shape =ft .RoundedRectangleBorder (radius =8 )),on_click =delete_car_click )],spacing =10 )],spacing =10 ),bgcolor =ft .Colors .GREY_50 ,border_radius =10 ,padding =ft .Padding (14 ,14 ,14 ,14 ),border =ft .Border .all (1 ,ft .Colors .GREY_200 ),visible =True )
        my_history =ft .Container (visible =False )
        if AppState .is_logged_in ():
            my_rentals =DB .get_rentals_for_user (AppState .current_user ['id'])
            car_my =[r for r in my_rentals if r ['car_id']==self ._car_id ]
            if car_my :
                status_colors ={'active':ft .Colors .ORANGE_600 ,'completed':ft .Colors .GREEN_600 ,'cancelled':ft .Colors .RED_500 }
                rows =[ft .Container (content =ft .Column (controls =[ft .Row (controls =[ft .Text (r ['renter_name'],size =13 ,weight =ft .FontWeight .W_500 ),ft .Container (content =ft .Text (r ['status'].upper (),size =10 ,color =ft .Colors .WHITE ),bgcolor =status_colors .get (r ['status'],ft .Colors .GREY_600 ),border_radius =4 ,padding =ft .Padding (6 ,2 ,6 ,2 ))],spacing =8 ),ft .Text (f"{r ['start_datetime'][:10 ]}  →  {r ['end_datetime'][:10 ]}",size =12 ,color =ft .Colors .GREY_600 ),ft .Text (f"{r ['days']} days  •  ${r ['total_price']}",size =12 ,color =ft .Colors .GREY_700 )],spacing =3 ),bgcolor =ft .Colors .WHITE ,border_radius =8 ,padding =ft .Padding (10 ,10 ,10 ,10 ),border =ft .Border .all (1 ,ft .Colors .GREY_200 ),margin =ft .Margin (0 ,0 ,0 ,6 ))for r in reversed (car_my )]
                my_history =ft .Container (content =ft .Column (controls =[ft .Text ('My Rentals for This Car',size =14 ,weight =ft .FontWeight .W_600 )]+rows ,spacing =6 ),visible =True )
        body =ft .Column (controls =[gallery_image ,nav_row ,dots_row ,ft .Container (height =8 ),ft .Row (controls =[ft .Column (controls =[ft .Text (f"{car ['brand']} {car ['model']}",size =22 ,weight =ft .FontWeight .BOLD ,color =ft .Colors .GREY_900 ),ft .Text (f"${car ['price']} / day",size =18 ,color =ft .Colors .GREY_700 ,weight =ft .FontWeight .W_500 )],spacing =4 ,expand =True ),status_chip ],vertical_alignment =ft .CrossAxisAlignment .START ),ft .Divider (height =16 ,color =ft .Colors .GREY_200 ),info_row (ft .Icons .BADGE ,'Plate:',car .get ('plate','—')),info_row (ft .Icons .CALENDAR_MONTH ,'Year:',str (car ['year'])),info_row (ft .Icons .PEOPLE ,'Seats:',str (car ['seats'])),info_row (ft .Icons .SETTINGS ,'Transmission:',car ['transmission']),info_row (ft .Icons .LOCAL_GAS_STATION ,'Fuel:',car ['fuel']),info_row (ft .Icons .COLOR_LENS ,'Color:',car .get ('color','—')),info_row (ft .Icons .SPEED ,'Mileage:',f"{car .get ('mileage',0 ):,} km"),ft .Divider (height =16 ,color =ft .Colors .GREY_200 ),ft .Text ('Description',size =14 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .GREY_800 ),ft .Text (car ['description'],size =13 ,color =ft .Colors .GREY_700 ),ft .Container (height =8 ),active_rental_section ,rental_section ,ft .Container (height =8 ),admin_section ,my_history ,ft .Container (height =24 )],scroll =ft .ScrollMode .AUTO ,expand =True ,spacing =6 )
        return ft .View (route =f'/car/{self ._car_id }',padding =0 ,bgcolor =ft .Colors .GREY_100 ,services =[start_picker ,end_picker ]+([file_picker ]if AppState .is_admin ()else []),controls =[ft .Column (spacing =0 ,expand =True ,controls =[header ,ft .Container (content =body ,expand =True ,padding =ft .Padding (16 ,12 ,16 ,12 ))])])

    def _complete_rental (self ,rental_id :str ):
        DB .complete_rental (rental_id )
        self ._page .show_dialog (ft .SnackBar (content =ft .Text ('Rental marked as completed',color =ft .Colors .WHITE ),bgcolor =ft .Colors .GREEN_700 ))
        asyncio .ensure_future (self ._page .push_route (f'/car/{self ._car_id }'))

    def _cancel_rental (self ,rental_id :str ):
        DB .cancel_rental (rental_id )
        self ._page .show_dialog (ft .SnackBar (content =ft .Text ('Rental cancelled',color =ft .Colors .WHITE ),bgcolor =ft .Colors .GREEN_700 ))
        asyncio .ensure_future (self ._page .push_route (f'/car/{self ._car_id }'))
