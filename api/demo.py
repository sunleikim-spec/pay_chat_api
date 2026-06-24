from fastapi import APIRouter

router = APIRouter(prefix="/api/demo", tags=["演示接口"])

@router.get("/test")
async def test():
    return {"data": "分组路由测试成功"}