import sys
import os
import grpc
from concurrent import futures
import time

# -----------------------------------------------------------------------------
# 1. PATH SETUP (Crucial for finding the generated files)
# -----------------------------------------------------------------------------
# Get the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Define the path to the 'generated' folder (one level up)
generated_dir = os.path.join(current_dir, '../generated')
# Add it to the system path
sys.path.append(generated_dir)

# -----------------------------------------------------------------------------
# 2. IMPORTS
# -----------------------------------------------------------------------------
# Now we can import the generated protobuf code
import symbol_detector_pb2
import symbol_detector_pb2_grpc

# Import our custom logic
# We use try/except to handle running as a module vs running as a script
try:
    from server.model import SiameseNetwork
    from server.scanner import BlueprintScanner
except ImportError:
    from model import SiameseNetwork
    from scanner import BlueprintScanner

# -----------------------------------------------------------------------------
# 3. SERVER LOGIC
# -----------------------------------------------------------------------------
class SymbolDetectorServicer(symbol_detector_pb2_grpc.SymbolDetectorServicer):
    def __init__(self):
        print("Initializing Model and Scanner...")
        self.model = SiameseNetwork()
        self.scanner = BlueprintScanner(self.model)
        print("Server Ready.")

    def Predict(self, request, context):
        """Standard One-Shot Comparison"""
        try:
            print(f"Received Predict Request (Ref: {len(request.reference_image)} bytes)")
            
            # Pass raw bytes to the model
            result = self.model.predict(request.reference_image, request.query_image)
            
            msg = f"Score: {result['score']:.4f}"
            
            return symbol_detector_pb2.PredictResponse(
                similarity_score=result["score"],
                is_match=result["is_match"],
                message=msg
            )
        except Exception as e:
            print(f"Predict Error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return symbol_detector_pb2.PredictResponse()

    def ScanBlueprint(self, request, context):
        """New: Sliding Window Scan"""
        try:
            print(f"Received Scan Request (Blueprint: {len(request.blueprint_image)} bytes)")
            
            # Run the scanner
            # Note: We use a slightly lower threshold (0.60) for scanning to catch more candidates
            results = self.scanner.scan(request.reference_image, request.blueprint_image, threshold=0.85)
            
            # Convert python dictionaries to Proto BoundingBox objects
            proto_matches = []
            for r in results:
                proto_matches.append(symbol_detector_pb2.BoundingBox(
                    x=r['x'], 
                    y=r['y'], 
                    width=r['width'], 
                    height=r['height'], 
                    score=r['score']
                ))
            
            return symbol_detector_pb2.ScanResponse(
                matches=proto_matches,
                message=f"Scan complete. Found {len(proto_matches)} matches."
            )
        except Exception as e:
            print(f"Scan Error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return symbol_detector_pb2.ScanResponse()

# -----------------------------------------------------------------------------
# 4. STARTUP
# -----------------------------------------------------------------------------
def serve():
    # Allow up to 10 simultaneous requests
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    symbol_detector_pb2_grpc.add_SymbolDetectorServicer_to_server(
        SymbolDetectorServicer(), server
    )
    
    # Listen on port 50051
    server.add_insecure_port('[::]:50051')
    print("One Shot Detector Server started on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()