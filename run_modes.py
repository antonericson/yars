import automatic_mode
import interactive_mode

DEFAULT = {
    'name': 'Automatic (default)',
    'callback': automatic_mode.default
}

PREVIEW = {
    'name': 'Preview mode',
    'callback': automatic_mode.preview
}

INTERACTIVE = {
    'name': 'Interactive mode',
    'callback': interactive_mode.run
}

ALL_OPTIONS = [DEFAULT, PREVIEW, INTERACTIVE]
