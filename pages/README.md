SafeRoad AI uses explicit sidebar navigation in `app.py`.

The page renderers live in `views/` so the app works consistently even when
Streamlit automatic page discovery is unavailable or launched from a different
working directory.
