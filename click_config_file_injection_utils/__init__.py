"""Public exports for click-config-file-injection-utils."""

from importlib import metadata

from click_config_file_injection_utils.injection import (
    MissingToolSectionError,
    injectDefaultOptionsFromToml,
)

__version__ = metadata.version('click-config-file-injection-utils')

__all__ = [
    'MissingToolSectionError',
    '__version__',
    'injectDefaultOptionsFromToml',
]
