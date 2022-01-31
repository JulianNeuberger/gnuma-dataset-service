from typing import Optional, List
from uuid import UUID

from eventsourcing.system import Leader

from domain.mapping import Mapping


class Mappings(Leader):
    def create_mapping(self, name: str, description: Optional[str] = '',
                       aliases: List[str] = None, tasks: List[str] = None) -> UUID:
        if aliases is None:
            aliases = []

        if tasks is None:
            tasks = []

        mapping = Mapping.create(name, description, aliases, tasks)
        self.save(mapping)
        return mapping.id
