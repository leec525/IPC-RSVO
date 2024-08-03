import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from mpl_toolkits.mplot3d import Axes3D
import os

# 设置插值间隔
interval_frame = 5
interval_row = 480  # 图像行数

# 生成控制点数量
num_points = 50

# 限定运动范围
x_range = 3000  # 3米
y_range = 3000  # 3米
z_range = 500   # 0.5米
rot_range_xy = np.pi / 4  # xy平面内旋转角度45度
rot_range_z = np.pi / 18  # z方向上旋转角度10度

# 不设置随机数种子以便每次生成不同的轨迹

def generate_control_points():
    # 生成随机平移和旋转
    translations = np.cumsum(np.random.uniform(-x_range / num_points, x_range / num_points, (num_points, 1)), axis=0)
    translations = np.hstack((translations, 
                              np.cumsum(np.random.uniform(-y_range / num_points, y_range / num_points, (num_points, 1)), axis=0),
                              np.cumsum(np.random.uniform(-z_range / num_points, z_range / num_points, (num_points, 1)), axis=0)))

    # 限制旋转在xy平面内较多，z方向变化较少
    rotations = np.cumsum(np.hstack((np.random.uniform(-rot_range_xy / num_points, rot_range_xy / num_points, (num_points, 2)),
                                     np.random.uniform(-rot_range_z / num_points, rot_range_z / num_points, (num_points, 1)))), axis=0)

    # 确保起点和终点相近
    translations -= translations[0]
    translations[-1] = translations[0]
    rotations -= rotations[0]
    rotations[-1] = rotations[0]

    return np.hstack((translations, rotations))


def plot_trajectory(control_points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(control_points[:, 0], control_points[:, 1], control_points[:, 2], 'bo-', label='Control Points')

    # 绘制姿态（用箭头表示方向）
    for point in control_points:
        ax.quiver(point[0], point[1], point[2], point[3], point[4], point[5], length=10.0, normalize=True)

    ax.legend()  # 显示图例
    ax.set_title('Randomly Generated Control Points')
    ax.set_xlabel('X (cm)')
    ax.set_ylabel('Y (cm)')
    ax.set_zlabel('Z (cm)')

    plt.show(block=False)

while True:
    control_points = generate_control_points()

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

    plot_trajectory(frame_control_points)
    
    # 提示用户是否保存
    user_input = input("满意此轨迹吗？按 's' 保存，按 'q' 退出，按其他键生成新轨迹: ").lower()
    
    if user_input == 's':
        output_file = 'saved_control_points.txt'
        np.savetxt(output_file, control_points, delimiter=',')
        print(f'控制点已保存到 {output_file}')
        break
    elif user_input == 'q':
        break
    else:
        plt.close()


