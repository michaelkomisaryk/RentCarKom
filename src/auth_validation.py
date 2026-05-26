from __future__ import annotations
import re
import unicodedata
_EMAIL_RE =re .compile ('^[a-zA-Z0-9][a-zA-Z0-9._%+-]{0,63}@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\\.[a-zA-Z]{2,})+$')
_SPECIAL_RE =re .compile ('[!@#$%^&*()_+\\-=\\[\\]{}|;:,.<>?/~`"\\\\]')

def validate_email (email :str )->tuple [bool ,str ]:
    e =(email or '').strip ().lower ()
    if not e :
        return (False ,'Введіть email.')
    if len (e )>254 :
        return (False ,'Email занадто довгий.')
    if not _EMAIL_RE .match (e ):
        return (False ,'Некоректний формат email (наприклад: name@domain.com).')
    local ,_ ,domain =e .partition ('@')
    if len (local )>64 or len (domain )>253 :
        return (False ,'Некоректний формат email.')
    return (True ,'')

def validate_display_name (name :str )->tuple [bool ,str ]:
    n =(name or '').strip ()
    if len (n )<2 :
        return (False ,"Ім'я має містити щонайменше 2 символи.")
    if len (n )>80 :
        return (False ,"Ім'я занадто довге (макс. 80 символів).")
    for ch in n :
        if ch in " '-.":
            continue
        cat =unicodedata .category (ch )
        if cat [0 ]!='L':
            return (False ,"Ім'я може містити лише літери, пробіл, дефіс, апостроф або крапку.")
    return (True ,'')

def validate_password_strength (password :str )->tuple [bool ,str ]:
    p =password or ''
    if len (p )<8 :
        return (False ,'Пароль має містити щонайменше 8 символів.')
    if len (p )>128 :
        return (False ,'Пароль занадто довгий.')
    if ' 'in p :
        return (False ,'Пароль не повинен містити пробіли.')
    if not re .search ('[A-Z]',p ):
        return (False ,'Додайте хоча б одну велику латинську літеру (A–Z).')
    if not re .search ('[a-z]',p ):
        return (False ,'Додайте хоча б одну малу латинську літеру (a–z).')
    if not re .search ('\\d',p ):
        return (False ,'Додайте хоча б одну цифру (0–9).')
    if not _SPECIAL_RE .search (p ):
        return (False ,'Додайте хоча б один спецсимвол (!@#$%^&* тощо).')
    lower =p .lower ()
    if lower in ('password123!','qwerty123!','12345678!','11111111!'):
        return (False ,'Цей пароль занадто слабкий / типовий. Оберіть інший.')
    return (True ,'')

def validate_registration (name :str ,email :str ,password :str )->tuple [bool ,str ]:
    ok ,msg =validate_display_name (name )
    if not ok :
        return (False ,msg )
    ok ,msg =validate_email (email )
    if not ok :
        return (False ,msg )
    ok ,msg =validate_password_strength (password )
    if not ok :
        return (False ,msg )
    return (True ,'')
