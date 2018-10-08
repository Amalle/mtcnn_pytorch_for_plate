<<<<<<< HEAD
import os,shutil
import operator
import xml.etree.ElementTree as ET

plate_color = ['蓝','黄','绿','白','黑']
plate_layer = ['单','双']
plate_type  = ['tradition','new_energy']

def movefile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.move(srcfile,dstfile)          #移动文件
        print("move %s -> %s"%( srcfile,dstfile))

def copyfile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.copyfile(srcfile,dstfile)      #复制文件
        print("copy %s -> %s"%( srcfile,dstfile))

def getFileNameFromPath(file_path):
    filename = os.path.split(file_path)[-1]
    img_type = filename.split('.')[-1]
    type_len = len(img_type)+1
    filename = filename[0:-type_len]
    return filename

def listdir(path, list_name, filetype, subpath=False):
    file_num = 0
    for file in os.listdir(path):
        # file_path = os.path.join(path, file)
        file_path = path + '/' + file
        if os.path.isdir(file_path) and subpath:
            listdir(file_path, list_name, filetype, subpath)
        elif os.path.splitext(file_path)[1]==filetype:
            list_name.append(file_path)
            file_num += 1
            # print(file_num,file_path)
    return file_num

#读取标注数据
def getLabel(label_file):
    pvertexs = []
    pcolors = []
    players = []
    ptypes = []

    xml = ET.parse(label_file)
    root = xml.getroot()
    if root.tag != "dataroot":
        print ("Can not find annotation")
    else:
        marknode = root.find('markNode')
        obj = marknode.find('object')
        if obj != None:
            for p in marknode.iter('object'):
                color = plate_color.index(p.find('color').text)
                layer = plate_layer.index(p.find('layer').text)
                ptype = plate_type.index(p.find('platetype').text)
                pcolors.append(color)
                players.append(layer)
                ptypes.append(ptype)

                vertexs = p.find('vertexs')
                if vertexs != None:
                    vers = []
                    for ver in vertexs.iter('vertex'):
                        x = int(ver.find('x').text)
                        y = int(ver.find('y').text)
                        vers.append([x,y])
                pvertexs.append(vers)
    return pvertexs,pcolors,players,ptypes

#读取旧版标注数据
def getOldLabel(label_file):
    pvertexs = []
    pcolors = []
    players = []
    ptypes = []

    xml = ET.parse(label_file)
    root = xml.getroot()
    if root.tag != "annotation":
        print ("Can not find annotation")
    else:
        marknode = root.find('object')
        obj = marknode.find('plate')
        if obj != None:
            for p in marknode.iter('plate'):
                color = plate_color.index(p.find('color').text)
                layer = plate_layer.index(p.find('mode').text)
                ptype = 0
                if color == 2:
                    ptype = 1
                pcolors.append(color)
                players.append(layer)
                ptypes.append(ptype)

                vertexs = p.find('vertexs')
                if vertexs != None:
                    vers = []
                    for ver in vertexs.iter('vertex'):
                        x = int(ver.find('x').text)
                        y = int(ver.find('y').text)
                        vers.append([x,y])
                pvertexs.append(vers)

    print(pvertexs,pcolors,players,ptypes)
    return pvertexs,pcolors,players,ptypes

#图片路径
image_path = "/users/maqiao/DNN/MTCNN/data20180925"
# image_path = "E:/test"
#标注文件路径1
xml_path = "/users/maqiao/DNN/MTCNN/data20180925"
# xml_path = "E:/test"
#读取文件列表
file_list = []
listdir(image_path,file_list,'.jpg',True)

f0 = open("image_list.txt",'w')
f = open("landmark_list.txt",'w')
count = 0
i = 0
j = 0
for file_name in file_list:
    count += 1
    print(str(count)+'/'+str(len(file_list))+'  '+file_name)
    fileName = getFileNameFromPath(file_name)
    xml_path = os.path.dirname(file_name)
    xmlfile_name = xml_path + '/' + fileName + '.xml'
    print(xmlfile_name)
    #检查文件是否存在并打开
    pvertexs = []
    if os.path.exists(xmlfile_name):
        pvertexs,colors,layers,types = getOldLabel(xmlfile_name)
        if len(pvertexs) == 0 or len(pvertexs[0]) != 4:
            continue
        
        # box
        for i in range(len(pvertexs)):
            vertexs = pvertexs[i]
            color = colors[i]
            layer = layers[i]
            ptype = types[i]

            left   = min(vertexs[0][0],vertexs[1][0],vertexs[2][0],vertexs[3][0])
            top    = min(vertexs[0][1],vertexs[1][1],vertexs[2][1],vertexs[3][1])
            right  = max(vertexs[0][0],vertexs[1][0],vertexs[2][0],vertexs[3][0])
            bottom = max(vertexs[0][1],vertexs[1][1],vertexs[2][1],vertexs[3][1])

            w = right - left
            h = bottom - top
            # if w/h < 2.5:
            #     continue

            f0.write(file_name + ' ' + str(left) + ' ' + str(top) + ' ' + str(right) + ' ' + str(bottom) + '\n')

            # landmark
            if vertexs[0][0] < vertexs[1][0] and vertexs[1][0] > (vertexs[0][0]+vertexs[1][0]+vertexs[2][0]+vertexs[3][0])/4:
                f.write(file_name + ' ' + str(left) + ' ' + str(right) + ' ' + str(top) + ' ' + str(bottom) + 
                        ' ' + str(vertexs[0][0]) + ' ' + str(vertexs[0][1]) + 
                        ' ' + str(vertexs[1][0]) + ' ' + str(vertexs[1][1]) + 
                        ' ' + str(vertexs[2][0]) + ' ' + str(vertexs[2][1]) + 
                        ' ' + str(vertexs[3][0]) + ' ' + str(vertexs[3][1]) + 
                        ' ' + str(color) + ' ' + str(layer) + ' ' + str(ptype) + '\n')
                i += 1
                print("clockwise")
            else:
                f.write(file_name + ' ' + str(left) + ' ' + str(right) + ' ' + str(top) + ' ' + str(bottom) + 
                        ' ' + str(vertexs[0][0]) + ' ' + str(vertexs[0][1]) + 
                        ' ' + str(vertexs[3][0]) + ' ' + str(vertexs[3][1]) + 
                        ' ' + str(vertexs[2][0]) + ' ' + str(vertexs[2][1]) + 
                        ' ' + str(vertexs[1][0]) + ' ' + str(vertexs[1][1]) + 
                        ' ' + str(color) + ' ' + str(layer) + ' ' + str(ptype) + '\n')
                j += 1
                print("***********anticlockwise")

print(i)
=======
import os,shutil
import operator
import xml.etree.ElementTree as ET

plate_color = ['蓝','黄','绿','白','黑']
plate_layer = ['单','双']
plate_type  = ['tradition','new_energy']

def movefile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.move(srcfile,dstfile)          #移动文件
        print("move %s -> %s"%( srcfile,dstfile))

def copyfile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.copyfile(srcfile,dstfile)      #复制文件
        print("copy %s -> %s"%( srcfile,dstfile))

def getFileNameFromPath(file_path):
    filename = os.path.split(file_path)[-1]
    img_type = filename.split('.')[-1]
    type_len = len(img_type)+1
    filename = filename[0:-type_len]
    return filename

def listdir(path, list_name, filetype, subpath=False):
    file_num = 0
    for file in os.listdir(path):
        # file_path = os.path.join(path, file)
        file_path = path + '/' + file
        if os.path.isdir(file_path) and subpath:
            listdir(file_path, list_name, filetype, subpath)
        elif os.path.splitext(file_path)[1]==filetype:
            list_name.append(file_path)
            file_num += 1
            # print(file_num,file_path)
    return file_num

#读取标注数据
def getLabel(label_file):
    pvertexs = []
    pcolors = []
    players = []
    ptypes = []

    xml = ET.parse(label_file)
    root = xml.getroot()
    if root.tag != "dataroot":
        print ("Can not find annotation")
    else:
        marknode = root.find('markNode')
        obj = marknode.find('object')
        if obj != None:
            for p in marknode.iter('object'):
                color = plate_color.index(p.find('color').text)
                layer = plate_layer.index(p.find('layer').text)
                ptype = plate_type.index(p.find('platetype').text)
                pcolors.append(color)
                players.append(layer)
                ptypes.append(ptype)

                vertexs = p.find('vertexs')
                if vertexs != None:
                    vers = []
                    for ver in vertexs.iter('vertex'):
                        x = int(ver.find('x').text)
                        y = int(ver.find('y').text)
                        vers.append([x,y])
                pvertexs.append(vers)
    return pvertexs,pcolors,players,ptypes

#读取旧版标注数据
def getOldLabel(label_file):
    pvertexs = []
    pcolors = []
    players = []
    ptypes = []

    xml = ET.parse(label_file)
    root = xml.getroot()
    if root.tag != "annotation":
        print ("Can not find annotation")
    else:
        marknode = root.find('object')
        obj = marknode.find('plate')
        if obj != None:
            for p in marknode.iter('plate'):
                color = plate_color.index(p.find('color').text)
                layer = plate_layer.index(p.find('mode').text)
                ptype = 0
                if color == 2:
                    ptype = 1
                pcolors.append(color)
                players.append(layer)
                ptypes.append(ptype)

                vertexs = p.find('vertexs')
                if vertexs != None:
                    vers = []
                    for ver in vertexs.iter('vertex'):
                        x = int(ver.find('x').text)
                        y = int(ver.find('y').text)
                        vers.append([x,y])
                pvertexs.append(vers)

    print(pvertexs,pcolors,players,ptypes)
    return pvertexs,pcolors,players,ptypes

#图片路径
image_path = "/users/maqiao/DNN/MTCNN/data20180925"
# image_path = "E:/test"
#标注文件路径1
xml_path = "/users/maqiao/DNN/MTCNN/data20180925"
# xml_path = "E:/test"
#读取文件列表
file_list = []
listdir(image_path,file_list,'.jpg',True)

f0 = open("image_list.txt",'w')
f = open("landmark_list.txt",'w')
count = 0
i = 0
j = 0
for file_name in file_list:
    count += 1
    print(str(count)+'/'+str(len(file_list))+'  '+file_name)
    fileName = getFileNameFromPath(file_name)
    xml_path = os.path.dirname(file_name)
    xmlfile_name = xml_path + '/' + fileName + '.xml'
    print(xmlfile_name)
    #检查文件是否存在并打开
    pvertexs = []
    if os.path.exists(xmlfile_name):
        pvertexs,colors,layers,types = getOldLabel(xmlfile_name)
        if len(pvertexs) == 0 or len(pvertexs[0]) != 4:
            continue
        
        # box
        for i in range(len(pvertexs)):
            vertexs = pvertexs[i]
            color = colors[i]
            layer = layers[i]
            ptype = types[i]

            left   = min(vertexs[0][0],vertexs[1][0],vertexs[2][0],vertexs[3][0])
            top    = min(vertexs[0][1],vertexs[1][1],vertexs[2][1],vertexs[3][1])
            right  = max(vertexs[0][0],vertexs[1][0],vertexs[2][0],vertexs[3][0])
            bottom = max(vertexs[0][1],vertexs[1][1],vertexs[2][1],vertexs[3][1])

            w = right - left
            h = bottom - top
            # if w/h < 2.5:
            #     continue

            f0.write(file_name + ' ' + str(left) + ' ' + str(top) + ' ' + str(right) + ' ' + str(bottom) + '\n')

            # landmark
            if vertexs[0][0] < vertexs[1][0] and vertexs[1][0] > (vertexs[0][0]+vertexs[1][0]+vertexs[2][0]+vertexs[3][0])/4:
                f.write(file_name + ' ' + str(left) + ' ' + str(right) + ' ' + str(top) + ' ' + str(bottom) + 
                        ' ' + str(vertexs[0][0]) + ' ' + str(vertexs[0][1]) + 
                        ' ' + str(vertexs[1][0]) + ' ' + str(vertexs[1][1]) + 
                        ' ' + str(vertexs[2][0]) + ' ' + str(vertexs[2][1]) + 
                        ' ' + str(vertexs[3][0]) + ' ' + str(vertexs[3][1]) + 
                        ' ' + str(color) + ' ' + str(layer) + ' ' + str(ptype) + '\n')
                i += 1
                print("clockwise")
            else:
                f.write(file_name + ' ' + str(left) + ' ' + str(right) + ' ' + str(top) + ' ' + str(bottom) + 
                        ' ' + str(vertexs[0][0]) + ' ' + str(vertexs[0][1]) + 
                        ' ' + str(vertexs[3][0]) + ' ' + str(vertexs[3][1]) + 
                        ' ' + str(vertexs[2][0]) + ' ' + str(vertexs[2][1]) + 
                        ' ' + str(vertexs[1][0]) + ' ' + str(vertexs[1][1]) + 
                        ' ' + str(color) + ' ' + str(layer) + ' ' + str(ptype) + '\n')
                j += 1
                print("***********anticlockwise")

print(i)
>>>>>>> e88472f491f7a4a8e9162d955659f88a773c3ea0
print(j)