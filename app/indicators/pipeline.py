"""
Indicator pipeline.
"""

from app.indicators.registry import (
    create_overlay,
    create_panel,
)
from app.models import (
    Candle,
    IndicatorSpec,
    OverlayIndicator,
    PanelIndicator,
)


def build_indicators(
    candles: list[Candle],
    overlays: list[IndicatorSpec] | None = None,
    panels: list[IndicatorSpec] | None = None,
) -> tuple[
    list[OverlayIndicator],
    list[PanelIndicator],
]:
    """
    Compute all indicators.
    """

    overlay_models: list[OverlayIndicator] = []
    panel_models: list[PanelIndicator] = []

    for spec in overlays or []:

        overlay_models.append(
            create_overlay(
                name=spec.name,
                func=spec.func,
                candles=candles,
                color=spec.color,
                linewidth=spec.linewidth,
                linestyle=spec.linestyle,
                plot_type=spec.plot_type,
                marker=spec.marker,
                **spec.kwargs,
            )
        )

    for spec in panels or []:

        panel_models.append(
            create_panel(
                name=spec.name,
                func=spec.func,
                candles=candles,
                color=spec.color,
                linewidth=spec.linewidth,
                linestyle=spec.linestyle,
                plot_type=spec.plot_type,
                marker=spec.marker,
                **spec.kwargs,
            )
        )

    return overlay_models, panel_models