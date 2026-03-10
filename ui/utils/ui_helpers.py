# =====================================================
# APPLY STYLE TO MULTIPLE WIDGETS
# =====================================================
def apply_style(widgets, style):
    """
    Apply stylesheet to list of widgets
    """
    for w in widgets:
        if w:
            w.setStyleSheet(style)


# =====================================================
# CLEAR MULTIPLE INPUTS
# =====================================================
def clear_inputs(widgets):
    for w in widgets:
        try:
            w.clear()
        except Exception:
            pass


# =====================================================
# ENABLE / DISABLE WIDGETS
# =====================================================
def set_enabled(widgets, enabled=True):
    for w in widgets:
        w.setEnabled(enabled)