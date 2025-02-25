from collections import defaultdict, deque
from dataclasses import dataclass
from itertools import count
from typing import Any, Self

import dukpy

from duty.vk.api import VkApi, VkApiResponseException


@dataclass(eq=True)
class MethodCall:
    method: str
    params: dict[str, Any]


@dataclass
class Message:
    id: int
    peer_id: int
    text: str


class UnexpectedCall(Exception):
    pass


class MethodNotSupported(Exception):
    pass


class FalseObject:
    def __bool__(self):
        return False

    def __getattr__(self, __name):
        return _false_obj

    def __getitem__(self, __name):
        return _false_obj


_false_obj = FalseObject()


class _Base(VkApi):
    _parent: 'Self | None' = None

    def as_cls(self):
        class TestVkApi_(TestVkApi):
            def __new__(cls, *args, **kwargs):
                api = type(self).__new__(cls)
                api._parent = self
                return api
        return TestVkApi_


class TestVkApi(_Base):
    _method_handlers = {}
    _next_message_id = count().__next__

    _messages_by_id: 'dict[int, Message]'
    _messages_by_peer: 'dict[int, list[Message]]'

    _known_users: 'dict[int, dict]'
    _known_user_tokens: 'dict[str, int]'
    _known_group_tokens: 'dict[str, int]'

    @classmethod
    def method_handler(cls, method: str):
        def decorator(func):
            cls._method_handlers[method] = func
        return decorator

    def __init__(
            self,
            access_token: str,
            version: str = "5.130"
    ):
        super().__init__(access_token, version)
        if not self._parent:
            self._messages_by_id = {}
            self._messages_by_peer = defaultdict(list)
            self._known_users = {}
            self._known_user_tokens = {}
            self._known_group_tokens = {}

    def __getattr__(self, __name: str):
        if self._parent:
            return getattr(self._parent, __name)
        return super().__getattr__(__name)

    def __call__(self, method, **kwargs) -> Any:
        if self.access_token not in self._known_user_tokens:
            raise VkApiResponseException({
                'error_code': 5,
                'error_msg': 'Invalid access token'
            })

        if method == 'execute':
            return self.handle_execute(method, kwargs['code'])

        handler = self._method_handlers.get(method)
        if handler is None:
            raise MethodNotSupported(method, kwargs)
        return handler(self, **kwargs)

    def handle_execute(self, method, code):
        def is_method_call(obj):
            return isinstance(obj, dict) and 'method' in obj

        def do_call(obj):
            return self(obj['method'], **obj.get('params', {}))

        def traverse(obj):
            if is_method_call(obj):
                return do_call(obj)
            if isinstance(obj, list):
                return [traverse(o) for o in obj]
            if isinstance(obj, dict):
                return {k: traverse(v) for k, v in obj.items()}
            return obj

        interpreter = dukpy.JSInterpreter()
        response = interpreter.evaljs('''
            var API = new Proxy({}, {
                get: function (target, groupName, receiver) {
                    return new Proxy({}, {
                        get: function (target, methodName, receiver) {
                            return function (params) {
                                return {
                                  'method': groupName + '.' + methodName,
                                  'params': params
                                }
                            }
                        }
                    });
                }
            });
            (function _() {
                %s
            })();
        ''' % code)
        return traverse(response)

    def add_user(
            self,
            user_id: int,
            token: 'str | None',
            name: 'tuple[str, str]'
    ):
        if token:
            self._known_user_tokens[token] = user_id
        self._known_users[user_id] = {
            "id": user_id,
			"first_name": name[0],
			"last_name": name[1],
			"can_access_closed": True,
			"is_closed": False
        }

    def add_message(
            self,
            message: Message
    ):
        self._messages_by_id[message.id] = message
        self._messages_by_peer[message.peer_id].append(message)

    def get_messages_from_peer(self, peer_id: int):
        return self._messages_by_peer[peer_id]


class ExpectTestVkApi(_Base):
    _expected_calls: 'deque[tuple[MethodCall, dict[str, Any]]]'

    def __init__(
            self,
            access_token: str,
            version: str = "5.130"
    ):
        super().__init__(access_token, version)
        if self._parent:
            self._expected_calls = self._parent._expected_calls
        else:
            self._expected_calls = deque()

    def __call__(self, method, **kwargs) -> Any:
        actual_call = MethodCall(method, kwargs)
        expected_call, response = self._expected_calls[0]
        if actual_call != expected_call:
            raise UnexpectedCall(actual_call, expected_call)
        self._expected_calls.popleft()
        return response

    def expect_call(self, call: MethodCall, response):
        self._expected_calls.append((call, response))


@TestVkApi.method_handler('users.get')
def users_get_handler(
    api: TestVkApi, *,
    user_ids=''
):
    if user_ids:
        raise MethodNotSupported()
    else:
        user_ids = [api._known_user_tokens[api.access_token]]

    response = []
    for uid in user_ids:
        if uid in api._known_users:
            response.append(api._known_users[uid])
    return response


@TestVkApi.method_handler('groups.getById')
def groups_get_by_id_handler(
    api: TestVkApi, *,
    group_ids=''
):
    if not group_ids:
        if api.access_token not in api._known_group_tokens:
            return False
    else:
        raise MethodNotSupported()


@TestVkApi.method_handler('messages.send')
def messages_send_handler(
    api: TestVkApi, *,
    message: str,
    peer_id: int,
    random_id=0,
):
    msg_obj = Message(
        id=api._next_message_id(),
        peer_id=peer_id,
        text=message,
    )
    api.add_message(msg_obj)
    return msg_obj.id
