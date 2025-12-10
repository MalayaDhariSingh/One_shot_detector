# client/grpc_client.py
import grpc
import sys
import os
import argparse

# -----------------------------------------------------------------------------
# 1. Setup Path to find Generated Files
# -----------------------------------------------------------------------------
# Finds the folder relative to where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))
generated_dir = os.path.join(current_dir, '../generated')

# Add 'generated' to Python's search path BEFORE importing protobufs
sys.path.append(generated_dir)

import symbol_detector_pb2
import symbol_detector_pb2_grpc

# -----------------------------------------------------------------------------
# 2. Client Logic
# -----------------------------------------------------------------------------
def run_prediction(ref_path, query_path):
    """
    Sends two images to the gRPC server and returns the response object.
    """
    # Check if files exist
    if not os.path.exists(ref_path):
        print(f"Error: Reference file not found at: {ref_path}")
        return None
    if not os.path.exists(query_path):
        print(f"Error: Query file not found at: {query_path}")
        return None

    # Read images as raw bytes
    try:
        with open(ref_path, "rb") as f:
            ref_bytes = f.read()
        with open(query_path, "rb") as f:
            query_bytes = f.read()
    except Exception as e:
        print(f"Error reading files: {e}")
        return None

    print(f"Connecting to server at localhost:50051...")
    
    # Open gRPC Channel
    # (Increase max message size if sending high-res images, e.g., 10MB)
    options = [('grpc.max_send_message_length', 10 * 1024 * 1024),
               ('grpc.max_receive_message_length', 10 * 1024 * 1024)]
               
    with grpc.insecure_channel('localhost:50051', options=options) as channel:
        stub = symbol_detector_pb2_grpc.SymbolDetectorStub(channel)
        
        # Create Request Object
        request = symbol_detector_pb2.PredictRequest(
            reference_image=ref_bytes,
            query_image=query_bytes
        )

        try:
            print(f"Sending request... (Ref: {len(ref_bytes)} bytes, Query: {len(query_bytes)} bytes)")
            response = stub.Predict(request)
            return response
        except grpc.RpcError as e:
            print(f"❌ gRPC Failed: {e.code()}")
            print(f"   Details: {e.details()}")
            return None
# client/grpc_client.py

# ... (Previous imports and run_prediction function remain the same) ...

def scan_blueprint(ref_path, blueprint_path):
    """
    Sends a reference symbol and a full blueprint to the server.
    Returns the ScanResponse object containing bounding boxes.
    """
    if not os.path.exists(ref_path) or not os.path.exists(blueprint_path):
        return None

    # Read images
    with open(ref_path, "rb") as f:
        ref_bytes = f.read()
    with open(blueprint_path, "rb") as f:
        blue_bytes = f.read()

    # Increase message size limit (Blueprints can be large!)
    options = [('grpc.max_send_message_length', 50 * 1024 * 1024),
               ('grpc.max_receive_message_length', 50 * 1024 * 1024)]

    with grpc.insecure_channel('localhost:50051', options=options) as channel:
        stub = symbol_detector_pb2_grpc.SymbolDetectorStub(channel)
        
        request = symbol_detector_pb2.ScanRequest(
            reference_image=ref_bytes,
            blueprint_image=blue_bytes
        )

        try:
            print("Sending Scan Request...")
            response = stub.ScanBlueprint(request)
            return response
        except grpc.RpcError as e:
            print(f"Scan Failed: {e.code()} - {e.details()}")
            return None
# -----------------------------------------------------------------------------
# 3. Main Execution (CLI)
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# 3. Main Execution
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    #  vvv  PASTE YOUR PATHS HERE  vvv
    
    # Windows Example: r"C:\Users\Name\Desktop\symbol.png" (Use 'r' for Windows paths)
    # Mac/Linux Example: "/Users/name/Desktop/symbol.png"
    
    my_ref_path = r"C:\Users\dhari\Downloads\logo.jpg" 
    my_query_path = r"C:\Users\dhari\Downloads\bg.jpg"

    print(f"Testing with:\nRef: {my_ref_path}\nQuery: {my_query_path}\n")

    # Run the function
    result = run_prediction(my_ref_path, my_query_path)
    
    if result:
        print(f"\n--- ✅ Server Response ---")
        print(f"Similarity Score: {result.similarity_score:.4f}")
        print(f"Match Found:      {result.is_match}")
        print(f"Server Message:   {result.message}")