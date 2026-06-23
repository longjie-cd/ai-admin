from fastapi import HTTPException, status
from api.sys.api_interface import crud
from api.sys.api_interface.schema import ApiInterfaceCreate, ApiInterfaceUpdate, ApiInterfaceOut, ApiInterfaceListOut


def list_apis() -> ApiInterfaceListOut:
    items = crud.list_all()
    return ApiInterfaceListOut(total=len(items), items=[ApiInterfaceOut(**item) for item in items])


def get_api(api_id: int) -> ApiInterfaceOut:
    item = crud.get_by_id(api_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API 接口不存在")
    return ApiInterfaceOut(**item)


def create_api(body: ApiInterfaceCreate) -> ApiInterfaceOut:
    if crud.get_by_path_and_method(body.path, body.method):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="API 接口已存在")
    item = crud.create(body.model_dump())
    return ApiInterfaceOut(**item)


def update_api(api_id: int, body: ApiInterfaceUpdate) -> ApiInterfaceOut:
    item = crud.update(api_id, body.model_dump(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API 接口不存在")
    return ApiInterfaceOut(**item)


def delete_api(api_id: int) -> None:
    if not crud.delete(api_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API 接口不存在")
