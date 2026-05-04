"""Simple temporal smoothing for noisy GPS fixes."""

from __future__ import annotations


class LowPassFilter:
    """Exponential low-pass: y[n] = alpha * x[n] + (1-alpha) * y[n-1]."""

    def __init__(
        self,
        alpha: float,
        initial_lat: float | None = None,
        initial_lon: float | None = None,
    ) -> None:
        if not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be in (0, 1]")
        self.alpha = alpha
        self._lat = initial_lat
        self._lon = initial_lon

    def reset(self, lat_deg: float | None = None, lon_deg: float | None = None) -> None:
        """Clear state or seed with a fix."""
        self._lat = lat_deg
        self._lon = lon_deg

    def filter_point(self, lat_deg: float, lon_deg: float) -> tuple[float, float]:
        """Return smoothed (lat, lon)."""
        if self._lat is None or self._lon is None:
            self._lat = lat_deg
            self._lon = lon_deg
            return lat_deg, lon_deg
        a = self.alpha
        self._lat = a * lat_deg + (1.0 - a) * self._lat
        self._lon = a * lon_deg + (1.0 - a) * self._lon
        return self._lat, self._lon
