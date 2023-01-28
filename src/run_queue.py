from typing import TypeVar, Generic, List, Callable, Tuple, Union
from threading import Lock, Semaphore

T = TypeVar('T')

class RunQueue(Generic[T]):

    def __init__(self):
        self.items: List[T] = []
        self.items_lock = Lock()
        self.queue_sem = Semaphore(0)
    
    def put(self, value: T):
        with self.items_lock:
            self.queue_sem.release()
            self.items.append(value)
    
    def get(self) -> T:
        self.queue_sem.acquire()
        with self.items_lock:
            return self.items.pop(0)

    def positionOf(self, recognize: Callable[[T], bool]) -> Union[Tuple[int, int], None]:
        with self.items_lock:
            for index, item in enumerate(self.items):
                if recognize(item):
                    return (index + 1, len(self.items))
            return None 