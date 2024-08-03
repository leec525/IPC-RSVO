# 这个文件用来逐行渲染图像，提取全局图像并将行图像拼接成卷帘图像，每拼接完成一张卷帘图像就将行图像删除，以节约内存
# This file is used to render the image row by row, extract the global image and stitch the rows into a rolling-shutter image
# It deleties the rows every time a rollup image is stitched to save memory.
# version: 2024-07-27
# author: <LiChen>

import os
from PIL import Image
import shutil
import subprocess

# 定义文件路径
motion_folder = os.path.abspath("motion_cam1")  # 各相机的位姿文件所在文件夹，每帧位姿文件中包含每行图像的位姿信息
output_part_folder = os.path.abspath("rgb_rs/sliced_t2_slow_cam1")  # 保存渲染所得的各相机的行图像文件夹
output_folder = os.path.abspath("rgb_rs/t2_slow_cam1")  # 保存拼接所得的卷帘图像文件夹
output_folder_gs = "rgb_gs/t2_slow/t2_cam1"  # 保存全局图像的文件夹
povray_executable = "/usr/local/bin/povray"  # povray可执行文件路径
povray_input_file = os.path.abspath("office.pov")  # povray渲染脚本文件路径

# 图像尺寸
image_width = 640
image_height = 480

# 确保输出文件夹存在
os.makedirs(output_part_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)
os.makedirs(output_folder_gs, exist_ok=True)

# 检查 motion 文件夹是否存在
if not os.path.exists(motion_folder):
    print(f'Error: The folder "{motion_folder}" does not exist.')
    exit(1)
else:
    print(f'The folder "{motion_folder}" exists.')

# 指定要处理的文件列表，从第几帧开始，到第几帧结束，左闭右开
specified_files = [f't2_slow_cam1_frame_{i:06d}.txt' for i in range(2, 4)]
# 获取所有的frame位姿文件
frame_files = sorted([f for f in specified_files if os.path.exists(os.path.join(motion_folder, f))])

# # 如果需要处理全部文件，可以使用下面这行代码，注释掉上面两行代码
# # 获取所有的位姿文件
# frame_files = sorted([f for f in os.listdir(motion_folder) if f.startswith('t2_slow_cam1_frame_')])

# Povray渲染函数
def render_image(transx, transy, transz, rotx, roty, rotz, output_file, start_row, end_row):
    # Povray命令
    povray_cmd = [
        povray_executable,
        f"+I{povray_input_file}",
        f"+O{output_file}",
        f"+W{image_width}", f"+H{image_height}", "+FN16", "+A0.3",
        f"Declare=transx={transx}", f"Declare=transy={transy}", f"Declare=transz={transz}",
        f"Declare=rotx={rotx}", f"Declare=roty={roty}", f"Declare=rotz={rotz}",
        f"Start_Row={start_row}", f"End_Row={end_row}"
    ]
    # 调用pov-ray渲染单行图像
    subprocess.run(povray_cmd)

# 处理每个frame文件
for frame_file in frame_files:
    # 读取位姿文件内容
    frame_path = os.path.join(motion_folder, frame_file)
    # 获取当前frame编号
    frame_num = int(frame_file.split('_')[-1].split('.')[0])  # 确保 frame_num 是整数

    # 构建要提取全局图像的原始文件名和路径
    # 逐行渲染图像时，Start_Row=1, End_Row=1，渲染所得为完整的整张图（不知道为什么），将这张图作为该时刻的全局图像帧
    part_filename_gs = f't2_slow_{frame_num:06d}_part_0000.png'
    part_path_gs = os.path.join(output_part_folder, part_filename_gs)

    with open(frame_path, 'r') as file:
        lines = file.readlines()
        
        # 检查已经渲染的部分
        rendered_parts = set()
        for i in range(image_height):
            part_filename = f't2_slow_{frame_num:06d}_part_{i:04d}.png'
            if os.path.exists(os.path.join(output_part_folder, part_filename)):
                rendered_parts.add(i)

        # 逐行渲染图像
        for i, line in enumerate(lines):
            if i in rendered_parts:
                continue  # 跳过已渲染的部分
            transx, transy, transz, rotx, roty, rotz = map(float, line.strip().split())
            output_file = os.path.join(output_part_folder, f"t2_slow_{frame_num:06d}_part_{i:04d}.png")
            render_image(transx, transy, transz, rotx, roty, rotz, output_file, i+1, i+1)

        # 提取全局图像
        if os.path.exists(part_path_gs):
            # 构建新的文件名和路径
            new_filename = f't2_slow_frame_{frame_num:04d}.png'
            new_path = os.path.join(output_folder_gs, new_filename)
            
            # 复制并重命名文件
            shutil.copy(part_path_gs, new_path)
            print(f'Copied and renamed {part_path_gs} to {new_path}')
        else:
            print(f"Warning: {part_path_gs} does not exist.")

    # 拼接卷帘图像
    # 创建一个空白的卷帘图像
    combined_image = Image.new('RGB', (image_width, image_height))
    
    for row in range(image_height):
        part_filename = f't2_slow_{frame_num:06d}_part_{row:04d}.png'
        part_path = os.path.join(output_part_folder, part_filename)
        
        if os.path.exists(part_path):
            part_image = Image.open(part_path)
            # 获取第 row 行的像素
            part_row = part_image.crop((0, row, image_width, row + 1))
            combined_image.paste(part_row, (0, row))
        else:
            print(f"Warning: {part_path} does not exist.")
    
    # 保存拼接后的图像
    combined_image.save(os.path.join(output_folder, f't2_slow_{frame_num:06d}.png'))
    print(f'Frame {frame_num} has been combined and saved.')

    # 删除行图像
    for i in range(image_height):
        part_filename = f't2_slow_{frame_num:06d}_part_{i:04d}.png'  # 确保使用正确的行号变量
        part_path = os.path.join(output_part_folder, part_filename)
        if os.path.exists(part_path):
            os.remove(part_path)
        else:
            print(f"Warning: {part_path} does not exist, skipping delete.")

print("所有全局图像帧保存完成！")
print("所有卷帘图像帧拼接完成！")