from typing import Optional, TypeVar, Generic, Dict, Any

T = TypeVar('T')

class Result(Generic[T]):
    def __init__(self, code: int, msg: Optional[str] = None, data: Optional[T] = None):
        self.code = code
        self.msg = msg
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }

    @staticmethod
    def success() -> 'Result[None]':
        return Result(code=1)

    @staticmethod
    def success_with_data(data: T) -> 'Result[T]':
        return Result(code=1, data=data)

    @staticmethod
    def error(msg: str) -> 'Result[None]':
        return Result(code=0, msg=msg)