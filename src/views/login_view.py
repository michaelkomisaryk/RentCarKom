"""
login_view.py — вхід / реєстрація з неоновим UI та надійною валідацією.
"""

import asyncio

import flet as ft

from src.database import DB
from src.neon_ui import neon_glow, neon_icon_display
from src.state import AppState
from src.theme import C
from src.ui_helpers import show_message


class LoginView:
    def __init__(self, page: ft.Page):
        self._page = page
        self._show_register = False

    def build(self) -> ft.View:
        cyan = C.CYAN
        pink = C.PINK

        name_field = ft.TextField(
            label="Повне ім'я",
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            border_color=ft.Colors.with_opacity(0.5, cyan),
            focused_border_color=pink,
            border_radius=12,
            cursor_color=cyan,
            visible=False,
        )
        email_field = ft.TextField(
            label="Email",
            prefix_icon=ft.Icons.EMAIL_OUTLINED,
            keyboard_type=ft.KeyboardType.EMAIL,
            border_color=ft.Colors.with_opacity(0.5, cyan),
            focused_border_color=pink,
            border_radius=12,
            cursor_color=cyan,
        )
        password_field = ft.TextField(
            label="Пароль",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.with_opacity(0.5, cyan),
            focused_border_color=pink,
            border_radius=12,
            cursor_color=cyan,
        )
        pwd_rules = ft.Text(
            "Пароль: ≥8 символів, латиниця A–Z і a–z, цифра, спецсимвол (!@#…)",
            size=11,
            color=ft.Colors.with_opacity(0.85, cyan),
            visible=False,
        )
        error_text = ft.Text("", color=C.PINK_SOFT, size=13, visible=False)

        title_text = ft.Text(
            "З поверненням",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=C.CYAN_SOFT,
        )
        subtitle_text = ft.Text(
            "Увійдіть у свій акаунт",
            size=14,
            color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
        )
        action_btn = ft.Button(
            content=ft.Text("Увійти", size=15, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.35, ft.Colors.DEEP_PURPLE_400),
                overlay_color=ft.Colors.with_opacity(0.2, pink),
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.Padding(0, 14, 0, 14),
                side=ft.BorderSide(1, cyan),
            ),
            expand=True,
        )
        toggle_btn = ft.TextButton(
            content=ft.Text("Немає акаунту? Зареєструватися", size=13, color=cyan),
            style=ft.ButtonStyle(overlay_color=ft.Colors.with_opacity(0.12, pink)),
        )

        async def do_login(_):
            error_text.visible = False
            email = (email_field.value or "").strip().lower()
            password = password_field.value or ""
            if not email or not password:
                error_text.value = "Заповніть усі поля."
                error_text.visible = True
                self._page.update()
                return
            user = DB.login(email, password)
            if user:
                AppState.login(user)
                await self._page.push_route("/home")
            else:
                error_text.value = "Невірний email або пароль."
                error_text.visible = True
                self._page.update()

        async def do_register(_):
            error_text.visible = False
            name = (name_field.value or "").strip()
            email = (email_field.value or "").strip().lower()
            password = password_field.value or ""
            if not name or not email or not password:
                error_text.value = "Заповніть усі поля."
                error_text.visible = True
                self._page.update()
                return
            ok, msg = DB.register(name, email, password)
            if ok:
                _toggle_mode(None)
                email_field.value = email
                password_field.value = ""
                show_message(self._page, "Реєстрація успішна! Тепер увійдіть.")
                self._page.update()
            else:
                error_text.value = msg
                error_text.visible = True
                self._page.update()

        def _toggle_mode(_):
            self._show_register = not self._show_register
            if self._show_register:
                title_text.value = "Новий акаунт"
                subtitle_text.value = "Заповніть дані — пароль перевіряється на надійність"
                name_field.visible = True
                pwd_rules.visible = True
                action_btn.content = ft.Text("Зареєструватися", size=15, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)
                action_btn.on_click = do_register
                toggle_btn.content = ft.Text("Вже є акаунт? Увійти", size=13, color=cyan)
            else:
                title_text.value = "З поверненням"
                subtitle_text.value = "Увійдіть у свій акаунт"
                name_field.visible = False
                pwd_rules.visible = False
                action_btn.content = ft.Text("Увійти", size=15, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)
                action_btn.on_click = do_login
                toggle_btn.content = ft.Text("Немає акаунту? Зареєструватися", size=13, color=cyan)
            error_text.visible = False
            self._page.update()

        action_btn.on_click = do_login
        toggle_btn.on_click = _toggle_mode

        logo = neon_icon_display(
            self._page,
            ft.Icons.DIRECTIONS_CAR,
            size=40,
            idle_color=cyan,
            hover_color=pink,
            padding=16,
        )

        form_card = ft.Container(
            content=ft.Column(
                controls=[
                    title_text,
                    subtitle_text,
                    ft.Container(height=16),
                    name_field,
                    email_field,
                    ft.Container(height=4),
                    password_field,
                    pwd_rules,
                    error_text,
                    ft.Container(height=8),
                    ft.Row(controls=[action_btn]),
                    ft.Container(height=4),
                    ft.Column(
                        controls=[toggle_btn],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
            border_radius=20,
            padding=ft.Padding(28, 28, 28, 28),
            border=ft.Border.all(1.5, ft.Colors.with_opacity(0.9, cyan)),
            shadow=neon_glow(cyan, strong=True),
        )

        body = ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1.4, -1),
                end=ft.Alignment(1.2, 1.4),
                colors=[
                    ft.Colors.BLACK,
                    ft.Colors.PURPLE_900,
                    ft.Colors.INDIGO_900,
                    ft.Colors.BLUE_GREY_900,
                ],
                stops=[0.0, 0.28, 0.62, 1.0],
            ),
            content=ft.Column(
                controls=[
                    ft.Container(height=36),
                    ft.Row(
                        controls=[
                            logo,
                            ft.Text(
                                "rentCarKom",
                                size=34,
                                weight=ft.FontWeight.BOLD,
                                color=C.CYAN_SOFT,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=14,
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=form_card,
                                width=400,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=12),
                    ft.TextButton(
                        content=ft.Text(
                            "← Продовжити як гість (перегляд каталогу)",
                            size=13,
                            color=ft.Colors.with_opacity(0.9, cyan),
                        ),
                        on_click=lambda e: asyncio.ensure_future(self._page.push_route("/home")),
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        "rentCarKom — оренда авто без зайвих клопотів",
                        size=13,
                        color=ft.Colors.with_opacity(0.65, ft.Colors.WHITE),
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=ft.Padding(16, 0, 16, 24),
        )

        return ft.View(
            route="/login",
            padding=0,
            bgcolor=ft.Colors.BLACK,
            controls=[body],
        )
