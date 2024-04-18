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
from ultralytics.yolo.utils.plotting import Annotator, colors
import json
word_set ={
    "IND",
    " ",
    "-",
    "_",
     "MARUTI SUZUKI",
    "HYUNDAI",
    "TATA MOTORS",
    "MAHINDRA & MAHINDRA",
    "TOYOTA",
    "HONDA",
    "FORD",
    "RENAULT",
    "NISSAN",
    "VOLKSWAGEN",
    "MERCEDES-BENZ",
    "BMW",
    "AUDI",
    "SKODA",
    "VOLVO",
    "JEEP",
    "KIA",
    "MG MOTOR",
    "JAGUAR LAND ROVER",
    "FIAT",
    "LAMBORGHINI",
    "PORSCHE",
    "ROLLS-ROYCE",
    "BENTLEY",
    "ASTON MARTIN",
    "FERRARI",
    "MASERATI",
    "ISUZU",
    "FORCE MOTORS",
    "PREMIER",
    "BAJAJ AUTO",
    "TVS MOTORS",
    "HERO MOTOCORP",
    "ROYAL ENFIELD",
    "MAHINDRA TWO WHEELERS",
    "YAMAHA",
    "SUZUKI MOTORCYCLE",
    "KAWASAKI",
    "TRIUMPH MOTORCYCLES",
    "HARLEY-DAVIDSON",
    "HYOSUNG",
    "INDIAN MOTORCYCLE",
    "PIAGGIO",
    "DUCATI",
    "APRILIA",
    "BENELLI",
    "MV AGUSTA",
    "NORTON",
    "HUSQVARNA",
    "BMW MOTORRAD",
    "KTM",
    "JAWA",
    "TRIUMPH MOTORCYCLES",
    "KYMCO",
    "OLA ELECTRIC",
    "MANHONDA",
    "SUDARSHANHONDA"
}

class DetectionPredictor(BasePredictor):

    def __init__(self, cfg, save_dir):
        super().__init__(cfg)
        self.save_dir = save_dir

    def get_annotator(self, img):
        line_width = 1
        return Annotator(img, line_width=line_width, example=str(self.model.names))

    def preprocess(self, img):
        img = torch.from_numpy(img).to(self.model.device)
        img = img.half() if self.model.fp16 else img.float()
        img /= 255
        return img

    def postprocess(self, preds, img, orig_img):
        preds = ops.non_max_suppression(preds,
                                        self.args.conf,
                                        self.args.iou,
                                        agnostic=self.args.agnostic_nms,
                                        max_det=self.args.max_det)

        for i, pred in enumerate(preds):
            shape = orig_img[i].shape if self.webcam else orig_img.shape
            pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], shape).round()

        return preds

    def write_results(self, idx, preds, batch):
        p, im, im0 = batch
        log_string = ""
        if len(im.shape) == 3:
            im = im[None]
        self.seen += 1
        im0 = im0.copy()
        if self.webcam:
            log_string += f'{idx}: '
            frame = self.dataset.count
        else:
            frame = getattr(self.dataset, 'frame', 0)

        self.data_path = p
        self.txt_path = os.path.join(self.save_dir, 'labels', os.path.splitext(p)[0]) + (
            '' if self.dataset.mode == 'image' else f'_{frame}')
        log_string += '%gx%g ' % im.shape[2:]
        self.annotator = self.get_annotator(im0)

        det = preds[idx]
        self.all_outputs.append(det)
        if len(det) == 0:
            return log_string

        # extracted_texts=[]
        for i, (*xyxy, conf, cls) in enumerate(reversed(det)):
            c = int(cls)
            label = None if self.args.hide_labels else self.model.names[c]

            if label != "license_plate":
                self.annotator.box_label(xyxy, label, color=colors(c, True))

                x1, y1, x2, y2 = map(int, xyxy)
                object_img = im0[y1:y2, x1:x2]
                object_pil_img = Image.fromarray(object_img)
                object_pil_img.save(
                    self.save_dir / 'results' / f'{os.path.splitext(os.path.basename(p))[0]}_object_{idx}_{i}.jpg')

                # Perform OCR on the cropped object image
                # print("performing ocr")
                print(object_pil_img)
                # object_text = self.perform_ocr(object_pil_img)
                # print("OCR Text:", object_text)
                # extracted_texts.append(object_text)

                # os.remove(self.save_dir / 'results' / f'{os.path.splitext(os.path.basename(p))[0]}_object_{idx}_{i}.jpg')

        # print(log_string)
        # print(extracted_texts)
        return log_string
    
    def perform_ocr(self, image):
        # Convert image to byte stream
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        # Prepare form data
        form_data = {
            'image': ('image.jpg', img_byte_arr)
        }

        # Make POST request to OCR API endpoint
        headers = {
            'X-RapidAPI-Key': '139c90d5bdmsh887cd3b63935516p1969a0jsn785beb400347',
            'X-RapidAPI-Host': 'ocr43.p.rapidapi.com'
        }
        response = requests.post('https://ocr43.p.rapidapi.com/v1/results', headers=headers, files=form_data)

        ocr_response=response.json()
        text=ocr_response['results'][0]['entities'][0]['objects'][0]['entities'][0]['text']
        text=self.parse_rc_number(text,word_set)
        if response.status_code == 200:
            return text
        else:
            return "Error performing OCR"
    
    def parse_rc_number(self, extracted_text, word_set):
        text_blocks = extracted_text.split('\n')
        result = ""
        for text in text_blocks:
            if text not in word_set and len(text) >= 2:
                result += text
            if(len(result)>=10):
                break
        result = result.replace(" ", "")
        return result


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