import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io

class SiameseNetwork:
    def __init__(self):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Model initializing on {self.device}...")
        
        weights = models.ResNet18_Weights.DEFAULT
        self.base_model = models.resnet18(weights=weights)
        self.feature_extractor = torch.nn.Sequential(*list(self.base_model.children())[:-1])
        self.feature_extractor.to(self.device)
        self.feature_extractor.eval()

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _load_image(self, image_bytes):
        return Image.open(io.BytesIO(image_bytes)).convert("RGB")

    def preprocess(self, image_bytes):
        image = self._load_image(image_bytes)
        tensor = self.transform(image).unsqueeze(0)
        return tensor.to(self.device)

    def get_embedding(self, tensor):
        """Returns the embedding vector for a tensor."""
        with torch.no_grad():
            emb = self.feature_extractor(tensor).flatten()
        return emb

    def compute_similarity(self, emb1, emb2):
        """Calculates cosine similarity between two embeddings."""
        cos = nn.CosineSimilarity(dim=0)
        return cos(emb1, emb2).item()

    # Keep the old predict method for backward compatibility
    def predict(self, ref_bytes, query_bytes, threshold=0.75):
        emb_ref = self.get_embedding(self.preprocess(ref_bytes))
        emb_query = self.get_embedding(self.preprocess(query_bytes))
        score = self.compute_similarity(emb_ref, emb_query)
        return {"score": score, "is_match": score > threshold}