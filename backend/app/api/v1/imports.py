"""Import API endpoints."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.import_batch import ImportBatch, ImportBatchList
from app.services.import_service import ImportService
from app.config import settings

router = APIRouter()


@router.post("/imports/upload", response_model=ImportBatch)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and import mBank CSV file.

    Args:
        file: CSV file upload
        db: Database session

    Returns:
        ImportBatch with import statistics

    Raises:
        HTTPException: If file too large, invalid format, or duplicate
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
        )

    # Get default user for MVP (single-user mode)
    import_service = ImportService(db, user_id=None)  # Will be set in service
    default_user_id = import_service.get_default_user_id()

    # Create import service with user
    import_service = ImportService(db, user_id=default_user_id)

    try:
        # Import CSV
        import_batch = await import_service.import_mbank_csv(
            file_content=content,
            file_name=file.filename
        )

        return import_batch

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error importing file: {str(e)}"
        )


@router.get("/imports", response_model=ImportBatchList)
async def list_imports(
    limit: int = 20,
    offset: int = 0,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    List import batches.

    Args:
        limit: Number of results
        offset: Offset for pagination
        status: Filter by status
        db: Database session

    Returns:
        List of import batches
    """
    from app.models import ImportBatch as ImportBatchModel, User

    # Get default user
    user = db.query(User).filter(User.email == 'default@finance.local').first()
    if not user:
        raise HTTPException(status_code=500, detail="Default user not found")

    # Build query
    query = db.query(ImportBatchModel).filter(
        ImportBatchModel.user_id == user.id
    )

    if status:
        query = query.filter(ImportBatchModel.import_status == status)

    # Get total count
    total = query.count()

    # Get paginated results
    imports = query.order_by(
        ImportBatchModel.created_at.desc()
    ).offset(offset).limit(limit).all()

    return ImportBatchList(imports=imports, total=total)


@router.get("/imports/{import_id}", response_model=ImportBatch)
async def get_import(
    import_id: str,
    db: Session = Depends(get_db)
):
    """
    Get import batch by ID.

    Args:
        import_id: Import batch UUID
        db: Database session

    Returns:
        Import batch details
    """
    from app.models import ImportBatch as ImportBatchModel
    from uuid import UUID

    try:
        import_uuid = UUID(import_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    import_batch = db.query(ImportBatchModel).filter(
        ImportBatchModel.id == import_uuid
    ).first()

    if not import_batch:
        raise HTTPException(status_code=404, detail="Import batch not found")

    return import_batch
