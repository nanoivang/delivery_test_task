# Написать алгоритм распределения заказов между курьерами, чтобы был приоритет в
# скорости доставки посылки клиентам.
# Входные параметры:
# ● Список заказов
#   ○ Параметры заказа:
#       ■ Гео-координаты точки А (Откуда)
#       ■ Гео-координаты точки Б (Куда)
#       ■ Стоимость заказа

# ● Список курьеров
#   ○ Параметры курьера:
#       ■ Гео-координаты курьера

# Предположим что курьеры двигаются с постоянной скоростью 1 и могут идти по самому короткому пути к цели (то есть по прямой линии от начала до конца).
# Курьерам будет назначены заказы и оптимальные пути развоза заказов для приоритизации времени доставки клиентам.

import math
from itertools import permutations

def shortest_path(point1, point2) -> float:
    """
        Функция принимает значения point1 [x1, y1], point2 [x2, y2]
        и возвращает кратчайший путь.
    """
    return math.dist(point1, point2)



def valid_permutation(permutation):
    """
        Валидатор перестановок, который проверяет чтобы координата конца не находилась раньше чем координата начала.
    """
    for i in range(len(permutation)):
        if permutation[i].startswith('end'):
            corresponding_start = 'start' + permutation[i][3:]
            if corresponding_start in permutation[i+1:]:
                return False
    return True

def generate_permutations(coords):
    """
        Функция генерирует все возможные перестановки координат. 
    """
    all_keys = list(coords.keys())
    all_keys.remove('start0')
    for permutation in permutations(all_keys):
        if valid_permutation(permutation):
            yield ["start0"] + list(permutation)

# Структура для заказа.

class Order: 
    def __init__(self, start : list[float], finish : list[float], price : float) -> None:
        self.start = start
        self.finish = finish
        self.price = price

    def __repr__(self):
        return f"Order Start: {self.start}, End: {self.finish}, Price: {self.price}"

# Нода заказа
class OrderItem:
    def __init__(self, data) -> None:
        self.data = data
        self.next = None

# Линкед лист для заказов.
class OrderList:
    def __init__(self) -> None:
        self.head = None
        self.fastest_path = []

    def append(self, data : Order):
        order_item = OrderItem(data)
        if not self.head:
            self.head = order_item
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = order_item

    def delete_order(self, data : Order):
        temp = self.head

        if temp is not None and temp.data == data:
            self.head = temp.next
            temp = None
            return

        while temp is not None:
            if temp.data == data:
                break
            prev = temp
            temp = temp.next

        if temp is None:
            return

        prev.next = temp.next
        temp = None

    
    def total_distance(self) -> float:
        result = 0
        current = self.head
        last_coordinates = current.data.start

        while current:
            result += shortest_path(last_coordinates, current.data.finish)
            last_coordinates = current.data.finish
            current = current.next
        
        return result
    
    def optimal_distance(self) -> float:
        if self.head.next is None:
            return self.total_distance()
        current = self.head
        coords = {}
        i = 0
        while current:
            coords[f"start{i}"] = current.data.start
            coords[f"end{i}"] = current.data.finish
            i += 1
            current = current.next

        min_distance = float('inf')
        for p in generate_permutations(coords):
            d = 0
            for i in range(len(p) - 1):
                d += shortest_path(coords[p[i]], coords[p[i + 1]])
            if min_distance > d:
                min_distance = d
                self.fastest_path = []
                for key in p:
                    self.fastest_path.append(coords[key])

        return min_distance


    def print_list(self):
        current = self.head
        while current:
            print(f"order start {current.data.start} end {current.data.finish} price {current.data.price}")
            current = current.next


class Courier: # Класс курьер содержит в себе свои заказы
    def __init__(self, location, id) -> None:
        self.location = location
        self.id = str(id)
        self.order_list = OrderList()

    def __repr__(self) -> str:
        return f"Courier {self.id}: with location {self.location}"
    
    def assign_order(self, order : Order):
        self.order_list.append(order)

    def print_orders(self):
        self.order_list.print_list()

    def remove_order(self, order : Order):
        self.order_list.delete_order(order)

    def have_order(self):
        return self.order_list.head is not None
    
    def travel_distance(self) -> float:
        if not self.have_order():
            return 0
        travel_distance = shortest_path(self.location, self.order_list.head.data.start)
        travel_distance += self.order_list.optimal_distance()

        return travel_distance
        
    
class CourierDispatcher: # Класс раздачи заказов курьерам и "регистрирующий курьеров"
    def __init__(self) -> None:
        self.__courier_count = 0
        self.__courier_list = []

    def register_courier(self, coordinates):
        result = Courier(coordinates, self.__courier_count)
        self.__courier_count += 1
        self.__courier_list.append(result)

        return result
    
    def register_couriers(self, data : list):
        for cour_data in data:
            self.__courier_list.append(Courier(cour_data, self.__courier_count))
            self.__courier_count += 1

    def assign_couriers(self, orders : list):
        """
            Функция назначает курьера для каждой доставки.
        """
        for courier in self.__courier_list:
            closest_order = min((order for order in orders if not courier.have_order()), key=lambda order: shortest_path(courier.location, order[0]) + shortest_path(order[0], order[1]))
            if closest_order:
                order = Order(*closest_order)
                courier.assign_order(order)
                orders.remove(closest_order)

        # если заказов больше чем курьеров ищем самого "быстрого курьера"
        for o in orders:
            order = Order(*o)
            minimal_dist = float('inf')
            fastest_cour = None
            for courier in self.__courier_list:
                courier.assign_order(order)
                cour_dist = courier.travel_distance()
                if minimal_dist > cour_dist:
                    minimal_dist = cour_dist
                    fastest_cour = courier
                courier.remove_order(order)
            
            fastest_cour.assign_order(order)
        
        for courier in self.__courier_list:
            print(f'courier {courier.id}')
            courier.print_orders()
            print(f'travels {courier.travel_distance()}')
            print(f"Fastest path: {courier.location} {courier.order_list.fastest_path} \n")
                    



if __name__ == "__main__":
    courier_disp = CourierDispatcher()

    courier_list = [[-15, 11], [-30, -13], [27, 34.5], [32, -10]]
    delivery_list = [[[-24, 16.5], [-13, 23.5], 1000], [[-30, 10], [-10, -5], 900], [[1, 3], [8,-8], 600], [[30, 10], [35, 5], 550], [[10, 10], [23, 33], 400], [[-17, -18], [10, -15], 123]]

    courier_disp.register_couriers(courier_list)
    courier_disp.assign_couriers(delivery_list)

