from typing import TypedDict


class RawChat(TypedDict):
    peer_id: int
    name: str
    installed: bool


class Chat:
    id: int
    name: str
    peer_id: int
    iris_id: str
    installed: bool

    def __init__(self, data: RawChat, iris_id: str):
        self.peer_id = data['peer_id']
        self.id = self.peer_id - 2000000000
        self.name = data.get('name', 'Чат не связан')
        self.iris_id = iris_id
        self.installed = data.get('installed', False)
