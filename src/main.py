import asyncio
from viam.module.module import Module
try:
    from models.toggler import Toggler
except ModuleNotFoundError:
    # when running as local module with run.sh
    from .models.toggler import Toggler


if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())
