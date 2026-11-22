# distributed_properties/lamport_clock.py
class LamportClock:
    def __init__(self):
        self.time = 0

    def tick(self):
        """Tăng thời gian trước khi gửi gói tin"""
        self.time += 1
        return self.time

    def update(self, received_time):
        """Cập nhật thời gian khi nhận gói tin"""
        self.time = max(self.time, received_time) + 1
        return self.time