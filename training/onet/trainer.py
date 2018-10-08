import torch
import datetime
import time
from models.lossfn import LossFn
from tools.utils import AverageMeter


class ONetTrainer(object):
    
    def __init__(self, lr, train_loader, model, optimizer, scheduler, logger, device):
        self.lr = lr
        self.train_loader = train_loader
        self.model = model
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device
        self.lossfn = LossFn(self.device)
        self.logger = logger
        self.run_count = 0
        self.scalar_info = {}

    def compute_accuracy(self, prob_cls, gt_cls, prob_attr, gt_attr):
        #we only need the detection which >= 0
        prob_cls = torch.squeeze(prob_cls)
        mask = torch.ge(gt_cls, 0)
        #get valid element
        valid_gt_cls = torch.masked_select(gt_cls, mask)
        valid_prob_cls = torch.masked_select(prob_cls, mask)
        size = min(valid_gt_cls.size()[0], valid_prob_cls.size()[0])
        prob_ones = torch.ge(valid_prob_cls, 0.6).float()
        right_ones = torch.eq(prob_ones, valid_gt_cls.float()).float()
        accuracy_cls = torch.div(torch.mul(torch.sum(right_ones), float(1.0)), float(size))


        prob_attr = torch.squeeze(prob_attr)
        mask_attr = torch.eq(gt_cls, -2)
        chose_index = torch.nonzero(mask_attr.data)
        chose_index = torch.squeeze(chose_index)
        valid_gt_attr = gt_attr[chose_index, :]
        valid_prob_attr = prob_attr[chose_index, :]
        size_attr = min(valid_gt_attr.size()[0], valid_prob_attr.size()[0])
        valid_gt_color = valid_gt_attr[:,0]
        valid_gt_layer = valid_gt_attr[:,1]
        valid_gt_type  = valid_gt_attr[:,2]
        # print(valid_prob_attr)
        valid_prob_color = torch.max(valid_prob_attr[:,:5],1)
        valid_prob_layer = torch.max(valid_prob_attr[:,5:7],1)
        valid_prob_type  = torch.max(valid_prob_attr[:,7:],1)
        # print(valid_prob_color)
        # print(valid_gt_color)
        color_right_ones = torch.eq(valid_prob_color[1],valid_gt_color).float()
        layer_right_ones = torch.eq(valid_prob_layer[1],valid_gt_layer).float()
        type_right_ones  = torch.eq(valid_prob_type[1], valid_gt_type).float()
        accuracy_color = torch.div(torch.mul(torch.sum(color_right_ones), float(1.0)), float(size_attr))
        accuracy_layer = torch.div(torch.mul(torch.sum(layer_right_ones), float(1.0)), float(size_attr))
        accuracy_type  = torch.div(torch.mul(torch.sum(type_right_ones),  float(1.0)), float(size_attr))

        return accuracy_cls,accuracy_color,accuracy_layer,accuracy_type

    def update_lr(self, epoch):
        """
        update learning rate of optimizers
        :param epoch: current training epoch
        """
        # update learning rate of model optimizer
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = self.lr

    def train(self, epoch):
        cls_loss_ = AverageMeter()
        box_offset_loss_ = AverageMeter()
        landmark_loss_ = AverageMeter()
        total_loss_ = AverageMeter()
        accuracy_cls_ = AverageMeter()
        accuracy_color_ = AverageMeter()
        accuracy_layer_ = AverageMeter()
        accuracy_type_ = AverageMeter()

        self.scheduler.step()
        self.model.train()

        for batch_idx, (data, target) in enumerate(self.train_loader):
            gt_label = target['label']
            gt_bbox = target['bbox_target']
            gt_landmark = target['landmark_target']
            gt_attr = target['attribute']
            data, gt_label, gt_bbox, gt_landmark, gt_attr = data.to(self.device), gt_label.to(
                self.device), gt_bbox.to(self.device).float(), gt_landmark.to(
                self.device).float(), gt_attr.to(self.device).long()

            cls_pred, box_offset_pred, landmark_offset_pred, attr_pred = self.model(data)
            # print(cls_pred[0:100])
            # print(box_offset_pred[0:100,:])
            # print(landmark_offset_pred[0:100,:])
            # print(attr_pred[0:100,:])
            # compute the loss
            cls_loss = self.lossfn.cls_loss(gt_label, cls_pred)
            box_offset_loss = self.lossfn.box_loss(
                gt_label, gt_bbox, box_offset_pred)
            landmark_loss = self.lossfn.landmark_loss(gt_label, gt_landmark, landmark_offset_pred)
            color_loss,layer_loss,type_loss = self.lossfn.attr_loss(gt_label,gt_attr,attr_pred)

            total_loss = cls_loss + box_offset_loss * 0.5 + landmark_loss + color_loss*0.5 + layer_loss*0.5 + type_loss*0.5
            accuracy_cls,accuracy_color,accuracy_layer,accuracy_type = self.compute_accuracy(cls_pred, gt_label, attr_pred, gt_attr)

            self.optimizer.zero_grad()
            total_loss.backward()
            self.optimizer.step()

            cls_loss_.update(cls_loss, data.size(0))
            box_offset_loss_.update(box_offset_loss, data.size(0))
            landmark_loss_.update(landmark_loss, data.size(0))
            total_loss_.update(total_loss, data.size(0))
            accuracy_cls_.update(accuracy_cls, data.size(0))
            accuracy_color_.update(accuracy_color, data.size(0))
            accuracy_layer_.update(accuracy_layer, data.size(0))
            accuracy_type_.update(accuracy_type, data.size(0))

            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}, cls_loss: {:.6f}, box_loss: {:.6f}, landmark_loss: {:.6f}, color_loss: {:.6f}, layer_loss: {:.6f}, type_loss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(self.train_loader.dataset),
                100. * batch_idx / len(self.train_loader), 
                total_loss.item(), cls_loss.item(), box_offset_loss.item(), landmark_loss.item(), 
                color_loss.item(),layer_loss.item(),type_loss.item()))
            print('Accuracy_cls: {:.6f}, Accuracy_color: {:.6f}, Accuracy_layer: {:.6f}, Accuracy_type: {:.6f}'.format(
                accuracy_cls.item(),accuracy_color.item(),accuracy_layer.item(),accuracy_type.item()))

        self.scalar_info['cls_loss'] = cls_loss_.avg
        self.scalar_info['box_offset_loss'] = box_offset_loss_.avg
        self.scalar_info['landmark_loss'] = landmark_loss_.avg
        self.scalar_info['total_loss'] = total_loss_.avg
        self.scalar_info['accuracy_cls'] = accuracy_cls_.avg
        self.scalar_info['accuracy_color'] = accuracy_color_.avg
        self.scalar_info['accuracy_layer'] = accuracy_layer_.avg
        self.scalar_info['accuracy_type'] = accuracy_type_.avg 
        self.scalar_info['lr'] = self.scheduler.get_lr()[0]

        if self.logger is not None:
            for tag, value in list(self.scalar_info.items()):
                self.logger.scalar_summary(tag, value, self.run_count)
            self.scalar_info = {}
        self.run_count += 1

        print("|===>Loss: {:.4f}".format(total_loss_.avg))
        return cls_loss_.avg, box_offset_loss_.avg, landmark_loss_.avg, total_loss_.avg, accuracy_cls_.avg, accuracy_color_.avg, accuracy_layer_.avg, accuracy_type_.avg