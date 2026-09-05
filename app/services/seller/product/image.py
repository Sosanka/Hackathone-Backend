import cloudinary
import cloudinary.uploader

from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings


# ============================================================
# IMAGE CONFIGURATION
# ============================================================

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# ============================================================
# CLOUDINARY CONFIGURATION
# ============================================================

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


# ============================================================
# UPLOAD PRODUCT IMAGE
# ============================================================

async def save_product_image(
    image: UploadFile,
) -> str:

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not image.filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file",
        )

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    extension = Path(image.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed",
        )

    # --------------------------------------------------------
    # Validate content type
    # --------------------------------------------------------

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid image content type",
        )

    # --------------------------------------------------------
    # Read image
    # --------------------------------------------------------

    content = await image.read()

    # --------------------------------------------------------
    # Validate file size
    # --------------------------------------------------------

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size must be less than 5 MB",
        )

    # --------------------------------------------------------
    # Upload to Cloudinary
    # --------------------------------------------------------

    try:
        result = cloudinary.uploader.upload(
            content,
            folder="products",
            resource_type="image",
            use_filename=False,
            unique_filename=True,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload image",
        ) from exc

    # --------------------------------------------------------
    # Return Cloudinary URL
    # --------------------------------------------------------

    return result["secure_url"]


# ============================================================
# DELETE PRODUCT IMAGE
# ============================================================

def delete_product_image(
    image_url: str | None,
) -> None:

    if not image_url:
        return

    try:

        # ----------------------------------------------------
        # Extract Cloudinary path
        # ----------------------------------------------------

        parts = image_url.split("/upload/")

        if len(parts) != 2:
            return

        public_id_with_version = parts[1]

        # ----------------------------------------------------
        # Remove version
        #
        # Example:
        # v123456789/products/abc123.jpg
        #
        # becomes:
        # products/abc123.jpg
        # ----------------------------------------------------

        public_id_parts = public_id_with_version.split("/", 1)

        if len(public_id_parts) != 2:
            return

        public_id_with_extension = public_id_parts[1]

        # ----------------------------------------------------
        # Remove file extension
        #
        # products/abc123.jpg
        #
        # becomes:
        # products/abc123
        # ----------------------------------------------------

        public_id = str(
            Path(public_id_with_extension).with_suffix("")
        )

        # ----------------------------------------------------
        # Delete from Cloudinary
        # ----------------------------------------------------

        cloudinary.uploader.destroy(
            public_id,
            resource_type="image",
        )

    except Exception:
        # Do not fail the API request if deletion fails
        pass