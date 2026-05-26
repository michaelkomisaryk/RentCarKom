

import asyncio
import os

import flet as ft

from src.database import DB
from src.state import AppState
from src.views.login_view import LoginView
from src.views.home_view import HomeView
from src.views.car_detail_view import CarDetailView
from src.views.add_car_view import AddCarView
from src.views.rentals_view import RentalsView
from src.ui_helpers import show_message


def _is_guest_allowed(route: str) -> bool:
    """Маршрути доступні без входу."""
    if route in ("/home", "/login"):
        return True
    if route.startswith("/car/"):
        return True
    return False


async def main(page: ft.Page):
    page.title = "rentCarKom"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.DEEP_PURPLE_700,
            secondary=ft.Colors.INDIGO_500,
            surface=ft.Colors.WHITE,
        ),
    )
    page.window = ft.Window(min_width=380)
    page.fonts = {}

    DB.init()

    def route_change(e):
        route = page.route or "/"

        # Головна для всіх: гість одразу дивиться каталог
        if route in ("", "/"):
            asyncio.create_task(page.push_route("/home"))
            return

        if route.startswith("/admin"):
            if not AppState.is_logged_in():
                show_message(page, "Увійдіть, щоб відкрити цей розділ.", error=True)
                asyncio.create_task(page.push_route("/login"))
                return
            if route.startswith("/admin/add-car") and not AppState.is_admin():
                show_message(page, "Доступ лише для адміністратора.", error=True)
                asyncio.create_task(page.push_route("/home"))
                return
            if route.startswith("/admin/rentals") and not AppState.is_manager_or_admin():
                show_message(page, "Недостатньо прав для цього розділу.", error=True)
                asyncio.create_task(page.push_route("/home"))
                return
        elif not _is_guest_allowed(route):
            if not AppState.is_logged_in():
                show_message(page, "Увійдіть або переглядайте каталог як гість.", error=True)
                asyncio.create_task(page.push_route("/home"))
                return

        page.views.clear()

        try:
            if route == "/home":
                page.views.append(HomeView(page).build())
            elif route == "/login":
                page.views.append(LoginView(page).build())
            elif route.startswith("/car/"):
                car_id = route.removeprefix("/car/").strip()
                if not car_id:
                    show_message(page, "Некоректне посилання на авто.", error=True)
                    asyncio.create_task(page.push_route("/home"))
                    return
                page.views.append(HomeView(page).build())
                page.views.append(CarDetailView(page, car_id).build())
            elif route == "/admin/add-car":
                page.views.append(HomeView(page).build())
                page.views.append(AddCarView(page).build())
            elif route == "/admin/rentals":
                page.views.append(HomeView(page).build())
                page.views.append(RentalsView(page).build())
            else:
                show_message(page, "Сторінку не знайдено.", error=True)
                page.views.append(HomeView(page).build())
        except Exception as ex:
            show_message(page, f"Помилка: {ex!s}", error=True)
            page.views.append(HomeView(page).build())

        page.update()

    async def view_pop(e: ft.ViewPopEvent):
        if len(page.views) > 1:
            page.views.pop()
            top = page.views[-1]
            await page.push_route(top.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    if not page.route or page.route in ("", "/"):
        page.route = "/home"
    route_change(None)


_PORT = int(os.environ.get("PORT", "8080"))

ft.run(
    main,
    view=ft.AppView.WEB_BROWSER,
    port=_PORT,
    upload_dir="assets/uploads",
    assets_dir="assets",
)
