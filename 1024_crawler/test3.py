import os
from random import sample

dirpath = r'/root/docker_aria2-pro/downloads_local' 
img_list = []
for root, dirs, files in os.walk(dirpath):
    # img_list = []  # 从文件列表中取出jpg文件放入到list中
    # print(root)

    # print(files)
        # print(dir)
    for file in files:
        apath = os.path.join(root, file)
        img_list.append(apath)
            # print(file)
            # print(str(os.path.join(root,dir,file)))
            # img_list.extend(os.path.join(root,dir,file))
            # print(img_list)
            # img_list.extend(files)
result = sample(img_list,9)

print(result)