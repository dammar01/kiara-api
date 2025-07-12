from app.utils.common import CommonHelper
import uvicorn

if __name__ == "__main__":
    helper = CommonHelper()
    helper.check_cuda()
    uvicorn.run("app.main:app", port=5123, reload=True)
