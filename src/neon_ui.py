"""
neon_ui.py — неонова обводка, світіння та hover (масштаб + колір) для іконок.
"""

from __future__ import annotations

import flet as ft
from flet.controls.control_event import ControlEvent


def neon_card_glow(color: str, *, strong: bool) -> list[ft.BoxShadow]:
    """Multi-layer glow for premium car cards (transform-only hover friendly)."""
    blur = 28 if strong else 14
    return [
        ft.BoxShadow(
            spread_radius=2 if strong else 0,
            blur_radius=blur,
            color=ft.Colors.with_opacity(0.55 if strong else 0.3, color),
            offset=ft.Offset(0, 0),
        ),
        ft.BoxShadow(
            blur_radius=blur + 12,
            color=ft.Colors.with_opacity(0.2 if strong else 0.1, color),
            offset=ft.Offset(0, 4),
        ),
    ]


def neon_glow(color: str, *, strong: bool) -> list[ft.BoxShadow]:
    blur = 18 if strong else 10
    spread = 1 if strong else 0
    opacity = 0.75 if strong else 0.45
    return [
        ft.BoxShadow(
            spread_radius=spread,
            blur_radius=blur,
            color=ft.Colors.with_opacity(opacity, color),
            offset=ft.Offset(0, 0),
        ),
        ft.BoxShadow(
            spread_radius=0,
            blur_radius=blur + 8,
            color=ft.Colors.with_opacity(0.25 if strong else 0.12, color),
            offset=ft.Offset(0, 2),
        ),
    ]


def neon_icon_display(
    page: ft.Page,
    icon,
    *,
    size: int = 32,
    idle_color: str | None = None,
    hover_color: str | None = None,
    padding: int = 14,
) -> ft.Container:
    """Декоративна іконка з неоновою рамкою та реакцією на наведення."""
    idle_color = idle_color or ft.Colors.CYAN_ACCENT_200
    hover_color = hover_color or idle_color
    ic = ft.Icon(icon=icon, size=size, color=idle_color)

    def on_hover(e: ControlEvent):
        w = e.control
        inner = w.content
        h = bool(e.data)
        inner.color = hover_color if h else idle_color
        inner.size = int(size * 1.14) if h else size
        w.border = ft.Border.all(2 if h else 1, hover_color if h else idle_color)
        w.shadow = neon_glow(hover_color if h else idle_color, strong=h)
        w.bgcolor = ft.Colors.with_opacity(0.22 if h else 0.1, idle_color)
        w.scale = ft.Scale(1.06 if h else 1.0)
        page.update()

    return ft.Container(
        content=ic,
        width=size + padding * 2,
        height=size + padding * 2,
        alignment=ft.Alignment(0, 0),
        border_radius=size + padding,
        border=ft.Border.all(1, idle_color),
        bgcolor=ft.Colors.with_opacity(0.1, idle_color),
        shadow=neon_glow(idle_color, strong=False),
        scale=ft.Scale(1.0),
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        on_hover=on_hover,
    )


def neon_icon_button(
    page: ft.Page,
    icon,
    *,
    on_click,
    tooltip: str = "",
    idle_ring: str | None = None,
    hover_ring: str | None = None,
    icon_idle: str = ft.Colors.WHITE,
    icon_hover: str | None = None,
    base_size: int = 22,
) -> ft.Container:
    """IconButton у неоновій обводці з hover-анімацією."""
    idle_ring = idle_ring or ft.Colors.CYAN_ACCENT_400
    hover_ring = hover_ring or ft.Colors.PINK_ACCENT_200
    icon_hover = icon_hover or ft.Colors.CYAN_100
    btn = ft.IconButton(
        icon=icon,
        icon_color=icon_idle,
        icon_size=base_size,
        tooltip=tooltip,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.with_opacity(0.14, idle_ring),
            overlay_color=ft.Colors.with_opacity(0.12, hover_ring),
            shape=ft.RoundedRectangleBorder(radius=14),
        ),
        on_click=on_click,
    )

    def on_hover(e: ControlEvent):
        w = e.control
        b = w.content
        h = bool(e.data)
        b.icon_color = icon_hover if h else icon_idle
        b.icon_size = int(base_size * 1.12) if h else base_size
        w.border = ft.Border.all(2 if h else 1, hover_ring if h else idle_ring)
        w.shadow = neon_glow(hover_ring if h else idle_ring, strong=h)
        w.scale = ft.Scale(1.05 if h else 1.0)
        page.update()

    return ft.Container(
        content=btn,
        padding=2,
        border_radius=18,
        border=ft.Border.all(1, idle_ring),
        shadow=neon_glow(idle_ring, strong=False),
        scale=ft.Scale(1.0),
        animate_scale=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
        on_hover=on_hover,
    )
