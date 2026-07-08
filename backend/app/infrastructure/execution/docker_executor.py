import docker
from app.domain.ports.code_executor import ICodeExecutor
from app.domain.entities.models import ExecutionResult
import time

class DockerCodeExecutor(ICodeExecutor):
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception:
            # Fallback if docker socket isn't mounted correctly during some testing
            self.client = None

    def _execute_sync(self, code: str, job_id: str) -> ExecutionResult:
        if not self.client:
            return ExecutionResult(job_id=job_id, exit_code=-1, output="Docker client not initialized")
        
        container = None
        start_time = time.time()
        try:
            container = self.client.containers.run(
                image="sandbox-python:3.12-slim",
                command=["python3", "-c", code],
                detach=True,
                network_disabled=True,
                read_only=True,
                tmpfs={"/tmp": "size=16m,mode=1777"},
                mem_limit="128m",
                # nano_cpus=int(0.5 * 1e9), # might not be supported on all windows docker hosts
                # pids_limit=64, # might not be supported on all windows docker hosts
                security_opt=["no-new-privileges:true"],
                cap_drop=["ALL"],
                stdout=True, stderr=True,
            )
            try:
                exited = container.wait(timeout=10)
                exit_code = exited["StatusCode"]
            except Exception as e:
                container.kill()
                exit_code = -1
                
            logs = container.logs().decode("utf-8", errors="replace")
            duration_ms = int((time.time() - start_time) * 1000)
            
            return ExecutionResult(
                job_id=job_id,
                exit_code=exit_code,
                output=logs[:20_000],
                duration_ms=duration_ms
            )
        except Exception as exc:
            return ExecutionResult(job_id=job_id, exit_code=-1, output=str(exc))
        finally:
            if container:
                try:
                    container.remove(force=True)
                except:
                    pass

    async def execute(self, code: str, job_id: str) -> ExecutionResult:
        # Docker SDK is synchronous, so we could run it in a threadpool
        import asyncio
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._execute_sync, code, job_id)
