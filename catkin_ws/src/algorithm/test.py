from Pytorch_DRL.HNRN import test_real_car
from Pytorch_DRL.HNRN import utils

def alg_inference(car_poses, car_targets, car_index, agent_num, LASER_RANGE, ROBOT_LENGTH):
    car_state = []
    for i in range(agent_num):
        temp_state = test_real_car.state_struct([float("inf") for _ in range(360)], car_poses[i][0], car_poses[i][1], car_poses[i][2], car_targets[i][0], car_targets[i][1])
        car_state.append(temp_state)
    car_state = utils.generate_laser_from_pos(car_state, LASER_RANGE, ROBOT_LENGTH)
    action = test_real_car.inference(car_state[car_index])
    # if car_index == 3:
    #     action[0] = action[0] * 0.8
    if abs(action[0]) < 1.0/14:
        action[0] = (1.0/14 + 0.001 if(action[0]>0) else -1.0/14 - 0.001)
    if utils.distance(car_poses[car_index][0], car_poses[car_index][1], car_targets[car_index][0], car_targets[car_index][1]) < 0.4:
        action = (0.0, 0.0)
        # rospy.loginfo("RigidBody0%d[RL algorithm]: Action linear = %f, angular = %f.", car_index+1, action[0], action[1])
    return action