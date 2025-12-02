import numpy as np
import faiss
import os
from db import get_db
from sqlalchemy import text

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(ROOT, ".."))
EMBED_DIR = os.path.join(BASE, "data", "embeddings")

os.makedirs(EMBED_DIR, exist_ok=True)

EMB_PATH = os.path.join(EMBED_DIR, "jobs_embeddings.npy")
IDS_PATH = os.path.join(EMBED_DIR, "job_ids.npy")
META_PATH = os.path.join(EMBED_DIR, "job_metadatas.npy")
TITLE_PATH = os.path.join(EMBED_DIR, "job_title_embs.npy")
INDEX_PATH = os.path.join(EMBED_DIR, "faiss_index.bin")


def delete_job_embeddings():
    # Validate input
    db = next(get_db())
    result = db.execute(text("""SELECT job_id
            FROM remarkhr.jobs
            WHERE job_status = 0
            AND job_updated_on >= NOW() - INTERVAL 12 HOUR;"""))
    rows = result.fetchall()
    db.close()

    if not rows:
        print("⚠ No inactive jobs found in last 12 hours.")
        return False

    # Convert to list of ints
    job_ids_to_delete = [row[0] for row in rows]

    if not isinstance(job_ids_to_delete, list):
        raise ValueError("job_ids_to_delete must be a list")

    # Check required files
    required = [EMB_PATH, IDS_PATH, META_PATH, TITLE_PATH, INDEX_PATH]
    if not all(os.path.exists(p) for p in required):
        print("❌ Missing embedding or index files.")
        return False

    # Load existing files
    embs = np.load(EMB_PATH)
    ids = np.load(IDS_PATH)
    metas = np.load(META_PATH, allow_pickle=True)
    title_embs = np.load(TITLE_PATH, allow_pickle=True)

    print(f"🗑 Trying to delete job_ids: {job_ids_to_delete}")

    # Convert to numpy for fast delete
    job_ids_to_delete = np.array(job_ids_to_delete)

    # Find all matching indexes
    delete_idxs = np.where(np.isin(ids, job_ids_to_delete))[0]

    if len(delete_idxs) == 0:
        print("⚠ No matching job_ids found. Nothing deleted.")
        return False

    print(f"🗑 Deleting {len(delete_idxs)} embeddings → Indexes: {delete_idxs}")

    # Delete rows from all arrays
    embs = np.delete(embs, delete_idxs, axis=0)
    ids = np.delete(ids, delete_idxs, axis=0)
    metas = np.delete(metas, delete_idxs, axis=0)
    title_embs = np.delete(title_embs, delete_idxs, axis=0)

    # 🔥 Rebuild FAISS (very fast)
    dim = embs.shape[1]
    faiss.normalize_L2(embs.astype("float32"))
    new_index = faiss.IndexFlatIP(dim)
    new_index.add(embs.astype("float32"))

    # Save updated files
    np.save(EMB_PATH, embs)
    np.save(IDS_PATH, ids)
    np.save(META_PATH, metas, allow_pickle=True)
    np.save(TITLE_PATH, title_embs, allow_pickle=True)
    faiss.write_index(new_index, INDEX_PATH)

    print("✅ Multiple job embeddings deleted & FAISS index updated.")
    return True

