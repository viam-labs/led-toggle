from typing import (Any, ClassVar, Dict, Final, List, Mapping, Optional,
                    Sequence, Tuple)

from typing_extensions import Self
from viam.components.generic import *
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import Geometry, ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes

from typing import cast
from viam.components.board import Board

class Toggler(Generic, EasyResource):
    # To enable debug-level logging, either run viam-server with the --debug option,
    # or configure your resource/machine to display debug logs.
    MODEL: ClassVar[Model] = Model(ModelFamily("naomi", "led-toggle"), "toggler")
    board_name: str
    board: Board
    local_board: Board
    pin: str

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Generic component.
        The default implementation sets the name from the `config` parameter.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both required and optional)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(
        cls, config: ComponentConfig
    ) -> Tuple[Sequence[str], Sequence[str]]:
        fields = config.attributes.fields
        if "board_name" not in fields:
            raise Exception("missing required board_name attribute")
        elif not fields["board_name"].HasField("string_value"):
            raise Exception("board_name must be a string")
        board_name = fields["board_name"].string_value
        if not board_name:
            raise ValueError("board_name cannot be empty")
        if "pin" not in fields:
            raise Exception("missing required pin attribute")
        elif not fields["pin"].HasField("string_value"):
            raise Exception("pin must be a string")
        pin = fields["pin"].string_value
        if not pin:
            raise ValueError("pin cannot be empty")
        # Return the board as a required dependency (just the name, not the full ResourceName)
        req_deps = [board_name]
        return req_deps, []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        self.board_name = config.attributes.fields["board_name"].string_value
        board_resource_name = Board.get_resource_name(self.board_name)
        board_resource = dependencies[board_resource_name]
        self.local_board = cast(Board, board_resource)
        self.pin = config.attributes.fields["pin"].string_value
        return super().reconfigure(config, dependencies)

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, ValueTypes]:
        result = {key: False for key in command.keys()}
        for name, args in command.items():
            if name == "action" and args == "toggle":
                pin = await self.local_board.gpio_pin_by_name(name=self.pin)
                high = await pin.get()
                if high:
                    await pin.set(high=False)
                else:
                    await pin.set(high=True)
                result[name] = True
        return result

    async def get_geometries(
        self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None
    ) -> Sequence[Geometry]:
        self.logger.error("`get_geometries` is not implemented")
        raise NotImplementedError()

