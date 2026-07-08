from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uuid
import json
from app.presentation.routers.auth_router import get_current_user
from app.infrastructure.execution.tasks import execute_code_task
from celery.result import AsyncResult
import asyncio

router = APIRouter()

class ExecuteRequest(BaseModel):
    code: str

class ExecuteResponse(BaseModel):
    job_id: str
    status: str

@router.post("/", response_model=ExecuteResponse)
async def execute_code(req: ExecuteRequest, current_user: dict = Depends(get_current_user)):
    job_id = str(uuid.uuid4())
    # Send to celery
    task = execute_code_task.apply_async(args=[req.code, job_id], task_id=job_id)
    return {"job_id": job_id, "status": "queued"}

@router.get("/{job_id}")
async def get_execution_status(job_id: str, current_user: dict = Depends(get_current_user)):
    task_result = AsyncResult(job_id)
    if task_result.state == 'PENDING':
        return {"job_id": job_id, "status": "pending"}
    elif task_result.state == 'SUCCESS':
        return {"job_id": job_id, "status": "completed", "result": task_result.result}
    elif task_result.state == 'FAILURE':
        return {"job_id": job_id, "status": "failed", "error": str(task_result.info)}
    else:
        return {"job_id": job_id, "status": task_result.state}

@router.websocket("/ws/interactive")
async def interactive_websocket(websocket: WebSocket):
    await websocket.accept()
    # Expect the first message to be the code to execute
    try:
        init_data = await websocket.receive_text()
        req_data = json.loads(init_data)
        code = req_data.get("code", "")
    except Exception as e:
        await websocket.close(code=1003, reason="Invalid initialization data")
        return

    process = None
    try:
        # Launch Docker interactively, capturing stdin/stdout
        process = await asyncio.create_subprocess_exec(
            "docker", "run", "-i", "--rm", 
            "--network=none", "--pids-limit=64", "--memory=128m",
            "sandbox-python:3.12-slim", "python", "-u", "-c", code,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        async def read_stdout():
            try:
                while True:
                    data = await process.stdout.read(1024)
                    if not data:
                        break
                    await websocket.send_text(json.dumps({
                        "type": "output", 
                        "data": data.decode('utf-8', errors='replace')
                    }))
            except Exception:
                pass

        async def read_ws():
            try:
                while True:
                    msg = await websocket.receive_text()
                    msg_data = json.loads(msg)
                    if msg_data.get("type") == "input":
                        stdin_data = msg_data.get("data", "")
                        if process.stdin:
                            process.stdin.write(stdin_data.encode('utf-8'))
                            await process.stdin.drain()
            except WebSocketDisconnect:
                pass
            except Exception:
                pass

        stdout_task = asyncio.create_task(read_stdout())
        ws_task = asyncio.create_task(read_ws())

        # Wait for the process to finish
        await process.wait()
        
        # Ensure all stdout is flushed
        await stdout_task
        
        # Stop listening for input since the process is dead
        ws_task.cancel()
        
        await websocket.send_text(json.dumps({"type": "status", "status": "completed"}))

    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"type": "status", "status": "failed", "error": str(e)}))
        except:
            pass
    finally:
        if process and process.returncode is None:
            try:
                process.terminate()
            except:
                pass
        try:
            await websocket.close()
        except:
            pass
