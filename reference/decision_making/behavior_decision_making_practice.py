"""
Behavior Decision-Making Module Practice
"""

import sys
from enum import Enum

import numpy as np


# TODO (1-1) / (2-1)
class BehaviorState(Enum):
    pass


class BehaviorDecisionMaking:
    actions = {"LANE_LEFT": 0, "IDLE": 1, "LANE_RIGHT": 2, "FASTER": 3, "SLOWER": 4}
    lane_width: float = 4.0
    vehicle_length: float = 5.0

    def __init__(self, sampling_time, target_headway_time=2, safety_ttc=4):
        self.sampling_time = sampling_time
        self.target_headway_time: float = target_headway_time
        self.safety_ttc: float = safety_ttc

        self.ego_vehicle: np.ndarray = np.array([])
        self.ego_current_lane: int = 0

        self.current_front_vehicle: np.ndarray = np.array([])
        self.left_front_vehicle: np.ndarray = np.array([])
        self.left_rear_vehicle: np.ndarray = np.array([])

        self.behavior_state: BehaviorState = BehaviorState.LANE_KEEPING

    def update(self, obs, step) -> int:
        self.update_ego_vehicle(obs)
        self.update_surrounding_vehicles(obs)

        self.decide_behavior()
        print(f"[{step * self.sampling_time:.2f} sec] position {self.ego_vehicle[1]:.2f} {-self.ego_vehicle[2]:.2f} / "
              f"velocity {self.ego_vehicle[3]:.2f} / {self.behavior_state}")

        return self.plan_action_command()

    def update_ego_vehicle(self, obs):
        self.ego_vehicle = obs[0]
        self.ego_current_lane = self.find_current_lane(self.ego_vehicle)

    def update_surrounding_vehicles(self, obs):
        # 전방 차량
        front_vehicles = [vehicle for vehicle in obs[1:] if vehicle[0] == 1 and vehicle[1] >= self.ego_vehicle[1]]

        current_front_vehicles = [vehicle for vehicle in front_vehicles if
                                  self.find_current_lane(vehicle) == self.ego_current_lane]
        self.current_front_vehicle = self.find_closest_vehicle(current_front_vehicles)

        left_front_vehicles = [vehicle for vehicle in front_vehicles if
                               self.find_current_lane(vehicle) == self.ego_current_lane - 1]
        self.left_front_vehicle = self.find_closest_vehicle(left_front_vehicles)

        # 후방 차량
        rear_vehicles = [vehicle for vehicle in obs[1:] if vehicle[0] == 1 and vehicle[1] < self.ego_vehicle[1]]

        left_rear_vehicles = [vehicle for vehicle in rear_vehicles if
                              self.find_current_lane(vehicle) == self.ego_current_lane - 1]
        self.left_rear_vehicle = self.find_closest_vehicle(left_rear_vehicles)

    def find_current_lane(self, vehicle) -> int:
        return int((vehicle[2] + self.lane_width / 2) // self.lane_width) + 1

    def find_closest_vehicle(self, vehicles: list) -> np.ndarray:
        if not vehicles:
            return np.array([])

        return min(vehicles, key=lambda vehicle: abs(vehicle[1] - self.ego_vehicle[1]))

    # TODO (1-2) / (2-2)
    def decide_behavior(self):
        """현재 차량의 주행 상황에 따라 Behavior 를 결정"""
        pass

    # TODO (1-3)
    def decide_reducing_speed(self, front_vehicle: np.ndarray) -> bool:
        """threshold headway time 보다 짧은 경우 감속하도록 판단"""
        pass

    # TODO (2-3)
    def decide_lane_change(self):
        """현재 차선의 위치와, 주행 효율, 안전을 고려하여 차선 변경 여부를 결정"""
        pass

    # TODO (2-4)
    def decide_discretionary_lane_change(self) -> bool:
        """MOBIL 을 단순화 하여, 현재 차선의 선행 차량이 감속하고, 왼쪽 차선의 선행 차량이 감속하지 않는 경우 차선 변경"""
        pass

    # TODO (2-5)
    def check_lane_change_safety(self):
        """왼쪽 차선의 후방 차량과 전방 차량과의 ttc 가 safety ttc 보다 큰 경우 차선 변경"""
        pass

    def calculate_headway_time(self, front_vehicle, rear_vehicle) -> float:
        relative_distance = front_vehicle[1] - rear_vehicle[1] - self.vehicle_length
        return relative_distance / rear_vehicle[3]

    def calculate_ttc(self, front_vehicle, rear_vehicle) -> float:
        relative_distance = front_vehicle[1] - rear_vehicle[1] - self.vehicle_length
        relative_velocity = rear_vehicle[3] - front_vehicle[3]
        if relative_distance <= 0:
            # 충돌 상황으로 ttc 를 0 으로 설정
            return 0
        elif relative_velocity <= 0:
            # 후방 차량이 전방 차량보다 속도가 느리므로, 충돌하지 않으므로 최대값으로 설정
            return sys.float_info.max
        else:
            return relative_distance / relative_velocity

    # TODO (1-4) / (2-6)
    def plan_action_command(self) -> int:
        """Behavior 에 따라 Action Command 를 결정"""
