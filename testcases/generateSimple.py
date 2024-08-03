import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import splprep, splev

# 基本控制点
control_points = np.array([
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
    [-20, 152, 50, 20, -10, 0],
    [-35, 153, 50, 20, -50, 0],
    [-50, 152, 50, 20, -90, 0],     #拐点3
    [-50, 151, 45, 20, -135, 0],
    [-50, 150, 35, 20, -180, 0],
    [-50, 150, 25, 20, -180, 0],
    [-50, 150, 10, 15, -180, 0],
    [-50, 150, -10, 13, -180, 0],
    [-50, 149, -25, 10, -180, 0],
    [-50, 148, -50, 0, -180, 0],    #拐点4
    [-40, 149, -50, 0, -200, 0],
    [-25, 149, -50, 0, -270, 0],
    [-10, 150, -50, 0, -320, 0],
    [0, 150, -50, 0, -360, 0],
    [10, 150, -50, 0, -360, 0],
    [25, 150, -50, 0, -360, 0]     #终点
])

# 插值函数
# def interpolate_points(points, num_points=300):
#     tck, u = splprep(points.T, s=0, k=3)
#     u_new = np.linspace(u.min(), u.max(), num_points)
#     new_points = np.array(splev(u_new, tck)).T
#     return new_points
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
segment_1 = control_points[0:7]
segment_2 = control_points[7:13]
segment_3 = control_points[13:30]
segment_4 = control_points[30:40]

segments = [segment_1, segment_2, segment_3, segment_4]

# 生成帧控制点
frame_control_points = generate_segment_control_points(segments, 5)

# 对控制点进行三次B样条插值
# num_interpolated_points = 300
# interpolated_points = interpolate_points(control_points, num_points=num_interpolated_points)

# 可视化轨迹
def plot_trajectory(control_points, interpolated_points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(control_points[:, 0], control_points[:, 1], control_points[:, 2], 'bo-', label='Control Points')
    ax.plot(interpolated_points[:, 0], interpolated_points[:, 1], interpolated_points[:, 2], 'r-', label='Interpolated B-spline')

    # 绘制姿态（用箭头表示方向）
    for point in interpolated_points:
        ax.quiver(point[0], point[1], point[2], np.cos(np.deg2rad(point[3])), np.sin(np.deg2rad(point[3])), 0, length=10.0, normalize=True)

    ax.legend()  # 显示图例
    ax.set_title('L-shaped Trajectory')
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_zlabel('Z (cm)')
    plt.show()

plot_trajectory(control_points, frame_control_points)

# # 保存控制点到文件
# output_file = 'l_trajectory_control_points.txt'
# np.savetxt(output_file, control_points, delimiter=',')
# print(f'控制点已保存到 {output_file}')
