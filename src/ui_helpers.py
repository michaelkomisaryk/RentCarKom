from __future__ import annotations
import base64
from pathlib import Path
import flet as ft

def show_message (page :ft .Page ,msg :str ,*,error :bool =False )->None :
    try :
        page .show_dialog (ft .SnackBar (content =ft .Text (msg ,color =ft .Colors .WHITE ),bgcolor =ft .Colors .RED_700 if error else ft .Colors .GREEN_700 ,duration =4000 ))
    except Exception :
        pass

def image_src_for_flet (stored :str |None )->str |None :
    if not stored :
        return None
    s =stored .replace ('\\','/').strip ()
    if s .startswith ('cars/'):
        return s
    marker ='/cars/'
    if marker in s :
        return 'cars/'+s .split (marker ,1 )[1 ]
    if s .startswith ('/')and Path (s ).is_file ():
        return s
    return s

def image_src_for_preview (path :str |None ,file_bytes :bytes |None ,filename :str )->str |bytes :
    if file_bytes is not None :
        ext =Path (filename ).suffix .lower ()
        mime ={'.png':'image/png','.gif':'image/gif','.webp':'image/webp','.jpg':'image/jpeg','.jpeg':'image/jpeg'}.get (ext ,'image/jpeg')
        b64 =base64 .b64encode (file_bytes ).decode ('ascii')
        return f'data:{mime };base64,{b64 }'
    return path or ''

def user_safe_error (exc :BaseException ,default :str ='Something went wrong. Check your input.')->str :
    if isinstance (exc ,ValueError ):
        return 'Некоректне числове значення або формат даних.'
    if isinstance (exc ,KeyError ):
        return 'Не вистачає обовʼязкового поля.'
    if isinstance (exc ,PermissionError ):
        return 'Немає прав на запис файлу.'
    if isinstance (exc ,OSError ):
        return 'Помилка файлової системи при збереженні.'
    return default
