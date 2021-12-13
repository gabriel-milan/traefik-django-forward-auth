#!/env/bin/python

from functools import partial
from os import getenv
import subprocess
from threading import Thread
from time import sleep
from typing import Callable, Union

from loguru import logger


def do_nothing(text_or_rc: Union[str, int]) -> None:
    pass


def log_error_and_skip(rc: int, text: str) -> None:
    logger.error(f"Error {rc} from {text}")


def log_error_and_raise(rc: int, text: str) -> None:
    logger.error(f"Error {rc} from {text}")
    raise Exception(f"Error {rc} from {text}")


@logger.catch
def run_shell_command(
    command: str,
    stdout_callback: Callable[[str], None] = do_nothing,
    on_error: Callable[[int], None] = do_nothing,
) -> int:
    popen = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        stdout_callback(stdout_line)
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        return on_error(return_code)
    return return_code


@logger.catch
def create_super_user() -> None:
    if (
        getenv("DJANGO_SUPERUSER_USERNAME")
        and
        getenv("DJANGO_SUPERUSER_PASSWORD")
    ):
        # Migrate database
        run_shell_command(
            "cd /app; python3 manage.py migrate",
            stdout_callback=logger.info,
            on_error=partial(log_error_and_skip, text="migrate"),
        )
        # Create super user
        email = getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        run_shell_command(
            f"cd /app; python3 manage.py createsuperuser --noinput --email {email}",
            stdout_callback=logger.info,
            on_error=partial(log_error_and_skip, text="create super user"),
        )


@logger.catch
def start_threaded_gunicorn() -> None:
    thread = Thread(
        target=run_shell_command,
        args=(
            "cd /app; gunicorn forward_auth.wsgi --bind 0.0.0.0:8000 --workers 3 --log-level debug",
            logger.info,
            partial(log_error_and_raise, text="gunicorn"),
        ),
        daemon=True,
    )
    thread.start()
    return thread


@logger.catch
def start_threaded_nginx() -> None:
    thread = Thread(
        target=run_shell_command,
        args=(
            "nginx -g \"daemon off;\"",
            logger.info,
            partial(log_error_and_raise, text="nginx"),
        ),
        daemon=True,
    )
    thread.start()
    return thread


if __name__ == "__main__":
    create_super_user()
    thread_gunicorn = start_threaded_gunicorn()
    thread_nginx = start_threaded_nginx()
    while True:
        sleep(1)
        if not thread_gunicorn.is_alive() or not thread_nginx.is_alive():
            logger.error("One of the threads died, please check logs")
            break
