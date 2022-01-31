from typing import List, Optional
from uuid import uuid4

from eventsourcing.domain import Aggregate, AggregateCreated, AggregateEvent


class Mapping(Aggregate):
    name: str
    aliases: List[str]
    description: str
    tasks: List[str]

    def __init__(self, name: str, aliases: List[str], description: str, tasks: List[str]):
        self.name = name
        self.aliases = aliases
        self.description = description
        self.tasks = tasks

    class Created(AggregateCreated):
        name: str
        aliases: List[str]
        description: str
        tasks: List[str]

    class TasksUpdatedEvent(AggregateEvent):
        tasks: List[str]

        def apply(self, aggregate: 'Mapping') -> None:
            aggregate.tasks = self.tasks

    class AliasesUpdatedEvent(AggregateEvent):
        aliases: List[str]

        def apply(self, aggregate: 'Mapping') -> None:
            aggregate.aliases = self.aliases

    @classmethod
    def create(cls, name: str, description: str, aliases: List[str], tasks: List[str]) -> 'Mapping':
        return cls._create(cls.Created, id=uuid4(), name=name, description=description, aliases=aliases, tasks=tasks)
