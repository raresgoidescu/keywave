from queue import Queue

class EventQueue():
	def __init__(self):
		self.LOG_LEVEL = 0
		self.user_to_queue_map = {}


	def set_log_level(self, level: int) -> None:
		if level < 0:
			level = 0
		
		if level > 2:
			level = 2

		self.LOG_LEVEL = level


	def __get_queue(self, id: int) -> Queue:
		if id not in self.user_to_queue_map:
			self.user_to_queue_map[id] = Queue()

		return self.user_to_queue_map[id]


	def store(self, event: dict, uid: int) -> None:
		q = self.__get_queue(uid)

		q.put(event)

		if self.LOG_LEVEL >= 2:
			print(f'[INFO] New event for user \'{uid}\' stored in queue')
		

	def empty(self, uid: int) -> bool:
		q = self.__get_queue(uid)

		return q.qsize() == 0


	def pop_front(self, uid: int) -> dict | None:
		q = self.__get_queue(uid)

		if q.qsize() == 0:
			if self.LOG_LEVEL >= 1:
				print(f'[WARN] Trying to get message for user {uid} with empty queue')

			return None

		return q.get(block=False)