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

    def get_mapping(self, mapping_id: UUID) -> Mapping:
        return self.repository.get(mapping_id)

    def get_mappings(self, mapping_ids: List[UUID]) -> List[Mapping]:
        return [self.repository.get(mapping_id) for mapping_id in mapping_ids]
