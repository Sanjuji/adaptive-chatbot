
# Lazy imports for heavy modules
from intelligent_import_optimizer import lazy_import

# Lazy load heavy modules
numpy = lazy_import('numpy')
pandas = lazy_import('pandas') 
matplotlib = lazy_import('matplotlib')
sklearn = lazy_import('sklearn')
