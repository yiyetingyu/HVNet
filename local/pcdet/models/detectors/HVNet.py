from .detector3d import Detector3D
from ...config import cfg


class HVNet(Detector3D):
    def __init__(self, num_class, dataset):
        super().__init__(num_class, dataset)
        self.build_networks(cfg.MODEL)
    
    def forward_rpn(self, input_dict):
        voxel_features = self.vfe(
            input_dict
        )
        rpn_preds_dict = self.rpn_head(
            voxel_features,
            **{'gt_boxes': input_dict.get('gt_boxes', None)}
        )
        return rpn_preds_dict

    def forward(self, input_dict):
        rpn_ret_dict = self.forward_rpn(input_dict)

        if self.training:
            loss, tb_dict, disp_dict = self.get_training_loss()

            ret_dict = {
                'loss': loss
            }
            return ret_dict, tb_dict, disp_dict

        else:
            pred_dicts, recall_dicts = self.predict_boxes(rpn_ret_dict, rcnn_ret_dict=None, input_dict=input_dict)
            return pred_dicts, recall_dicts

    def get_training_loss(self):
        disp_dict = {}

        loss_anchor_box, tb_dict = self.rpn_head.get_loss()
        loss_rpn = loss_anchor_box
        tb_dict = {
            'loss_rpn': loss_rpn,
            **tb_dict
        }

        loss = loss_rpn
        return loss, tb_dict, disp_dict