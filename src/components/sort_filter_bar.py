from __future__ import annotations
from typing import Callable
import flet as ft
from src .catalog import SORT_LABELS ,SortDirection ,SortField
_ANIM =ft .Animation (220 ,ft .AnimationCurve .EASE_OUT )
_SORT_FIELDS :list [SortField ]=['price','popularity','newest','rating','availability']

def _chip (label :str ,*,active :bool ,on_click :Callable ,icon :str |None =None )->ft .Container :
    color =ft .Colors .DEEP_PURPLE_600 if active else ft .Colors .BLUE_GREY_100
    text_color =ft .Colors .WHITE if active else ft .Colors .BLUE_GREY_800
    border_color =ft .Colors .DEEP_PURPLE_400 if active else ft .Colors .BLUE_GREY_200
    controls :list =[]
    if icon :
        controls .append (ft .Icon (icon ,size =14 ,color =text_color ))
    controls .append (ft .Text (label ,size =12 ,weight =ft .FontWeight .W_600 if active else ft .FontWeight .W_500 ,color =text_color ))
    return ft .Container (content =ft .Row (controls =controls ,spacing =6 ,tight =True ),padding =ft .Padding (12 ,8 ,12 ,8 ),border_radius =20 ,bgcolor =color ,border =ft .Border .all (1.5 if active else 1 ,border_color ),shadow =ft .BoxShadow (blur_radius =10 if active else 4 ,color =ft .Colors .with_opacity (0.25 if active else 0.08 ,ft .Colors .DEEP_PURPLE ),offset =ft .Offset (0 ,2 ))if active else None ,animate =ft .Animation (200 ,ft .AnimationCurve .EASE_OUT ),on_click =on_click ,ink =True )

class SortFilterBar :

    def __init__ (self ,page :ft .Page ,*,on_change :Callable [[],None ],initial_fuel :str ='All',initial_available_only :bool =False ,initial_sort :SortField ='price',initial_direction :SortDirection ='asc'):
        self ._page =page
        self ._on_change =on_change
        self .fuel =initial_fuel
        self .available_only =initial_available_only
        self .sort_field :SortField =initial_sort
        self .sort_direction :SortDirection =initial_direction
        self ._fuel_chips_row :ft .Row |None =None
        self ._sort_seg :ft .SegmentedButton |None =None
        self ._dir_btn :ft .IconButton |None =None
        self ._active_sort_label :ft .Text |None =None

    def _notify (self ):
        self ._on_change ()

    def _set_sort (self ,field :SortField ):
        self .sort_field =field
        if self ._sort_seg :
            self ._sort_seg .selected =[field ]
        self ._update_sort_ui ()
        self ._notify ()

    def _toggle_direction (self ,_ =None ):
        self .sort_direction ='desc'if self .sort_direction =='asc'else 'asc'
        self ._update_dir_btn ()
        self ._notify ()

    def _update_dir_btn (self ):
        if self ._dir_btn :
            asc =self .sort_direction =='asc'
            self ._dir_btn .icon =ft .Icons .ARROW_UPWARD if asc else ft .Icons .ARROW_DOWNWARD
            self ._dir_btn .tooltip ='За зростанням'if asc else 'За спаданням'

    def _update_sort_ui (self ):
        if self ._sort_seg :
            self ._sort_seg .selected =[self .sort_field ]
        if self ._active_sort_label :
            dir_txt ='↑'if self .sort_direction =='asc'else '↓'
            self ._active_sort_label .value =f'Активно: {SORT_LABELS [self .sort_field ]} {dir_txt }'

    def _set_fuel (self ,fuel :str ):
        self .fuel =fuel
        self ._rebuild_fuel_chips ()
        self ._notify ()

    def _set_available (self ,value :bool ):
        self .available_only =value
        self ._notify ()

    def _rebuild_fuel_chips (self ):
        if not self ._fuel_chips_row :
            return
        fuels =[('All','Усі',None ),('Gasoline','Бензин',ft .Icons .LOCAL_GAS_STATION ),('Diesel','Дизель',ft .Icons .OIL_BARREL ),('Hybrid','Гібрид',ft .Icons .ECO ),('Electric','Електро',ft .Icons .ELECTRIC_BOLT )]
        self ._fuel_chips_row .controls =[_chip (label ,active =self .fuel ==key ,icon =icon ,on_click =lambda e ,k =key :self ._set_fuel (k ))for key ,label ,icon in fuels ]
        self ._page .update ()

    def build (self ,*,brand_search_field :ft .TextField ,avail_toggle :ft .Checkbox )->ft .Container :
        _sort_icons ={'price':ft .Icons .ATTACH_MONEY ,'popularity':ft .Icons .TRENDING_UP ,'newest':ft .Icons .NEW_RELEASES ,'rating':ft .Icons .STAR ,'availability':ft .Icons .CHECK_CIRCLE_OUTLINE }
        sort_segments =[ft .Segment (value =f ,label =ft .Text (SORT_LABELS [f ],size =11 ),icon =_sort_icons [f ])for f in _SORT_FIELDS ]

        def on_sort_seg (e :ft .ControlEvent ):
            sel =e .control .selected
            if sel :
                self .sort_field =sel [0 ]
                self ._update_sort_ui ()
                self ._notify ()
        self ._sort_seg =ft .SegmentedButton (selected =[self .sort_field ],segments =sort_segments ,allow_multiple_selection =False ,style =ft .ButtonStyle (bgcolor =ft .Colors .with_opacity (0.08 ,ft .Colors .DEEP_PURPLE ),color =ft .Colors .BLUE_GREY_800 ,overlay_color =ft .Colors .with_opacity (0.12 ,ft .Colors .DEEP_PURPLE )),on_change =on_sort_seg )
        self ._dir_btn =ft .IconButton (icon =ft .Icons .ARROW_UPWARD ,icon_color =ft .Colors .DEEP_PURPLE_700 ,tooltip ='За зростанням',style =ft .ButtonStyle (bgcolor =ft .Colors .with_opacity (0.1 ,ft .Colors .DEEP_PURPLE ),shape =ft .RoundedRectangleBorder (radius =10 )),on_click =self ._toggle_direction )
        self ._update_dir_btn ()

        def on_sort_dd (e :ft .ControlEvent ):
            self ._set_sort (e .control .value or 'price')
        sort_dd =ft .Dropdown (label ='Сортувати за',width =200 ,value =self .sort_field ,options =[ft .DropdownOption (key =f ,text =SORT_LABELS [f ])for f in _SORT_FIELDS ],border_radius =12 ,text_size =13 ,border_color =ft .Colors .DEEP_PURPLE_200 ,focused_border_color =ft .Colors .DEEP_PURPLE_400 )
        sort_dd .on_select =on_sort_dd
        _base_update =self ._update_sort_ui

        def _update_sort_ui ():
            _base_update ()
            sort_dd .value =self .sort_field
        self ._update_sort_ui =_update_sort_ui
        self ._active_sort_label =ft .Text (f"Активно: {SORT_LABELS [self .sort_field ]} {('↑'if self .sort_direction =='asc'else '↓')}",size =12 ,color =ft .Colors .DEEP_PURPLE_700 ,weight =ft .FontWeight .W_600 )

        def on_avail (e :ft .ControlEvent ):
            self ._set_available (bool (e .control .value ))
        avail_toggle .on_change =on_avail
        self ._fuel_chips_row =ft .Row (spacing =8 ,wrap =True ,run_spacing =8 )
        self ._rebuild_fuel_chips ()
        filter_panel =ft .Container (content =ft .Column (controls =[ft .Row (controls =[ft .Icon (ft .Icons .TUNE ,color =ft .Colors .DEEP_PURPLE_500 ,size =22 ),ft .Text ('Фільтри та сортування',size =17 ,weight =ft .FontWeight .W_700 ,color =ft .Colors .BLUE_GREY_900 ),ft .Container (expand =True ),self ._active_sort_label ],vertical_alignment =ft .CrossAxisAlignment .CENTER ),ft .Container (content =brand_search_field ,animate_opacity =_ANIM ),ft .Text ('Паливо',size =12 ,color =ft .Colors .BLUE_GREY_600 ,weight =ft .FontWeight .W_500 ),self ._fuel_chips_row ,ft .Row (controls =[avail_toggle ]),ft .Divider (height =1 ,color =ft .Colors .BLUE_GREY_100 ),ft .Text ('Сортування',size =12 ,color =ft .Colors .BLUE_GREY_600 ,weight =ft .FontWeight .W_500 ),ft .ResponsiveRow (spacing =12 ,run_spacing =12 ,controls =[ft .Container (col ={'xs':12 ,'md':5 },content =sort_dd ),ft .Container (col ={'xs':12 ,'md':7 },content =ft .Row (controls =[self ._sort_seg ,self ._dir_btn ],spacing =8 ,vertical_alignment =ft .CrossAxisAlignment .CENTER ,scroll =ft .ScrollMode .AUTO ))])],spacing =12 ),padding =ft .Padding (20 ,18 ,20 ,18 ),bgcolor =ft .Colors .with_opacity (0.92 ,ft .Colors .WHITE ),blur =ft .Blur (8 ,8 ,ft .BlurTileMode .CLAMP ),border_radius =18 ,border =ft .Border .all (1 ,ft .Colors .with_opacity (0.15 ,ft .Colors .DEEP_PURPLE_200 )),shadow =ft .BoxShadow (blur_radius =20 ,color =ft .Colors .with_opacity (0.12 ,ft .Colors .DEEP_PURPLE ),offset =ft .Offset (0 ,4 )),animate =ft .Animation (300 ,ft .AnimationCurve .EASE_OUT ))
        return filter_panel
