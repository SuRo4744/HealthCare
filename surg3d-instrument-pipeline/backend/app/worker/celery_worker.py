from celery import Celery
from app.config import settings
from app.services.zed_extractor import extract_zed2i_instrument_frames
from app.services.sam2_segmenter import segment_surgical_instrument
from app.services.reconstruct_3d import run_instrument_3d_reconstruction

celery_app = Celery("surg3d_worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

@celery_app.task(name="reconstruct_surgical_instrument_task")
def reconstruct_surgical_instrument_task(instrument_id: str, svo_or_mp4_path: str):
    frames_meta = extract_zed2i_instrument_frames(svo_or_mp4_path, f"{settings.STORAGE_DIR}/{instrument_id}_frames")
    seg_meta = segment_surgical_instrument(f"{settings.STORAGE_DIR}/{instrument_id}_frames")
    mesh_meta = run_instrument_3d_reconstruction(instrument_id, settings.STORAGE_DIR)
    return {
        "instrument_id": instrument_id,
        "frames": frames_meta,
        "segmentation": seg_meta,
        "mesh": mesh_meta
    }
