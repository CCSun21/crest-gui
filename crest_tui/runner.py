"""Async job runner for CREST processes."""

import asyncio
import signal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Callable, Awaitable


class JobStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class Job:
    id: str
    command: list[str]
    status: JobStatus = JobStatus.PENDING
    output_lines: list[str] = field(default_factory=list)
    start_time: datetime | None = None
    end_time: datetime | None = None
    returncode: int | None = None
    _process: asyncio.subprocess.Process | None = field(default=None, repr=False, compare=False)


class JobRunner:
    """Manages CREST job execution."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def register_job(self, job: Job) -> None:
        self._jobs[job.id] = job

    async def run_job(
        self,
        job: Job,
        output_callback: Callable[[str], Awaitable[None]] | Callable[[str], None] | None = None,
    ) -> None:
        """Run a job asynchronously, streaming output via callback."""
        job.status = JobStatus.RUNNING
        job.start_time = datetime.now()
        job.output_lines.clear()

        try:
            process = await asyncio.create_subprocess_exec(
                *job.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            job._process = process

            assert process.stdout is not None
            async for raw_line in process.stdout:
                line = raw_line.decode("utf-8", errors="replace").rstrip()
                job.output_lines.append(line)
                if output_callback is not None:
                    result = output_callback(line)
                    if asyncio.iscoroutine(result):
                        await result

            await process.wait()
            job.returncode = process.returncode
            job.end_time = datetime.now()

            if process.returncode == 0:
                job.status = JobStatus.COMPLETED
            elif job.status != JobStatus.CANCELLED:
                job.status = JobStatus.FAILED

        except FileNotFoundError:
            job.status = JobStatus.FAILED
            job.end_time = datetime.now()
            msg = f"Error: binary not found: {job.command[0]}"
            job.output_lines.append(msg)
            if output_callback is not None:
                result = output_callback(msg)
                if asyncio.iscoroutine(result):
                    await result
        except Exception as exc:
            job.status = JobStatus.FAILED
            job.end_time = datetime.now()
            msg = f"Error: {exc}"
            job.output_lines.append(msg)
            if output_callback is not None:
                result = output_callback(msg)
                if asyncio.iscoroutine(result):
                    await result

    def cancel_job(self, job: Job) -> None:
        """Send SIGTERM to the running process."""
        if job._process is not None and job.status == JobStatus.RUNNING:
            try:
                job._process.send_signal(signal.SIGTERM)
                job.status = JobStatus.CANCELLED
            except ProcessLookupError:
                pass

    def get_job(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def list_jobs(self) -> list[Job]:
        return list(self._jobs.values())
