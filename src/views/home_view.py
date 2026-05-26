"""
home_view.py — Головна: каталог з фільтрами, сортуванням і пагінацією.
"""

from __future__ import annotations

import asyncio

import flet as ft

from src.catalog import CatalogQuery, query_catalog
from src.database import DB
from src.state import AppState
from src.components.header import build_header
from src.components.car_card import build_car_card
from src.components.sort_filter_bar import SortFilterBar


class HomeView:
    PAGE_SIZE = 6
    SEARCH_DEBOUNCE_MS = 280

    def __init__(self, page: ft.Page):
        self._page = page
        self._brand_search = ""
        self._pending_search = ""
        self._current_page = 1
        self._debounce_task: asyncio.Task | None = None
        self._cars_grid: ft.ResponsiveRow | None = None
        self._pagination_row: ft.Row | None = None
        self._results_label: ft.Text | None = None
        self._sort_bar: SortFilterBar | None = None

    def _build_query(self) -> CatalogQuery:
        bar = self._sort_bar
        return CatalogQuery(
            search=self._brand_search,
            fuel=bar.fuel if bar else "All",
            available_only=bar.available_only if bar else False,
            sort_field=bar.sort_field if bar else "price",
            sort_direction=bar.sort_direction if bar else "asc",
            page=self._current_page,
            page_size=self.PAGE_SIZE,
        )

    def _grid_columns(self):
        return {
            ft.ResponsiveRowBreakpoint.XS: 12,
            ft.ResponsiveRowBreakpoint.SM: 6,
            ft.ResponsiveRowBreakpoint.MD: 6,
            ft.ResponsiveRowBreakpoint.LG: 4,
        }

    def _refresh_list(self):
        if self._cars_grid is None:
            return

        result = query_catalog(self._build_query())
        col = self._grid_columns()

        if self._results_label:
            start = (result.page - 1) * result.page_size + 1 if result.total else 0
            end = min(result.page * result.page_size, result.total)
            self._results_label.value = (
                f"Показано {start}–{end} з {result.total}"
                if result.total
                else "Немає результатів"
            )

        if self._pagination_row:
            prev_btn = self._pagination_row.controls[0]
            next_btn = self._pagination_row.controls[2]
            page_lbl = self._pagination_row.controls[1]
            prev_btn.disabled = result.page <= 1
            next_btn.disabled = result.page >= result.total_pages
            page_lbl.value = f"Сторінка {result.page} / {result.total_pages}"

        if not result.items:
            self._cars_grid.controls = [
                ft.Container(
                    col=col,
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(ft.Icons.SEARCH_OFF, size=56, color=ft.Colors.BLUE_GREY_300),
                                ft.Text(
                                    "Немає авто за такими параметрами",
                                    color=ft.Colors.BLUE_GREY_600,
                                    size=15,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "Спробуйте змінити фільтри або сортування",
                                    color=ft.Colors.BLUE_GREY_400,
                                    size=13,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        padding=ft.Padding(36, 48, 36, 48),
                        alignment=ft.Alignment(0, 0),
                    ),
                )
            ]
        else:
            self._cars_grid.controls = [
                ft.Container(col=col, content=build_car_card(self._page, c))
                for c in result.items
            ]

        self._page.update()

    def _on_filters_change(self):
        self._current_page = 1
        self._refresh_list()

    def _schedule_search(self, value: str):
        self._pending_search = value

        async def _debounced():
            await asyncio.sleep(self.SEARCH_DEBOUNCE_MS / 1000)
            if self._pending_search == value:
                self._brand_search = value
                self._current_page = 1
                self._refresh_list()

        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()
        self._debounce_task = asyncio.create_task(_debounced())

    def _change_page(self, delta: int):
        q = self._build_query()
        result = query_catalog(q)
        new_page = max(1, min(result.total_pages, self._current_page + delta))
        if new_page != self._current_page:
            self._current_page = new_page
            self._refresh_list()

    def build(self) -> ft.View:
        header = build_header(self._page, title="rentCarKom", show_back=False)

        brand_search_field = ft.TextField(
            label="Марка, модель або номер",
            hint_text="Наприклад: Toyota, BMW…",
            dense=True,
            border_radius=12,
            prefix_icon=ft.Icons.SEARCH,
            border_color=ft.Colors.BLUE_GREY_200,
            focused_border_color=ft.Colors.DEEP_PURPLE_400,
            on_change=lambda e: self._schedule_search(e.control.value or ""),
        )

        avail_toggle = ft.Checkbox(
            label="Лише вільні",
            value=False,
            label_style=ft.TextStyle(size=13, color=ft.Colors.BLUE_GREY_800),
        )

        self._sort_bar = SortFilterBar(self._page, on_change=self._on_filters_change)
        filter_card = self._sort_bar.build(
            brand_search_field=brand_search_field,
            avail_toggle=avail_toggle,
        )

        self._cars_grid = ft.ResponsiveRow(spacing=12, run_spacing=12, controls=[])

        self._results_label = ft.Text("", size=13, color=ft.Colors.BLUE_GREY_600)

        def go_prev(_):
            self._change_page(-1)

        def go_next(_):
            self._change_page(1)

        prev_btn = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color=ft.Colors.DEEP_PURPLE_700,
            style=ft.ButtonStyle(bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.DEEP_PURPLE)),
            on_click=go_prev,
        )
        next_btn = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_color=ft.Colors.DEEP_PURPLE_700,
            style=ft.ButtonStyle(bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.DEEP_PURPLE)),
            on_click=go_next,
        )
        page_lbl = ft.Text("Сторінка 1 / 1", size=13, color=ft.Colors.BLUE_GREY_800, weight=ft.FontWeight.W_500)

        self._pagination_row = ft.Row(
            controls=[prev_btn, page_lbl, next_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
        )

        self._refresh_list()

        stats_row = ft.Container(visible=False)
        if AppState.is_manager_or_admin():
            all_cars = DB.get_cars()
            rented = sum(1 for c in all_cars if c["is_rented"])
            total_rentals = len(DB.get_rentals())

            def stat_box(label, value, color):
                return ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(str(value), size=22, weight=ft.FontWeight.BOLD, color=color),
                            ft.Text(label, size=11, color=ft.Colors.BLUE_GREY_600),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                    ),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    padding=ft.Padding(16, 12, 16, 12),
                    expand=True,
                    border=ft.Border.all(1, ft.Colors.BLUE_GREY_100),
                )

            stats_row = ft.Container(
                content=ft.Row(
                    controls=[
                        stat_box("Авто", len(all_cars), ft.Colors.INDIGO_600),
                        stat_box("В оренді", rented, ft.Colors.DEEP_ORANGE_500),
                        stat_box("Вільні", len(all_cars) - rented, ft.Colors.GREEN_600),
                        stat_box("Оренд (усі)", total_rentals, ft.Colors.AMBER_700),
                    ],
                    spacing=10,
                ),
                padding=ft.Padding(0, 4, 0, 8),
                visible=True,
            )

        def _go_add_car(_):
            asyncio.create_task(self._page.push_route("/admin/add-car"))

        def _go_rentals(_):
            asyncio.create_task(self._page.push_route("/admin/rentals"))

        add_car_fab = ft.Container(visible=False)
        if AppState.is_admin():
            add_car_fab = ft.Container(
                content=ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ADD_ROUNDED, color=ft.Colors.WHITE, size=24),
                            ft.Text(
                                "Додати авто",
                                color=ft.Colors.WHITE,
                                size=14,
                                weight=ft.FontWeight.W_600,
                            ),
                        ],
                        spacing=10,
                        tight=True,
                    ),
                    padding=ft.Padding(22, 14, 24, 14),
                    bgcolor=ft.Colors.DEEP_PURPLE_700,
                    border_radius=28,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=18,
                        color=ft.Colors.with_opacity(0.4, ft.Colors.DEEP_PURPLE_900),
                        offset=ft.Offset(0, 5),
                    ),
                    on_click=_go_add_car,
                    ink=True,
                    tooltip="Додати нове авто в каталог",
                ),
                right=20,
                bottom=24,
                visible=True,
            )

        mgr_btn = ft.Container(visible=False)
        if AppState.is_manager_or_admin():
            mgr_actions: list[ft.Control] = []
            if AppState.is_admin():
                mgr_actions.append(
                    ft.Button(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=18, color=ft.Colors.WHITE),
                                ft.Text("Додати авто", size=13, color=ft.Colors.WHITE),
                            ],
                            spacing=8,
                            tight=True,
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.DEEP_PURPLE_700,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.Padding(16, 10, 16, 10),
                        ),
                        on_click=_go_add_car,
                    )
                )
            mgr_actions.append(
                ft.Button(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LIST_ALT, size=18, color=ft.Colors.WHITE),
                            ft.Text("Всі оренди", size=13, color=ft.Colors.WHITE),
                        ],
                        spacing=8,
                        tight=True,
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.INDIGO_700,
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.Padding(16, 10, 16, 10),
                    ),
                    on_click=_go_rentals,
                )
            )
            mgr_btn = ft.Container(
                content=ft.Row(
                    controls=mgr_actions,
                    alignment=ft.MainAxisAlignment.END,
                    spacing=10,
                    wrap=True,
                ),
                padding=ft.Padding(0, 6, 0, 0),
                visible=True,
            )

        guest_banner = ft.Container(visible=not AppState.is_logged_in())
        if not AppState.is_logged_in():

            async def go_auth(_):
                await self._page.push_route("/login")

            guest_banner = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=ft.Colors.DEEP_PURPLE_700),
                        ft.Text(
                            "Ви переглядаєте каталог як гість. Увійдіть, щоб орендувати авто.",
                            size=13,
                            color=ft.Colors.BLUE_GREY_800,
                            expand=True,
                        ),
                        ft.TextButton("Увійти", on_click=go_auth),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(14, 12, 14, 12),
                bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.DEEP_PURPLE_200),
                border_radius=12,
                border=ft.Border.all(1, ft.Colors.DEEP_PURPLE_100),
                margin=ft.Margin(0, 0, 0, 10),
                visible=True,
            )

        scroll_body = ft.Container(
            content=ft.Column(
                controls=[
                    guest_banner,
                    filter_card,
                    stats_row,
                    mgr_btn,
                    ft.Container(height=8),
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Каталог авто",
                                size=20,
                                weight=ft.FontWeight.W_700,
                                color=ft.Colors.BLUE_GREY_900,
                            ),
                            ft.Container(expand=True),
                            self._results_label,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(height=8),
                    self._cars_grid,
                    ft.Container(height=12),
                    self._pagination_row,
                    ft.Container(height=88),
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            expand=True,
            padding=ft.Padding(16, 12, 16, 12),
        )

        return ft.View(
            route="/home",
            padding=0,
            bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.DEEP_PURPLE_900),
            controls=[
                ft.Column(
                    spacing=0,
                    expand=True,
                    controls=[
                        header,
                        ft.Stack(
                            expand=True,
                            controls=[
                                scroll_body,
                                add_car_fab,
                            ],
                        ),
                    ],
                )
            ],
        )
