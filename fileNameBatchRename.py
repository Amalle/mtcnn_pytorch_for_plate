<<<<<<< HEAD
import os,glob

def listdir(path, list_name, filetype, subpath=False):
    file_num = 0
    for file in os.listdir(path):
        # file_path = os.path.join(path, file)
        file_path = path + '/' + file
        if os.path.isdir(file_path) and subpath:
            listdir(file_path, list_name, filetype, subpath)
        elif os.path.splitext(file_path)[1] in filetype:
            list_name.append(file_path)
            file_num += 1
            # print(file_num,file_path)
    return file_num

def getFileNameFromPath(file_path):
    filename = os.path.split(file_path)[-1]
    img_type = filename.split('.')[-1]
    type_len = len(img_type)+1
    filename = filename[0:-type_len]
    return filename

def cropFileName(filepath):
    filename = getFileNameFromPath(filepath)
    name = filename.split('_')[-2] + '_m' + filename.split('_')[-1]
    return name

imageDir = "/users/maqiao/DNN/MTCNN/data20180925/new"
xmlDir = "/users/maqiao/DNN/MTCNN/data20180925/new"
# imageList = glob.glob(os.path.join(imageDir, '*.jpg'))
imageList = []
image_type = ['.jpg','.jpeg','.JPG','.png','.gif']
listdir(imageDir,imageList,image_type,True)

if 0 != len(imageList):
    i = 0
    for image_file in imageList:
        i += 1
        print(str(i)+'/'+str(len(imageList))+'  '+image_file)
        if True:
            image_name = getFileNameFromPath(image_file)
            xmlDir = os.path.dirname(image_file)
            xml_file = xmlDir + '/' + image_name + '.xml'
            if not os.path.exists(image_file):
                continue
            if not os.path.exists(xml_file):
                os.remove(image_file)
                continue
            img_new_name = 'plate00'+str(i)
            img_new_file = xmlDir + '/' + img_new_name + '.jpg'
            xml_new_file = xmlDir + '/' + img_new_name + '.xml'
            os.rename(image_file,img_new_file)
            os.rename(xml_file,xml_new_file)
        # if True:
        #     image_name = getFileNameFromPath(image_file)
        #     image_name_ = image_name[:-6]
        #     img_crop_name = 'hasline'+str(i)
        #     img_crop_file = imageDir + '/' + img_crop_name + '.jpg'
        # else:
        #     image_name = cropFileName(image_file)
        #     img_crop_name = image_name
        #     img_crop_file = imageDir + '/' + img_crop_name + '.png'

        # os.rename(image_file,img_crop_file)
=======
import os,glob

def listdir(path, list_name, filetype, subpath=False):
    file_num = 0
    for file in os.listdir(path):
        # file_path = os.path.join(path, file)
        file_path = path + '/' + file
        if os.path.isdir(file_path) and subpath:
            listdir(file_path, list_name, filetype, subpath)
        elif os.path.splitext(file_path)[1] in filetype:
            list_name.append(file_path)
            file_num += 1
            # print(file_num,file_path)
    return file_num

def getFileNameFromPath(file_path):
    filename = os.path.split(file_path)[-1]
    img_type = filename.split('.')[-1]
    type_len = len(img_type)+1
    filename = filename[0:-type_len]
    return filename

def cropFileName(filepath):
    filename = getFileNameFromPath(filepath)
    name = filename.split('_')[-2] + '_m' + filename.split('_')[-1]
    return name

imageDir = "/users/maqiao/DNN/MTCNN/data20180925/new"
xmlDir = "/users/maqiao/DNN/MTCNN/data20180925/new"
# imageList = glob.glob(os.path.join(imageDir, '*.jpg'))
imageList = []
image_type = ['.jpg','.jpeg','.JPG','.png','.gif']
listdir(imageDir,imageList,image_type,True)

if 0 != len(imageList):
    i = 0
    for image_file in imageList:
        i += 1
        print(str(i)+'/'+str(len(imageList))+'  '+image_file)
        if True:
            image_name = getFileNameFromPath(image_file)
            xmlDir = os.path.dirname(image_file)
            xml_file = xmlDir + '/' + image_name + '.xml'
            if not os.path.exists(image_file):
                continue
            if not os.path.exists(xml_file):
                os.remove(image_file)
                continue
            img_new_name = 'plate00'+str(i)
            img_new_file = xmlDir + '/' + img_new_name + '.jpg'
            xml_new_file = xmlDir + '/' + img_new_name + '.xml'
            os.rename(image_file,img_new_file)
            os.rename(xml_file,xml_new_file)
        # if True:
        #     image_name = getFileNameFromPath(image_file)
        #     image_name_ = image_name[:-6]
        #     img_crop_name = 'hasline'+str(i)
        #     img_crop_file = imageDir + '/' + img_crop_name + '.jpg'
        # else:
        #     image_name = cropFileName(image_file)
        #     img_crop_name = image_name
        #     img_crop_file = imageDir + '/' + img_crop_name + '.png'

        # os.rename(image_file,img_crop_file)
>>>>>>> e88472f491f7a4a8e9162d955659f88a773c3ea0
