# 此文件用于生成相机运动轨迹
# version: 2024-07-10
# author: <LiChen>

import numpy as np
import os
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from mpl_toolkits.mplot3d import Axes3D

# 设置插值间隔
interval_frame = 10
interval_row = 480  # 图像行数

# 创建输出目录
output_dir = 'output_frames/t2_slow'
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
    [0, 150, -50, 20, 0, 0],       #起点，要先运动一段进行初始化
    [-15, 150, -50, 20, 0, 0],     #向左运动
    [-30, 150, -50, 20, 0, 0],
    [-40, 150, -50, 20, 0, 0],
    [-50, 150, -50, 20, 0, 0],     #拐点
    [-40, 150, -50, 20, 0, 0],
    [-30, 150, -50, 20, 0, 0],     #向右运动
    [-15, 150, -50, 20, 0, 0],
    [0, 150, -50, 20, 0, 0],
    [0, 150, -50, 20, 0, 20],     #相机开始摇头
    [0, 150, -50, 20, 0, -20],    
    [0, 150, -50, 20, 0, 0],
    [25, 150, -50, 20, 0, 0],     #初始化运动结束，相机开始向右运动
    [35, 150, -50, 30, 0, 0],
    [45, 150, -50, 35, 0, 0],
    [50, 150, -50, 30, 0, 0],     #拐点1
    [50, 150, -45, 25, -10, 0],
    [50, 149, -25, 20, 0, 0], 
    [50, 148, 0, 20, 10, 0],       #向前运动
    [50, 149, 25, 20, 0, -1],
    [50, 150, 50, 20, 0, -2],      #拐点2
    [35, 150, 50, 20, 0, -3],
    [20, 150, 50, 20, 0, -2],      
    [0, 151, 50, 20, 0, -1],     
    [-20, 152, 50, 20, 10, 0],
    [-35, 153, 50, 20, 50, 0],
    [-50, 152, 50, 20, 90, 0],     #拐点3
    [-50, 151, 45, 20, 135, 0],
    [-50, 150, 35, 20, 180, 0],
    [-50, 150, 25, 20, 180, 0],
    [-50, 150, 10, 15, 180, 0],
    [-50, 150, -10, 13, 180, 0],
    [-50, 149, -25, 10, 180, 0],
    [-50, 148, -50, 0, 180, 0],    #拐点4
    [-40, 149, -50, 0, 200, 0],
    [-25, 149, -50, 0, 270, 0],
    [-10, 150, -50, 0, 320, 0],
    [0, 150, -50, 0, 360, 0],
    [10, 150, -50, 0, 360, 0],
    [25, 150, -50, 0, 360, 0]     #终点
])

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
# 对每一段生成控制点
def generate_segment_control_points(segments, interval):
    frame_control_points = []

    for segment in segments:
        if len(segment) < 4:
            continue

        tck, u = splprep(segment.T, s=0, k=3)
        u_new = np.linspace(u.min(), u.max(), num=(len(segment) - 1) * interval)
        segment_control_points = np.array(splev(u_new, tck)).T
        frame_control_points.append(segment_control_points[:-1])

    frame_control_points.append(segments[-1][-1].reshape(1, -1))
    frame_control_points = np.vstack(frame_control_points)
    return frame_control_points

# 将控制点按段分割
segment_1 = control_points[0:8]
segment_2 = control_points[7:14]
segment_3 = control_points[13:30]
segment_4 = control_points[29:40]

segments = [segment_1, segment_2, segment_3, segment_4]

# 生成帧控制点
frame_control_points = generate_segment_control_points(segments, interval_frame)

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
    frame_motion = os.path.join(output_dir, f't2_slow_cam1_frame_{i:06d}.txt')
    save_pose_to_file(frame_motion, frame_segment)
    

print(f'Generated frames saved in {output_dir}.')

# 可视化
plot_trajectory(control_points, frame_control_points)


    