
class VectorClock:

    def __init__(self, node_id, total_nodes):

        self.node_id = node_id
        self.total_nodes = total_nodes

        # Khoi tao Vector Clock
        self.vector = [0] * total_nodes

    def tick(self):

        """
        Tang phan tu cua Node hien tai truoc khi gui
        """

        self.vector[self.node_id] += 1

        return self.vector.copy()

    def update(self, received_vector):

        """
        Cap nhat Vector Clock khi nhan Token
        Lay gia tri lon nhat cua tung phan tu
        Sau do tang dong ho cua Node hien tai
        """

        if len(received_vector) != self.total_nodes:
            raise ValueError("Vector Clock khong hop le")

        for i in range(self.total_nodes):

            self.vector[i] = max(
                self.vector[i],
                received_vector[i]
            )

        self.vector[self.node_id] += 1

        return self.vector.copy()
