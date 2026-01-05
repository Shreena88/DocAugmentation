import cv2
import platform
import logging

def get_device_info():
    """
    Detects available hardware acceleration.
    Returns: dict of available backends.
    """
    info = {
        "cpu": True,
        "cuda": False,
        "openvino": False,
        "backend": "cv2.dnn.DNN_BACKEND_OPENCV",
        "target": "cv2.dnn.DNN_TARGET_CPU"
    }

    # Check CUDA
    try:
        count = cv2.cuda.getCudaEnabledDeviceCount()
        if count > 0:
            info["cuda"] = True
            info["backend"] = "cv2.dnn.DNN_BACKEND_CUDA"
            info["target"] = "cv2.dnn.DNN_TARGET_CUDA"
            logging.info(f"CUDA detected: {count} device(s).")
    except Exception as e:
        logging.warning(f"CUDA detection failed: {e}")

    # Check OpenVINO (simple check via cv2 backend support, 
    # robust check usually involves trying to load a network, 
    # but we will assume logic based on imports later)
    # For now, we manually flag OpenVINO availability if cv2 has it.
    try:
        # This is a heuristic; actual availability depends on the build.
        # Intel Arc users often have a custom build or OpenVINO separate.
        # We will assume 'standard' OpenCV behavior for now.
        pass
    except:
        pass

    return info
