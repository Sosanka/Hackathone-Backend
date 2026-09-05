import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile


UPLOAD_DIR = Path("uploads/products")

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


async def save_product_image(
    image: UploadFile,
) -> str:

    if not image.filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file",
        )

    extension = Path(image.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed",
        )

    content = await image.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size must be less than 5 MB",
        )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = f"{uuid.uuid4().hex}{extension}"

    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as file:
        file.write(content)

    return f"/uploads/products/{filename}"


def delete_product_image(
    image_url: str | None,
) -> None:

    if not image_url:
        return

    filename = Path(image_url).name

    file_path = UPLOAD_DIR / filename

    if file_path.exists():
        os.remove(file_path)