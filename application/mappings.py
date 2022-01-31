from typing import Optional, List
from uuid import UUID

from eventsourcing.application import Application

from domain.mapping import Mapping


class Mappings(Application):
    def create_mapping(self, name: str, description: Optional[str] = '',
                       aliases: List[str] = None, tasks: List[str] = None) -> UUID:
        if aliases is None:
            aliases = []

        if tasks is None:
            tasks = []

        mapping = Mapping.create(name, description, aliases, tasks)
        self.save(mapping)
        return mapping.id
