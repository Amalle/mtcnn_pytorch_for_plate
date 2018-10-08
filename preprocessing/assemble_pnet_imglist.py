import os
import config
import preprocessing.assemble as assemble

if __name__ == '__main__':
    anno_list = []

    pnet_postive_file = os.path.join(
        config.ANNO_STORE_DIR, config.PNET_POSTIVE_ANNO_FILENAME)
    pnet_part_file = os.path.join(
        config.ANNO_STORE_DIR, config.PNET_PART_ANNO_FILENAME)
    pnet_neg_file = os.path.join(
        config.ANNO_STORE_DIR, config.PNET_NEGATIVE_ANNO_FILENAME)

    anno_list.append(pnet_postive_file)
    anno_list.append(pnet_part_file)
    anno_list.append(pnet_neg_file)

    imglist_filename = config.PNET_TRAIN_IMGLIST_FILENAME
    anno_dir = config.ANNO_STORE_DIR
    imglist_file = os.path.join(anno_dir, imglist_filename)

    chose_count = assemble.assemble_data(imglist_file, anno_list)
    print("PNet train annotation result file path:%s" % imglist_file)
