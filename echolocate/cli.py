import argparse
from datetime import datetime
from pathlib import Path

from .audio import ItemRecognizer, RoomFingerprint, EchoLocateRunner, record_audio
from .db import last_seen
from .http_api import run_server

fingerprint = RoomFingerprint()
recognizer = ItemRecognizer()
runner = EchoLocateRunner(recognizer, fingerprint)


def cmd_teach(args):
    path = Path(args.file)
    if not path.exists():
        print(f"File {path} does not exist")
        return
    recognizer.teach(args.item, path)
    print(f"Learned sound for {args.item}")


def cmd_run(args):
    fingerprint.cluster()
    runner.start()
    print("Listening... press Ctrl+C to stop")
    try:
        run_server(host='127.0.0.1', port=args.port)
    except KeyboardInterrupt:
        pass
    finally:
        runner.stop()


def cmd_where(args):
    zone, ts = last_seen(args.item)
    if ts is None:
        print("No data for", args.item)
    else:
        delta = datetime.utcnow() - ts
        minutes = int(delta.total_seconds() // 60)
        print(f"{zone}, {minutes} min ago")


def main(argv=None):
    parser = argparse.ArgumentParser(prog='echolocate')
    sub = parser.add_subparsers(dest='command')

    teach_p = sub.add_parser('teach')
    teach_p.add_argument('item')
    teach_p.add_argument('file')
    teach_p.set_defaults(func=cmd_teach)

    run_p = sub.add_parser('run')
    run_p.add_argument('--port', type=int, default=8000)
    run_p.set_defaults(func=cmd_run)

    where_p = sub.add_parser('where')
    where_p.add_argument('item')
    where_p.set_defaults(func=cmd_where)

    args = parser.parse_args(argv)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
