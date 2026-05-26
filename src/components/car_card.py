from __future__ import annotations
from datetime import datetime ,timedelta
import flet as ft
from flet .controls .control_event import ControlEvent
from src .database import DB
from src .neon_ui import neon_card_glow
from src .state import AppState
from src .ui_helpers import image_src_for_flet
_EASE =ft .AnimationCurve .EASE_OUT_CUBIC
_ANIM =ft .Animation (320 ,_EASE )
_HOVER_SCALE =1.03
_PHOTO_H =158
_DETAILS_H =128

def _is_new_car (car :dict )->bool :
    year =int (car .get ('year',0 ))
    if year >=2024 :
        return True
    raw =car .get ('created_at')
    if not raw :
        return False
    try :
        created =datetime .fromisoformat (str (raw ))
        return created >=datetime .now ()-timedelta (days =120 )
    except ValueError :
        return False

def _badge (label :str ,color :str ,icon :str |None =None )->ft .Container :
    row_controls :list =[]
    if icon :
        row_controls .append (ft .Icon (icon ,size =11 ,color =ft .Colors .WHITE ))
    row_controls .append (ft .Text (label ,size =10 ,weight =ft .FontWeight .W_600 ,color =ft .Colors .WHITE ))
    return ft .Container (content =ft .Row (controls =row_controls ,spacing =4 ,tight =True ),bgcolor =ft .Colors .with_opacity (0.85 ,color ),border =ft .Border .all (1 ,ft .Colors .with_opacity (0.5 ,color )),border_radius =20 ,padding =ft .Padding (8 ,4 ,8 ,4 ))

def _car_badges (car :dict )->list [ft .Container ]:
    badges :list [ft .Container ]=[]
    if not car .get ('is_rented'):
        badges .append (_badge ('Вільно',ft .Colors .GREEN_600 ,ft .Icons .CHECK_CIRCLE ))
    else :
        badges .append (_badge ('Зайнято',ft .Colors .DEEP_ORANGE_500 ,ft .Icons .SCHEDULE ))
    if car .get ('is_premium')or float (car .get ('price',0 ))>=85 :
        badges .append (_badge ('Premium',ft .Colors .AMBER_700 ,ft .Icons .WORKSPACE_PREMIUM ))
    if str (car .get ('fuel','')).lower ()=='electric':
        badges .append (_badge ('Electric',ft .Colors .CYAN_700 ,ft .Icons .ELECTRIC_BOLT ))
    elif str (car .get ('fuel','')).lower ()=='hybrid':
        badges .append (_badge ('Hybrid',ft .Colors .TEAL_600 ,ft .Icons .ECO ))
    if _is_new_car (car ):
        badges .append (_badge ('New',ft .Colors .PINK_400 ,ft .Icons .NEW_RELEASES ))
    return badges

def _rental_count (car_id :str )->int :
    return sum ((1 for r in DB .get_rentals ()if r .get ('car_id')==car_id ))

def build_car_card (page :ft .Page ,car :dict )->ft .Container :
    car_id =car ['id']
    accent =ft .Colors .CYAN_ACCENT_200 if not car .get ('is_rented')else ft .Colors .ORANGE_ACCENT_200
    hover_accent =ft .Colors .PINK_ACCENT_200
    hover_state ={'in':False }

    async def go_to_detail (_ ):
        await page .push_route (f'/car/{car_id }')

    async def on_rent_now (_ ):
        await page .push_route (f'/car/{car_id }')

    def on_favorite (e :ControlEvent ):
        fav =AppState .toggle_favorite (car_id )
        e .control .icon =ft .Icons .FAVORITE if fav else ft .Icons .FAVORITE_BORDER
        e .control .icon_color =ft .Colors .PINK_ACCENT_200 if fav else ft .Colors .with_opacity (0.7 ,ft .Colors .WHITE )
        page .update ()
    photos =car .get ('photos')or []
    src0 =image_src_for_flet (photos [0 ])if photos else None
    if src0 :
        photo =ft .Container (height =_PHOTO_H ,clip_behavior =ft .ClipBehavior .HARD_EDGE ,border_radius =ft .BorderRadius (12 ,12 ,0 ,0 ),image =ft .DecorationImage (src =src0 ,fit =ft .BoxFit .COVER ,alignment =ft .Alignment (0 ,0 )))
    else :
        photo =ft .Container (height =_PHOTO_H ,border_radius =ft .BorderRadius (12 ,12 ,0 ,0 ),gradient =ft .LinearGradient (begin =ft .Alignment (-1 ,-1 ),end =ft .Alignment (1 ,1 ),colors =[ft .Colors .with_opacity (0.35 ,accent ),ft .Colors .with_opacity (0.15 ,ft .Colors .DEEP_PURPLE_900 )]),content =ft .Icon (ft .Icons .DIRECTIONS_CAR_OUTLINED ,size =56 ,color =ft .Colors .with_opacity (0.7 ,accent )),alignment =ft .Alignment (0 ,0 ))
    rating =float (car .get ('rating',4.5 ))
    popularity =_rental_count (car_id )
    badges_wrap =ft .Row (controls =_car_badges (car ),spacing =6 ,wrap =True ,run_spacing =6 )
    photo_stack =ft .Stack (height =_PHOTO_H ,controls =[photo ,ft .Container (content =badges_wrap ,top =8 ,left =8 ,right =8 )])
    base_info =ft .Column (controls =[ft .Text (f"{car ['brand']} {car ['model']}",size =16 ,weight =ft .FontWeight .BOLD ,color =ft .Colors .WHITE ,max_lines =1 ,overflow =ft .TextOverflow .ELLIPSIS ),ft .Text (f"{car .get ('year','')} · {car .get ('fuel','')}",size =12 ,color =ft .Colors .with_opacity (0.6 ,ft .Colors .WHITE )),ft .Row (controls =[ft .Text (f"${float (car .get ('price',0 )):.0f}",size =20 ,weight =ft .FontWeight .W_700 ,color =ft .Colors .CYAN_ACCENT_200 ),ft .Text ('/день',size =12 ,color =ft .Colors .with_opacity (0.54 ,ft .Colors .WHITE )),ft .Container (expand =True ),ft .Row (controls =[ft .Icon (ft .Icons .STAR ,size =14 ,color =ft .Colors .AMBER_300 ),ft .Text (f'{rating :.1f}',size =12 ,color =ft .Colors .with_opacity (0.7 ,ft .Colors .WHITE ))],spacing =2 )],vertical_alignment =ft .CrossAxisAlignment .CENTER )],spacing =6 ,tight =True )
    hover_overlay =ft .Container (opacity =0 ,animate_opacity =_ANIM ,bgcolor =ft .Colors .with_opacity (0.88 ,ft .Colors .BLUE_GREY_900 ),border_radius =ft .BorderRadius (0 ,0 ,12 ,12 ),padding =ft .Padding (14 ,10 ,14 ,12 ),content =ft .Column (controls =[ft .Row (controls =[ft .Row (controls =[ft .Icon (ft .Icons .STAR ,size =16 ,color =ft .Colors .AMBER_300 ),ft .Text (f'{rating :.1f}',size =13 ,weight =ft .FontWeight .BOLD ,color =ft .Colors .WHITE ),ft .Text (f'· {popularity } оренд',size =11 ,color =ft .Colors .with_opacity (0.65 ,ft .Colors .WHITE ))],spacing =4 ),ft .Text (f"${float (car .get ('price',0 )):.0f}/день",size =15 ,weight =ft .FontWeight .W_700 ,color =ft .Colors .CYAN_100 )],alignment =ft .MainAxisAlignment .SPACE_BETWEEN ),ft .Row (controls =[ft .Icon (ft .Icons .EVENT_SEAT ,size =14 ,color =ft .Colors .CYAN_100 ),ft .Text (f"{car .get ('seats',5 )} місць",size =11 ,color =ft .Colors .with_opacity (0.7 ,ft .Colors .WHITE )),ft .Icon (ft .Icons .SPEED ,size =14 ,color =ft .Colors .CYAN_100 ),ft .Text (f"{int (car .get ('mileage',0 )):,} км".replace (',',' '),size =11 ,color =ft .Colors .with_opacity (0.7 ,ft .Colors .WHITE ))],spacing =6 ,wrap =True ),ft .Row (controls =[ft .IconButton (icon =ft .Icons .FAVORITE if AppState .is_favorite (car_id )else ft .Icons .FAVORITE_BORDER ,icon_color =ft .Colors .PINK_ACCENT_200 if AppState .is_favorite (car_id )else ft .Colors .with_opacity (0.7 ,ft .Colors .WHITE ),icon_size =20 ,tooltip ='Обране',style =ft .ButtonStyle (bgcolor =ft .Colors .with_opacity (0.2 ,ft .Colors .PINK_200 ),shape =ft .CircleBorder ()),on_click =on_favorite ),ft .OutlinedButton (content =ft .Text ('Деталі',size =12 ),style =ft .ButtonStyle (color =ft .Colors .WHITE ,side =ft .BorderSide (1 ,ft .Colors .with_opacity (0.5 ,accent ))),on_click =go_to_detail ),ft .Button (content =ft .Text ('Орендувати',size =12 ,weight =ft .FontWeight .W_600 ),style =ft .ButtonStyle (bgcolor =ft .Colors .DEEP_PURPLE_400 ,color =ft .Colors .WHITE ),on_click =on_rent_now )],spacing =6 ,alignment =ft .MainAxisAlignment .END )],spacing =8 ,tight =True ))
    details_stack =ft .Container (height =_DETAILS_H ,content =ft .Stack (controls =[ft .Container (content =base_info ,padding =ft .Padding (14 ,12 ,14 ,12 ),top =0 ,left =0 ,right =0 ),ft .Container (content =hover_overlay ,top =0 ,left =0 ,right =0 ,bottom =0 )]))
    glass_body =ft .Container (content =ft .Column (controls =[photo_stack ,details_stack ],spacing =0 ,tight =True ),bgcolor =ft .Colors .with_opacity (0.72 ,ft .Colors .BLUE_GREY_900 ),blur =ft .Blur (10 ,10 ,ft .BlurTileMode .CLAMP ),border_radius =14 ,border =ft .Border .all (1 ,ft .Colors .with_opacity (0.28 ,accent )),clip_behavior =ft .ClipBehavior .ANTI_ALIAS )
    sweep =ft .Container (height =2 ,opacity =0 ,animate_opacity =_ANIM ,gradient =ft .LinearGradient (begin =ft .Alignment (-1 ,0 ),end =ft .Alignment (1 ,0 ),colors =[ft .Colors .TRANSPARENT ,ft .Colors .with_opacity (0.75 ,accent ),ft .Colors .with_opacity (0.75 ,hover_accent ),ft .Colors .TRANSPARENT ]))
    border_ring =ft .Container (border_radius =16 ,padding =2 ,gradient =ft .LinearGradient (begin =ft .Alignment (-1 ,-1 ),end =ft .Alignment (1 ,1 ),colors =[ft .Colors .with_opacity (0.4 ,accent ),ft .Colors .with_opacity (0.18 ,ft .Colors .DEEP_PURPLE_400 ),ft .Colors .with_opacity (0.35 ,hover_accent )]),content =ft .Column (controls =[sweep ,glass_body ],spacing =0 ,tight =True ))
    visual =ft .Container (content =border_ring ,scale =ft .Scale (1.0 ),animate_scale =_ANIM ,shadow =neon_card_glow (accent ,strong =False ))

    def on_hover (e :ControlEvent ):
        h =bool (e .data )
        if hover_state ['in']==h :
            return
        hover_state ['in']=h
        visual .scale =ft .Scale (_HOVER_SCALE if h else 1.0 )
        visual .shadow =neon_card_glow (hover_accent if h else accent ,strong =h )
        glass_body .border =ft .Border .all (2 if h else 1 ,ft .Colors .with_opacity (0.85 if h else 0.28 ,hover_accent if h else accent ))
        hover_overlay .opacity =1.0 if h else 0.0
        base_info .opacity =0.0 if h else 1.0
        base_info .animate_opacity =_ANIM
        sweep .opacity =1.0 if h else 0.0
        page .update ()
    base_info .opacity =1.0
    base_info .animate_opacity =_ANIM
    return ft .Container (content =visual ,padding =ft .Padding (4 ,6 ,4 ,10 ),alignment =ft .Alignment (0 ,0 ),on_hover =on_hover ,on_click =go_to_detail ,ink =False )
