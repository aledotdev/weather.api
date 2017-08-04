import os

from .common import *

env = os.getenv('ENV', 'local')

if env == 'local':
    from .local import *
elif env == 'dev':
    from .dev import *
elif env == 'prod':
    from .prod import *
