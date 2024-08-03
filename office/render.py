import os
import subprocess

# 定义文件路径
motion_folder = os.path.abspath("motion_cam1")
output_part_folder = os.path.abspath("rgb_rs/sliced")
output_folder = os.path.abspath("rgb_rs/t1_fast_cam1")
povray_executable = "/usr/local/bin/povray"
povray_input_file = os.path.abspath("office.pov")

# 确保输出文件夹存在
os.makedirs(output_part_folder, exist_ok=True)
os.makedirs(output_folder, exist_ok=True)

# 检查 motion 文件夹是否存在
if not os.path.exists(motion_folder):
    print(f'Error: The folder "{motion_folder}" does not exist.')
    exit(1)
else:
    print(f'The folder "{motion_folder}" exists.')

# 生成shell脚本内容
script_content = "#!/bin/bash\n"

# 指定要处理的文件列表
specified_files = [f't1_fast_motion_frame_{i:06d}.txt' for i in range(0, 2)]
# 获取所有的frame位姿文件
frame_files = sorted([f for f in specified_files if os.path.exists(os.path.join(motion_folder, f))])

# Povray渲染函数
def render_image(transx, transy, transz, rotx, roty, rotz, output_file, start_row, end_row):
    # Povray命令
    povray_cmd = [
        povray_executable,
        f"+I{povray_input_file}",
        f"+O{output_file}",
        "+W640", "+H480", "+FN16", "+A0.3",
        f"Declare=transx={transx}", f"Declare=transy={transy}", f"Declare=transz={transz}",
        f"Declare=rotx={rotx}", f"Declare=roty={roty}", f"Declare=rotz={rotz}",
        f"Start_Row={start_row}", f"End_Row={end_row}"
    ]

    try:
    #     # 执行命令
    #     result = subprocess.run(povray_cmd, check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=os.path.dirname(povray_input_file))
    #     print(f"Command output: {result.stdout.decode()}")
    #     print(f"Command stderr: {result.stderr.decode()}")
    # except subprocess.CalledProcessError as e:
    #     print(f"Error occurred while rendering: {e}")
    #     print(f"Command output: {e.output.decode()}")
    #     print(f"Command stderr: {e.stderr.decode()}")
        # 执行命令
        result = subprocess.Popen(povray_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ)
        stdout, stderr = result.communicate()
        
        print(f"Command output: {stdout.decode()}")
        print(f"Command stderr: {stderr.decode()}")
        
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, povray_cmd, output=stdout, stderr=stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while rendering: {e}")
        print(f"Command output: {e.output.decode()}")
        print(f"Command stderr: {e.stderr.decode()}")

# 处理每个frame文件
for frame_file in frame_files:
    # 读取位姿文件内容
    frame_path = os.path.join(motion_folder, frame_file)
    frame_num = frame_file.split('_')[-1].split('.')[0]
    with open(frame_path, 'r') as file:
        lines = file.readlines()
        
        # 逐行渲染图像
        for i, line in enumerate(lines):
            transx, transy, transz, rotx, roty, rotz = map(float, line.strip().split())
            output_file = os.path.join(output_part_folder, f"{frame_file[:-4]}_line_{i:03d}.png")
            render_image(transx, transy, transz, rotx, roty, rotz, output_file, i+1, i+1)

# for frame_file in frame_files:
#     # 读取位姿文件内容
#     frame_path = os.path.join(motion_folder, frame_file)
#     with open(frame_path, 'r') as file:
#         lines = file.readlines()
        
#         # 逐行生成渲染命令
#         for i, line in enumerate(lines):
#             transx, transy, transz, rotx, roty, rotz = map(float, line.strip().split())
#             output_file = os.path.join(output_part_folder, f"{frame_file[:-4]}_part_{i:04d}.png")
#             povray_cmd = f'/usr/local/bin/povray +I"office.pov" +O"{output_file}" +W640 +H480 +FN16 +A0.3 Declare=transx={transx} Declare=transy={transy} Declare=transz={transz} Declare=rotx={rotx} Declare=roty={roty} Declare=rotz={rotz} Start_Row={i+1} End_Row={i+1}\n'
#             script_content += povray_cmd

# # 写入并执行shell脚本
# script_path = "/media/simulator/3d08f519-87e3-490e-b123-7269f4156f6c/home/simulator/LIC/Datasets/myTraj/office/render_script.sh"
# with open(script_path, 'w') as script_file:
#     script_file.write(script_content)

# # 确保shell脚本有执行权限
# os.chmod(script_path, 0o755)

# # 执行shell脚本
# subprocess.run(script_path, shell=True, check=True)

print("渲染完成！")

