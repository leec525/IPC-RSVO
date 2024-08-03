# 此文件用于生成相机运动轨迹
# version: 2024-07-10
# author: <LiChen>

import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from mpl_toolkits.mplot3d import Axes3D

# 设置插值间隔
interval_frame = 5
interval_row = 480  # 图像行数

# 创建输出目录
output_dir = 'output_frames'
os.makedirs(output_dir, exist_ok=True)

# 读取控制点
# input_file = 'saved_control_points.txt'
# control_points = np.loadtxt(input_file, delimiter=',')

# Step 1: 手动设置基本控制点
# 本轨迹大致需要50个控制点
# （曹t1轨迹手动设置的基本控制点为141，t2为146个
# 相同类型速度的插值路标点的间隔相同，快速、中速、慢速对应的插值间隔分别为5,10,20
# 由帧控制点到最终卷帘渲染帧之间的插值数为480）
control_points = np.array([
    # [transx, transy, transz, rotx, roty, rotz]
    [0, 150, 20, 20, 0, 0],       #起点，要先运动一段进行初始化
    [-20, 150, 20, 20, 0, 0],     #向左运动
    [-40, 150, 20, 20, 0, 0],
    [-60, 150, 20, 20, 0, 0],     #拐点
    [-50, 150, 20, 20, 0, 0],     #向右运动
    [-30, 150, 20, 20, 0, 0],
    [-10, 150, 20, 20, 0, 0],     #拐点
    [-30, 150, 20, 20, 0, 0],     #向左运动
    [-50, 150, 20, 20, 0, 0],
    [-70, 150, 20, 20, 0, 0],
    [-80, 150, 20, 20, 0, 0],     #拐点，相机开始摇头
    [-80, 150, 20, 20, 0, 20],
    [-80, 150, 20, 20, 0, -20],
    [-80, 150, 20, 20, 0, 0],     #初始化运动结束，相机运动开始
    [-70, 150, 20, 20, 0, 0],     #向右运动
    [-60, 150, 20, 20, 0, 0],
    [-40, 150, 20, 20, 0, 0],
    [-30, 150, 20, 22, 0, 0],     #拐点1
    [-20, 151, 40, 25, 0, 0],     
    [-20, 153, 60, 30, 0, 0],
    [-20, 152, 80, 35, -10, 0],
    [-20, 151, 90, 30, -5, 0],
    [-20, 150, 100, 20, 10, 0],   #拐点2
    [0, 149, 100, 35, 10, 0],
    [20, 148, 100, 30, 0, 0],    #拐点3
    [20, 149, 90, 20, 0, 0],
    [20, 150, 80, 20, 50, 0],
    [20, 150, 70, 20, 90, 0],
    [20, 149, 60, 10, 120, 0],
    [20, 148, 40, 10, 180, 0],
    [20, 148, 30, 5, 150, 0],
    [20, 149, 20, 3, 120, 0],      #拐点4
    [30, 150, 20, 2, 90, -1],
    [40, 150, 20, 1.5, 90, -1],
    [60, 150, 20, 1, 90, -2],
    [80, 150, 20, 0, 130, 0],     #拐点5
    [80, 151, 10, 0, 140, 0],
    [80, 152, 0, 0, 150, 0],
    [80, 151, -10, 0, 160, 0],
    [80, 150, -20, 0, 180, 0],    #拐点6
    [60, 150, -20, 0, 180, 0],
    [40, 149, -20, 0, 180, 0],
    [30, 148, -20, 2, 180, 1],
    [20, 149, -20, 2, 180, 2],    #拐点7
    [20, 150, -40, 3, 180, 3],
    [20, 150, -60, 4, 180, 3],
    [20, 150, -80, 5, 180, 1],
    [20, 150, -100, 5, 180, 0],    #拐点8
    [0, 150, -100, 8, 180, 0],
    [-20, 150, -100, 10, 180, -1], #拐点9
    [-20, 151, -80, 12, 190, -3],
    [-20, 152, -70, 10, 200, -2],  
    [-20, 152, -60, 8, 190, -1],  
    [-20, 151, -40, 5, 180, 0],  
    [-20, 150, -20, 3, 200, 0],    #拐点10
    [-40, 150, -20, 1, 240, 0],
    [-50, 150, -20, 1, 240, 0],
    [-60, 149, -20, 0, 270, 0],
    [-70, 148, -20, 0, 270, -2],
    [-80, 148, -20, 0, 270, -5],    #拐点11
    [-80, 148, -10, 0, 280, -3],
    [-80, 148, 0, 10, 300, 0],
    [-80, 149, 10, 15, 330, 2],
    [-80, 150, 20, 20, 360, 5],
    [-60, 150, 20, 20, 360, 2],
    [-50, 150, 20, 20, 360, 0],     #终点12
])

# 设置随机数种子以便复现
# np.random.seed(42)

# # 生成控制点数量
# num_points = 50

# # 限定运动范围
# x_range = 300  # 3米
# y_range = 300  # 3米
# z_range = 50   # 0.5米
# rot_range_xy = np.pi / 4  # xy平面内旋转角度45度
# rot_range_z = np.pi / 18  # z方向上旋转角度10度

# # 生成随机平移和旋转
# translations = np.cumsum(np.random.uniform(-x_range / num_points, x_range / num_points, (num_points, 1)), axis=0)
# translations = np.hstack((translations, 
#                           np.cumsum(np.random.uniform(-y_range / num_points, y_range / num_points, (num_points, 1)), axis=0),
#                           np.cumsum(np.random.uniform(-z_range / num_points, z_range / num_points, (num_points, 1)), axis=0)))

# # 限制旋转在xy平面内较多，z方向变化较少
# rotations = np.cumsum(np.hstack((np.random.uniform(-rot_range_xy / num_points, rot_range_xy / num_points, (num_points, 2)),
#                                  np.random.uniform(-rot_range_z / num_points, rot_range_z / num_points, (num_points, 1)))), axis=0)

# # 确保起点和终点相近
# translations -= translations[0]
# translations[-1] = translations[0]
# rotations -= rotations[0]
# rotations[-1] = rotations[0]

# control_points = np.hstack((translations, rotations))

# # 保存控制点到文件
# output_file = 'control_points.txt'
# np.savetxt(output_file, control_points, delimiter=',')

# 该函数将姿态数据保存到文件中，每个姿态数据以空格分隔，保留6位小数
def save_pose_to_file(filename, poses):
    with open(filename, 'w') as f:
        for pose in poses:
            f.write(' '.join(f'{v:.6f}' for v in pose) + '\n')

# 该函数绘制控制点和插值后的B样条曲线，并在每个点上绘制姿态箭头
def plot_trajectory(control_points, new_frame_points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(control_points[:, 0], control_points[:, 1], control_points[:, 2], 'bo-', label='Control Points')
    ax.plot(new_frame_points[:, 0], new_frame_points[:, 1], new_frame_points[:, 2], 'r-', label='Interpolated B-spline')

    # 绘制姿态（用箭头表示方向）
    for point in new_frame_points:
        ax.quiver(point[0], point[1], point[2], point[3], point[4], point[5], length=10.0, normalize=True)

    ax.legend()  # 显示图例
    ax.set_title('B-Spline Interpolation of Control Points')
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_zlabel('Z (cm)')
    plt.show()

# 定义生成帧控制点的函数
def generate_frame_control_points(control_points, interval):
    # splprep()用于计算B样条的参数化形式
    # s: 平滑因子,值越大越平滑，s=0表示插值通过所有控制点；k: 样条阶数
    # tck: B样条表示的返回值，u: 插值参数范围
    tck, u = splprep(control_points.T, s=0, k=3)
    u_new = np.linspace(u.min(), u.max(), num=(len(control_points) - 1) * interval)
    frame_control_points = np.array(splev(u_new, tck)).T
    return frame_control_points

# Step 2: 对每个基本控制点进行三次B样条插值，生成更细粒度的帧控制点
frame_control_points = generate_frame_control_points(control_points, interval_frame)

# 定义生成每帧位姿的函数
def generate_frame_poses(frame_control_points, interval):
    tck, u = splprep(frame_control_points.T, s=0, k=3)
    u_new = np.linspace(u.min(), u.max(), num=(len(frame_control_points) - 1) * interval)
    frame_poses = np.array(splev(u_new, tck)).T
    return frame_poses
# Step 3: 对每帧数据进行三次B样条插值，插值间隔为480
frame_poses = generate_frame_poses(frame_control_points, interval_row)

# 将得到的位姿作为该帧图像的行位姿，存入该帧位姿信息文件
for i in range(len(frame_control_points) - 1):
    start_idx = i * interval_row
    end_idx = start_idx + interval_row
    frame_segment = frame_poses[start_idx:end_idx]
    frame_motion = os.path.join(output_dir, f't2_fast_cam1_frame_{i:06d}.txt')
    save_pose_to_file(frame_motion, frame_segment)

# # 定义生成每帧位姿的函数
# def generate_frame_poses(frame_control_points, interval):
#     frame_poses_list = []
#     for i in range(len(frame_control_points) - 1):
#         segment = frame_control_points[i:i+2]
#         tck, u = splprep(segment.T, s=0, k=3)
#         u_new = np.linspace(u.min(), u.max(), num=interval)
#         frame_poses = np.array(splev(u_new, tck)).T
#         frame_poses_list.append(frame_poses)
#     return frame_poses_list

# # Step 3: 对每两个帧控制点之间进行三次B样条插值，插值间隔为480
# frame_poses_list = generate_frame_poses(frame_control_points, interval_row)

# # 将得到的位姿作为该帧图像的行位姿，存入该帧位姿信息文件
# for i, frame_poses in enumerate(frame_poses_list):
#     frame_motion = os.path.join(output_dir, f't1_fast_cam1_frame_{i:06d}.txt')
#     save_pose_to_file(frame_motion, frame_poses)
    

print(f'Generated frames saved in {output_dir}.')

# 可视化
plot_trajectory(control_points, frame_control_points)


    