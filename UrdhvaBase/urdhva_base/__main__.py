import urdhva_base
import os
import sys
import typing
import uvicorn
import argparse
import urdhva_base.utilities

sys.path.append(os.getcwd())
parser = argparse.ArgumentParser(description='Parse Model & generate code for a target language.')
parser.add_argument('-c','--config', action='store_true', help='Sample config file.')
args = parser.parse_args()


if __name__ == "__main__":
    log_level: typing.Optional[str] = None
    reload: bool = urdhva_base.utilities.parse_bool(os.environ.get("AUTO_RELOAD", False))
    port: int = int(os.environ.get("PORT", 9002))
    host: str = os.environ.get("HOST", "127.0.0.1")
    # print(os.getcwd(), sys.path)
    if args.config:
        print(urdhva_base.settings.json(indent=2))
        sys.exit(0)

    if os.environ.get("MODE", "prod") == "dev":
        log_level = "debug"
        reload = True

    print(f"Running on {host}:{port}")

    uvicorn.run("urdhva_base.restapi:app", port=port, host=host, log_level=log_level,
                reload=reload, reload_dirs=[os.getcwd()])
