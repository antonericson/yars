import automatic_generation
import interactive_mode

DEFAULT = {
    'name': 'Automatic (default)',
    'callback': automatic_generation.default
}

PREVIEW = {
    'name': 'Preview mode',
    'callback': automatic_generation.preview
}

INTERACTIVE = {
    'name': 'Interactive mode',
    'callback': interactive_mode.run
}

ALL_OPTIONS = [DEFAULT, PREVIEW, INTERACTIVE]
