class AppState :
    current_user :dict |None =None
    favorite_car_ids :set [str ]=set ()
    _listeners :list =[]

    @classmethod
    def toggle_favorite (cls ,car_id :str )->bool :
        if car_id in cls .favorite_car_ids :
            cls .favorite_car_ids .discard (car_id )
            return False
        cls .favorite_car_ids .add (car_id )
        return True

    @classmethod
    def is_favorite (cls ,car_id :str )->bool :
        return car_id in cls .favorite_car_ids

    @classmethod
    def login (cls ,user :dict ):
        cls .current_user =user
        cls ._notify ()

    @classmethod
    def logout (cls ):
        cls .current_user =None
        cls ._notify ()

    @classmethod
    def is_logged_in (cls )->bool :
        return cls .current_user is not None

    @classmethod
    def get_role (cls )->str :
        if cls .current_user :
            return cls .current_user .get ('role','client')
        return 'guest'

    @classmethod
    def is_admin (cls )->bool :
        return cls .get_role ()=='admin'

    @classmethod
    def is_manager_or_admin (cls )->bool :
        return cls .get_role ()in ('admin','manager')

    @classmethod
    def add_listener (cls ,fn ):
        cls ._listeners .append (fn )

    @classmethod
    def remove_listener (cls ,fn ):
        cls ._listeners =[f for f in cls ._listeners if f !=fn ]

    @classmethod
    def _notify (cls ):
        for fn in list (cls ._listeners ):
            try :
                fn ()
            except Exception :
                pass
