import hydra
import json
import requests
from io import BytesIO
import torch
import os
from pathlib import Path
from PIL import Image
from ultralytics.yolo.engine.predictor import BasePredictor
from ultralytics.yolo.utils import DEFAULT_CONFIG, ROOT, ops
from ultralytics.yolo.utils.checks import check_imgsz

class DetectionPredictor(BasePredictor):
    def __init__(self, cfg, save_dir):
        super().__init__(cfg)
        self.save_dir = save_dir

    def get_annotator(self, img):
        return None  # We don't need an annotator in this case

    def preprocess(self, img):
        img = torch.from_numpy(img).to(self.model.device)
        img = img.half() if self.model.fp16 else img.float()
        img /= 255
        return img

    def postprocess(self, preds, img, orig_img):
        preds = ops.non_max_suppression(preds, self.args.conf, self.args.iou, agnostic=self.args.agnostic_nms, max_det=self.args.max_det)
        for i, pred in enumerate(preds):
            shape = orig_img[i].shape if self.webcam else orig_img.shape
            pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], shape).round()
        return preds

    def write_results(self, idx, preds, batch):
        p, im, im0 = batch
        if len(im.shape) == 3:
            im = im[None]
        self.seen += 1
        im0 = im0.copy()
        if self.webcam:
            frame = self.dataset.count
        else:
            frame = getattr(self.dataset, 'frame', 0)
        self.data_path = p
        self.txt_path = os.path.join(self.save_dir, 'labels', os.path.splitext(p)[0]) + ('' if self.dataset.mode == 'image' else f'_{frame}')

        det = preds[idx]
        for i, (*xyxy, conf, cls) in enumerate(reversed(det)):
            if int(cls) == self.model.names.index("license_plate"):
                x1, y1, x2, y2 = map(int, xyxy)
                object_img = im0[y1:y2, x1:x2]
                object_pil_img = Image.fromarray(object_img)
                object_pil_img.save(self.save_dir / 'results' / f'{os.path.splitext(os.path.basename(p))[0]}_object_{idx}_{i}.jpg')

@hydra.main(version_base=None, config_path=str(DEFAULT_CONFIG.parent), config_name=DEFAULT_CONFIG.name)
def predict(cfg):
    cfg.model = cfg.model or "yolov8n.pt"
    cfg.imgsz = check_imgsz(cfg.imgsz, min_dim=2)
    cfg.source = cfg.source if cfg.source is not None else ROOT / "assets"
    save_dir = Path(cfg.save_dir) if hasattr(cfg, 'save_dir') else Path.cwd()
    predictor = DetectionPredictor(cfg, save_dir)
    predictor()

if __name__ == "__main__":
    predict()