import numpy as np
from PIL import Image

class BlueprintScanner:
    def __init__(self, model):
        self.model = model

    def sliding_window(self, image, step_size, window_size):
        w, h = image.size
        # Use a larger step size (70% of window) to reduce total checks
        # This makes it faster and produces fewer duplicate boxes
        step_x = int(window_size[0] * 0.7)
        step_y = int(window_size[1] * 0.7)
        
        for y in range(0, h - window_size[1], step_y):
            for x in range(0, w - window_size[0], step_x):
                yield (x, y, image.crop((x, y, x + window_size[0], y + window_size[1])))

    def calculate_iou(self, boxA, boxB):
        # Determine the coordinates of the intersection rectangle
        xA = max(boxA['x'], boxB['x'])
        yA = max(boxA['y'], boxB['y'])
        xB = min(boxA['x'] + boxA['width'], boxB['x'] + boxB['width'])
        yB = min(boxA['y'] + boxA['height'], boxB['y'] + boxB['height'])

        # Compute the area of intersection rectangle
        interArea = max(0, xB - xA) * max(0, yB - yA)
        if interArea == 0: return 0

        # Compute the area of both rectangles
        boxAArea = boxA['width'] * boxA['height']
        boxBArea = boxB['width'] * boxB['height']

        # Compute IoU
        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou

    def apply_nms(self, boxes, iou_threshold=0.1): # aggressive threshold
        if not boxes: return []
        
        # Sort boxes by score (highest first)
        boxes = sorted(boxes, key=lambda x: x['score'], reverse=True)
        keep = []
        
        while boxes:
            current = boxes.pop(0)
            keep.append(current)
            
            remaining = []
            for box in boxes:
                iou = self.calculate_iou(current, box)
                # If they overlap AT ALL (0.1), kill the weaker one
                if iou < iou_threshold:
                    remaining.append(box)
            boxes = remaining
            
        return keep

    def scan(self, ref_bytes, blueprint_bytes, threshold=0.85): # <--- HIGH THRESHOLD
        ref_img = self.model._load_image(ref_bytes)
        blueprint_img = self.model._load_image(blueprint_bytes)
        
        win_w, win_h = ref_img.size
        
        # Pre-calculate Reference Embedding
        ref_tensor = self.model.preprocess(ref_bytes)
        ref_embedding = self.model.get_embedding(ref_tensor)

        matches = []
        
        # Dynamic step size based on window width
        step = int(win_w * 0.5)
        
        print(f"Scanning blueprint ({blueprint_img.size}) with window ({win_w}x{win_h})...")
        
        for (x, y, patch) in self.sliding_window(blueprint_img, step, (win_w, win_h)):
            patch_tensor = self.model.transform(patch).unsqueeze(0).to(self.model.device)
            patch_embedding = self.model.get_embedding(patch_tensor)
            score = self.model.compute_similarity(ref_embedding, patch_embedding)
            
            # Only keep VERY strong matches
            if score > threshold:
                matches.append({
                    "x": x, "y": y, 
                    "width": win_w, "height": win_h, 
                    "score": score
                })
        
        print(f"Raw candidates: {len(matches)}")
        
        # Apply NMS with a very aggressive overlap check (0.1)
        # This means if two boxes touch even slightly, we only keep the best one.
        clean_matches = self.apply_nms(matches, iou_threshold=0.1)
        
        print(f"Final matches: {len(clean_matches)}")
        return clean_matches