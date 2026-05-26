import flet as ft
from src .database import DB
from src .state import AppState
from src .components .header import build_header

def _show_snack (page :ft .Page ,msg :str ,error :bool =False ):
    page .show_dialog (ft .SnackBar (content =ft .Text (msg ,color =ft .Colors .WHITE ),bgcolor =ft .Colors .RED_700 if error else ft .Colors .GREEN_700 ))

class RentalsView :

    def __init__ (self ,page :ft .Page ):
        self ._page =page

    def build (self )->ft .View :
        if not AppState .is_manager_or_admin ():
            return ft .View (route ='/admin/rentals',controls =[ft .Text ('Access Denied',size =22 ,color =ft .Colors .RED_600 )])
        header =build_header (self ._page ,title ='All Rentals',show_back =True )
        filter_value =['all']
        list_container =ft .Column (spacing =6 ,expand =True )

        def build_rental_cards (status_filter :str ):
            rentals =DB .get_rentals ()
            if status_filter !='all':
                rentals =[r for r in rentals if r ['status']==status_filter ]
            if not rentals :
                return [ft .Container (content =ft .Column (controls =[ft .Icon (ft .Icons .INBOX ,size =48 ,color =ft .Colors .GREY_300 ),ft .Text ('No rentals found',color =ft .Colors .GREY_400 ,size =14 )],horizontal_alignment =ft .CrossAxisAlignment .CENTER ,spacing =8 ),alignment =ft .Alignment (0 ,0 ),padding =ft .Padding (40 ,40 ,40 ,40 ))]
            cards =[]
            status_colors ={'active':ft .Colors .ORANGE_600 ,'completed':ft .Colors .GREEN_600 ,'cancelled':ft .Colors .RED_500 }
            for r in reversed (rentals ):
                s_color =status_colors .get (r ['status'],ft .Colors .GREY_600 )
                action_btns =[]
                if r ['status']=='active'and AppState .is_manager_or_admin ():

                    def make_complete (rid ):

                        def on_complete (e ):
                            DB .complete_rental (rid )
                            _show_snack (self ._page ,'Rental completed')
                            self ._refresh (list_container ,filter_value [0 ])
                        return on_complete

                    def make_cancel (rid ):

                        def on_cancel (e ):
                            DB .cancel_rental (rid )
                            _show_snack (self ._page ,'Rental cancelled')
                            self ._refresh (list_container ,filter_value [0 ])
                        return on_cancel
                    action_btns =[ft .TextButton (content =ft .Text ('Complete',color =ft .Colors .GREEN_700 ,size =12 ),on_click =make_complete (r ['id'])),ft .TextButton (content =ft .Text ('Cancel',color =ft .Colors .RED_700 ,size =12 ),on_click =make_cancel (r ['id']))]
                card =ft .Container (content =ft .Column (controls =[ft .Row (controls =[ft .Text (f"{r ['car_brand']} {r ['car_model']}",size =14 ,weight =ft .FontWeight .BOLD ,color =ft .Colors .GREY_900 ,expand =True ),ft .Container (content =ft .Text (r ['status'].upper (),size =10 ,weight =ft .FontWeight .BOLD ,color =ft .Colors .WHITE ),bgcolor =s_color ,border_radius =4 ,padding =ft .Padding (6 ,2 ,6 ,2 ))]),ft .Text (f"Plate: {r .get ('car_plate','—')}",size =12 ,color =ft .Colors .GREY_600 ),ft .Text (f"Renter: {r ['renter_name']} · {r ['user_email']}",size =12 ,color =ft .Colors .GREY_600 ),ft .Text (f"📅 {r ['start_datetime'][:16 ].replace ('T',' ')} → {r ['end_datetime'][:16 ].replace ('T',' ')}",size =12 ,color =ft .Colors .GREY_600 ),ft .Text (f"{r ['days']} day(s)  •  ${r ['price_per_day']}/day  •  Total: ${r ['total_price']}",size =13 ,weight =ft .FontWeight .W_500 ,color =ft .Colors .GREY_800 ),ft .Text (f"Rental ID: {r ['id']}",size =10 ,color =ft .Colors .GREY_400 ),ft .Row (controls =action_btns ,spacing =4 )if action_btns else ft .Container ()],spacing =4 ),bgcolor =ft .Colors .WHITE ,border_radius =12 ,padding =ft .Padding (14 ,14 ,14 ,14 ),border =ft .Border .all (1 ,ft .Colors .GREY_200 ),shadow =ft .BoxShadow (spread_radius =0 ,blur_radius =4 ,color =ft .Colors .BLACK12 ,offset =ft .Offset (0 ,2 )))
                cards .append (card )
            return cards
        tabs_row =ft .Row (spacing =8 ,scroll =ft .ScrollMode .AUTO )

        def _build_tab (label :str ,value :str ,selected :bool ):
            return ft .Container (content =ft .Text (label ,size =13 ,weight =ft .FontWeight .W_600 if selected else ft .FontWeight .NORMAL ,color =ft .Colors .WHITE if selected else ft .Colors .GREY_700 ),bgcolor =ft .Colors .GREY_800 if selected else ft .Colors .WHITE ,border_radius =20 ,padding =ft .Padding (14 ,8 ,14 ,8 ),border =ft .Border .all (1 ,ft .Colors .GREY_300 if not selected else ft .Colors .GREY_800 ),on_click =lambda e ,v =value :_on_tab (v ),ink =True )

        def _on_tab (value :str ):
            filter_value [0 ]=value
            tabs_row .controls =[_build_tab ('All','all',value =='all'),_build_tab ('Active','active',value =='active'),_build_tab ('Completed','completed',value =='completed'),_build_tab ('Cancelled','cancelled',value =='cancelled')]
            self ._refresh (list_container ,value )
        tabs_row .controls =[_build_tab ('All','all',True ),_build_tab ('Active','active',False ),_build_tab ('Completed','completed',False ),_build_tab ('Cancelled','cancelled',False )]
        list_container .controls =build_rental_cards ('all')
        return ft .View (route ='/admin/rentals',padding =0 ,bgcolor =ft .Colors .GREY_100 ,controls =[ft .Column (spacing =0 ,expand =True ,controls =[header ,ft .Container (content =ft .Column (controls =[ft .Container (height =8 ),tabs_row ,ft .Container (height =8 ),ft .Container (content =list_container ,expand =True ),ft .Container (height =20 )],scroll =ft .ScrollMode .AUTO ,expand =True ,spacing =0 ),expand =True ,padding =ft .Padding (16 ,0 ,16 ,0 ))])])

    def _refresh (self ,list_container :ft .Column ,status_filter :str ):
        rentals =DB .get_rentals ()
        if status_filter !='all':
            rentals =[r for r in rentals if r ['status']==status_filter ]
        status_colors ={'active':ft .Colors .ORANGE_600 ,'completed':ft .Colors .GREEN_600 ,'cancelled':ft .Colors .RED_500 }
        if not rentals :
            list_container .controls =[ft .Container (content =ft .Column (controls =[ft .Icon (ft .Icons .INBOX ,size =48 ,color =ft .Colors .GREY_300 ),ft .Text ('No rentals found',color =ft .Colors .GREY_400 ,size =14 )],horizontal_alignment =ft .CrossAxisAlignment .CENTER ,spacing =8 ),alignment =ft .Alignment (0 ,0 ),padding =ft .Padding (40 ,40 ,40 ,40 ))]
            self ._page .update ()
            return
        cards =[]
        for r in reversed (rentals ):
            s_color =status_colors .get (r ['status'],ft .Colors .GREY_600 )
            action_btns =[]
            if r ['status']=='active'and AppState .is_manager_or_admin ():

                def make_complete (rid ):

                    def on_complete (e ):
                        DB .complete_rental (rid )
                        _show_snack (self ._page ,'Rental completed')
                        self ._refresh (list_container ,status_filter )
                    return on_complete

                def make_cancel (rid ):

                    def on_cancel (e ):
                        DB .cancel_rental (rid )
                        _show_snack (self ._page ,'Rental cancelled')
                        self ._refresh (list_container ,status_filter )
                    return on_cancel
                action_btns =[ft .TextButton (content =ft .Text ('Complete',color =ft .Colors .GREEN_700 ,size =12 ),on_click =make_complete (r ['id'])),ft .TextButton (content =ft .Text ('Cancel',color =ft .Colors .RED_700 ,size =12 ),on_click =make_cancel (r ['id']))]
            card =ft .Container (content =ft .Column (controls =[ft .Row (controls =[ft .Text (f"{r ['car_brand']} {r ['car_model']}",size =14 ,weight =ft .FontWeight .BOLD ,color =ft .Colors .GREY_900 ,expand =True ),ft .Container (content =ft .Text (r ['status'].upper (),size =10 ,weight =ft .FontWeight .BOLD ,color =ft .Colors .WHITE ),bgcolor =s_color ,border_radius =4 ,padding =ft .Padding (6 ,2 ,6 ,2 ))]),ft .Text (f"Plate: {r .get ('car_plate','—')}",size =12 ,color =ft .Colors .GREY_600 ),ft .Text (f"Renter: {r ['renter_name']} · {r ['user_email']}",size =12 ,color =ft .Colors .GREY_600 ),ft .Text (f"📅 {r ['start_datetime'][:16 ].replace ('T',' ')} → {r ['end_datetime'][:16 ].replace ('T',' ')}",size =12 ,color =ft .Colors .GREY_600 ),ft .Text (f"{r ['days']} day(s)  •  Total: ${r ['total_price']}",size =13 ,weight =ft .FontWeight .W_500 ,color =ft .Colors .GREY_800 ),ft .Text (f"ID: {r ['id']}",size =10 ,color =ft .Colors .GREY_400 ),ft .Row (controls =action_btns ,spacing =4 )if action_btns else ft .Container ()],spacing =4 ),bgcolor =ft .Colors .WHITE ,border_radius =12 ,padding =ft .Padding (14 ,14 ,14 ,14 ),border =ft .Border .all (1 ,ft .Colors .GREY_200 ),shadow =ft .BoxShadow (spread_radius =0 ,blur_radius =4 ,color =ft .Colors .BLACK12 ,offset =ft .Offset (0 ,2 )))
            cards .append (card )
        list_container .controls =cards
        self ._page .update ()
