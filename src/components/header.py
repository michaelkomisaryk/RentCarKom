import flet as ft
from src .neon_ui import neon_glow ,neon_icon_button ,neon_icon_display
from src .state import AppState
from src .theme import C

def build_header (page :ft .Page ,title :str ='rentCarKom',show_back :bool =False )->ft .Container :

    async def go_back (_ ):
        if len (page .views )>1 :
            page .views .pop ()
            top =page .views [-1 ]
            await page .push_route (top .route )

    async def do_logout (_ ):
        AppState .logout ()
        page .views .clear ()
        await page .push_route ('/home')
    left_controls =[]
    if show_back :
        left_controls .append (neon_icon_button (page ,ft .Icons .ARROW_BACK_IOS_NEW ,on_click =go_back ,tooltip ='Назад',idle_ring =C .CYAN_RING ,hover_ring =C .PINK ,icon_idle =C .CYAN_SOFT ,icon_hover =C .PINK_SOFT ,base_size =20 ))
    title_icon =neon_icon_display (page ,ft .Icons .DIRECTIONS_CAR ,size =26 ,idle_color =C .CYAN ,hover_color =C .PINK ,padding =12 )
    left_controls .append (ft .Row (controls =[title_icon ,ft .Text (title ,size =19 ,weight =ft .FontWeight .BOLD ,color =C .CYAN_SOFT )],spacing =10 ))
    role =AppState .get_role ()
    role_colors ={'admin':ft .Colors .RED_400 ,'manager':ft .Colors .CYAN_300 ,'client':C .GREEN_SOFT ,'guest':ft .Colors .GREY_400 }
    role_labels ={'admin':'ADMIN','manager':'МЕНЕДЖЕР','client':'КЛІЄНТ','guest':'ГІСТЬ'}
    role_badge =ft .Container (content =ft .Text (role_labels .get (role ,role .upper ()),size =10 ,weight =ft .FontWeight .BOLD ,color =ft .Colors .WHITE ),bgcolor =role_colors .get (role ,ft .Colors .GREY_600 ),border_radius =20 ,padding =ft .Padding (10 ,4 ,10 ,4 ),border =ft .Border .all (1 ,ft .Colors .with_opacity (0.8 ,ft .Colors .WHITE )),shadow =neon_glow (C .PINK ,strong =False ))
    right_controls =[role_badge ]
    if AppState .is_logged_in ():
        right_controls .append (neon_icon_button (page ,ft .Icons .LOGOUT ,on_click =do_logout ,tooltip ='Вийти',idle_ring =C .BLUE_SOFT ,hover_ring =C .PINK ,icon_idle =C .CYAN_SOFT ,icon_hover =C .PINK_SOFT ,base_size =22 ))
    else :

        async def go_login (_ ):
            await page .push_route ('/login')
        right_controls .extend ([ft .TextButton (content =ft .Text ('Увійти',size =13 ,color =C .CYAN_SOFT ),on_click =go_login ),ft .Button (content =ft .Text ('Реєстрація',size =12 ,color =ft .Colors .WHITE ),style =ft .ButtonStyle (bgcolor =ft .Colors .with_opacity (0.35 ,ft .Colors .DEEP_PURPLE_400 ),padding =ft .Padding (14 ,8 ,14 ,8 ),shape =ft .RoundedRectangleBorder (radius =10 )),on_click =go_login )])
    return ft .Container (content =ft .Row (controls =[ft .Row (controls =left_controls ,spacing =8 ,vertical_alignment =ft .CrossAxisAlignment .CENTER ),ft .Row (controls =right_controls ,spacing =10 ,vertical_alignment =ft .CrossAxisAlignment .CENTER )],alignment =ft .MainAxisAlignment .SPACE_BETWEEN ,vertical_alignment =ft .CrossAxisAlignment .CENTER ),gradient =ft .LinearGradient (begin =ft .Alignment (-1.2 ,-1 ),end =ft .Alignment (1.2 ,1.2 ),colors =[ft .Colors .PURPLE_900 ,ft .Colors .INDIGO_900 ,ft .Colors .BLUE_GREY_900 ,ft .Colors .BLACK ],stops =[0.0 ,0.35 ,0.72 ,1.0 ]),padding =ft .Padding (14 ,12 ,14 ,12 ),shadow =ft .BoxShadow (spread_radius =0 ,blur_radius =16 ,color =ft .Colors .with_opacity (0.55 ,C .CYAN_RING ),offset =ft .Offset (0 ,4 )))
