import automatic_mode
import interactive_mode

LEGACY = {
    'name': 'Legacy mode (automatic)',
    'callback': automatic_mode.default
}

PREVIEW = {
    'name': 'Front End dev mode',
    'callback': automatic_mode.preview
}

INTERACTIVE = {
    'name': 'Interactive mode',
    'callback': interactive_mode.run
}

ALL_OPTIONS = [INTERACTIVE, PREVIEW, LEGACY]
