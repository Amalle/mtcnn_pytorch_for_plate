import torch
import torch.nn as nn
import torch.nn.functional as F

class LossFn:
    def __init__(self, device):
        # loss function
        self.loss_cls = nn.BCELoss().to(device)
        self.loss_box = nn.MSELoss().to(device)
        self.loss_landmark = nn.MSELoss().to(device)
        self.loss_attr = nn.CrossEntropyLoss().to(device)

    def cls_loss(self,gt_label,pred_label):
        # get the mask element which >= 0, only 0 and 1 can effect the detection loss
        pred_label = torch.squeeze(pred_label)
        mask = torch.ge(gt_label,0)
        valid_gt_label = torch.masked_select(gt_label,mask).float()
        valid_pred_label = torch.masked_select(pred_label,mask)
        return self.loss_cls(valid_pred_label,valid_gt_label)

    def attr_loss(self, gt_label, gt_attr, pred_attr):
        mask = torch.eq(gt_label,-2)
        chose_index = torch.nonzero(mask.data)
        chose_index = torch.squeeze(chose_index)
        valid_gt_attr = gt_attr[chose_index, :]
        valid_pred_attr = pred_attr[chose_index, :]

        valid_gt_color = valid_gt_attr[:,0]
        valid_gt_layer = valid_gt_attr[:,1]
        valid_gt_type  = valid_gt_attr[:,2]
        valid_pred_color = valid_pred_attr[:,:5]
        valid_pred_layer = valid_pred_attr[:,5:7]
        valid_pred_type  = valid_pred_attr[:,7:]
        # print(valid_gt_color)
        # print(valid_gt_layer)
        # print(valid_gt_type)
        # print(valid_pred_color)
        # print(valid_pred_layer)
        # print(valid_pred_type)
        loss_color = self.loss_attr(valid_pred_color, valid_gt_color)
        loss_layer = self.loss_attr(valid_pred_layer, valid_gt_layer)
        loss_type  = self.loss_attr(valid_pred_type, valid_gt_type)
        return loss_color,loss_layer,loss_type

    def box_loss(self,gt_label,gt_offset,pred_offset):
        #get the mask element which != 0
        mask = torch.ne(gt_label,0)
        #convert mask to dim index
        chose_index = torch.nonzero(mask)
        chose_index = torch.squeeze(chose_index)
        #only valid element can effect the loss
        valid_gt_offset = gt_offset[chose_index,:]
        valid_pred_offset = pred_offset[chose_index,:]
        valid_pred_offset = torch.squeeze(valid_pred_offset)
        return self.loss_box(valid_pred_offset,valid_gt_offset)


    def landmark_loss(self,gt_label,gt_landmark,pred_landmark):
        mask = torch.eq(gt_label,-2)

        chose_index = torch.nonzero(mask.data)
        chose_index = torch.squeeze(chose_index)

        valid_gt_landmark = gt_landmark[chose_index, :]
        valid_pred_landmark = pred_landmark[chose_index, :]
        return self.loss_landmark(valid_pred_landmark, valid_gt_landmark)