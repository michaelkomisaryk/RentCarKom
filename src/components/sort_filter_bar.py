from __future__ import annotations

from typing import Callable

import flet as ft

from src.catalog import SORT_LABELS, SortDirection, SortField

_ANIM = ft.Animation(220, ft.AnimationCurve.EASE_OUT)
_SORT_FIELDS: list[SortField] = ["price", "popularity", "newest", "rating", "availability"]


def _chip(
    label: str,
    *,
    active: bool,
    on_click: Callable,
    icon: str | None = None,
) -> ft.Container:
    color = ft.Colors.DEEP_PURPLE_600 if active else ft.Colors.BLUE_GREY_100
    text_color = ft.Colors.WHITE if active else ft.Colors.BLUE_GREY_800
    border_color = ft.Colors.DEEP_PURPLE_400 if active else ft.Colors.BLUE_GREY_200
    controls: list = []
    if icon:
        controls.append(ft.Icon(icon, size=14, color=text_color))
    controls.append(
        ft.Text(
            label,
            size=12,
            weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_500,
            color=text_color,
        )
    )
    return ft.Container(
        content=ft.Row(controls=controls, spacing=6, tight=True),
        padding=ft.Padding(12, 8, 12, 8),
        border_radius=20,
        bgcolor=color,
        border=ft.Border.all(1.5 if active else 1, border_color),
        shadow=ft.BoxShadow(
            blur_radius=10 if active else 4,
            color=ft.Colors.with_opacity(0.25 if active else 0.08, ft.Colors.DEEP_PURPLE),
            offset=ft.Offset(0, 2),
        )
        if active
        else None,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        on_click=on_click,
        ink=True,
    )


class SortFilterBar:
    def __init__(
        self,
        page: ft.Page,
        *,
        on_change: Callable[[], None],
        initial_fuel: str = "All",
        initial_available_only: bool = False,
        initial_sort: SortField = "price",
        initial_direction: SortDirection = "asc",
    ):
        self._page = page
        self._on_change = on_change
        self.fuel = initial_fuel
        self.available_only = initial_available_only
        self.sort_field: SortField = initial_sort
        self.sort_direction: SortDirection = initial_direction
        self._fuel_chips_row: ft.Row | None = None
        self._sort_chips_row: ft.Row | None = None
        self._dir_btn: ft.IconButton | None = None

    def _notify(self):
        self._on_change()

    def _set_sort(self, field: SortField):
        self.sort_field = field
        self._rebuild_sort_chips()
        self._notify()

    def _toggle_direction(self, _=None):
        self.sort_direction = "desc" if self.sort_direction == "asc" else "asc"
        self._update_dir_btn()
        self._notify()

    def _update_dir_btn(self):
        if self._dir_btn:
            asc = self.sort_direction == "asc"
            self._dir_btn.icon = ft.Icons.ARROW_UPWARD if asc else ft.Icons.ARROW_DOWNWARD
            self._dir_btn.tooltip = "За зростанням" if asc else "За спаданням"

    def _rebuild_sort_chips(self):
        if not self._sort_chips_row:
            return
        sort_icons = {
            "price": ft.Icons.ATTACH_MONEY,
            "popularity": ft.Icons.TRENDING_UP,
            "newest": ft.Icons.NEW_RELEASES,
            "rating": ft.Icons.STAR,
            "availability": ft.Icons.CHECK_CIRCLE_OUTLINE,
        }
        self._sort_chips_row.controls = [
            _chip(
                SORT_LABELS[f],
                active=self.sort_field == f,
                icon=sort_icons.get(f),
                on_click=lambda e, field=f: self._set_sort(field),
            )
            for f in _SORT_FIELDS
        ]
        self._page.update()

    def _set_fuel(self, fuel: str):
        self.fuel = fuel
        self._rebuild_fuel_chips()
        self._notify()

    def _set_available(self, value: bool):
        self.available_only = value
        self._notify()

    def _rebuild_fuel_chips(self):
        if not self._fuel_chips_row:
            return
        fuels = [
            ("All", "Усі", None),
            ("Gasoline", "Бензин", ft.Icons.LOCAL_GAS_STATION),
            ("Diesel", "Дизель", ft.Icons.OIL_BARREL),
            ("Hybrid", "Гібрид", ft.Icons.ECO),
            ("Electric", "Електро", ft.Icons.ELECTRIC_BOLT),
        ]
        self._fuel_chips_row.controls = [
            _chip(label, active=self.fuel == key, icon=icon, on_click=lambda e, k=key: self._set_fuel(k))
            for key, label, icon in fuels
        ]
        self._page.update()

    def build(self, *, brand_search_field: ft.TextField, avail_toggle: ft.Checkbox) -> ft.Container:
        self._dir_btn = ft.IconButton(
            icon=ft.Icons.ARROW_UPWARD,
            icon_color=ft.Colors.DEEP_PURPLE_700,
            tooltip="За зростанням",
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.DEEP_PURPLE),
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=self._toggle_direction,
        )
        self._update_dir_btn()

        def on_avail(e: ft.ControlEvent):
            self._set_available(bool(e.control.value))

        avail_toggle.on_change = on_avail
        self._fuel_chips_row = ft.Row(spacing=8, wrap=True, run_spacing=8)
        self._rebuild_fuel_chips()
        self._sort_chips_row = ft.Row(spacing=8, wrap=True, run_spacing=8)
        self._rebuild_sort_chips()

        filter_panel = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.TUNE, color=ft.Colors.DEEP_PURPLE_500, size=22),
                            ft.Text(
                                "Фільтри та сортування",
                                size=17,
                                weight=ft.FontWeight.W_700,
                                color=ft.Colors.BLUE_GREY_900,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(content=brand_search_field, animate_opacity=_ANIM),
                    ft.Text("Паливо", size=12, color=ft.Colors.BLUE_GREY_600, weight=ft.FontWeight.W_500),
                    self._fuel_chips_row,
                    ft.Row(controls=[avail_toggle]),
                    ft.Divider(height=1, color=ft.Colors.BLUE_GREY_100),
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Сортування",
                                size=12,
                                color=ft.Colors.BLUE_GREY_600,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Container(expand=True),
                            self._dir_btn,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self._sort_chips_row,
                ],
                spacing=12,
            ),
            padding=ft.Padding(20, 18, 20, 18),
            bgcolor=ft.Colors.with_opacity(0.92, ft.Colors.WHITE),
            blur=ft.Blur(8, 8, ft.BlurTileMode.CLAMP),
            border_radius=18,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.DEEP_PURPLE_200)),
            shadow=ft.BoxShadow(
                blur_radius=20,
                color=ft.Colors.with_opacity(0.12, ft.Colors.DEEP_PURPLE),
                offset=ft.Offset(0, 4),
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )
        return filter_panel
