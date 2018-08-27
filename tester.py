#!/usr/bin/env python3

from flask import Flask, request
import argparse
import datetime
import hashlib
import requests

target_count = 10
app = Flask("tester")


def submit_job():
    update_seed()
    difficulty = app.difficulty
    miner_port = app.miner_port
    problem = app.seed
    content = {'result': [
        f"0x{problem}",
        difficulty]}
    requests.post(f"http://127.0.0.1:{miner_port}", json=content)
    print(f"Send job {content} to {miner_port}")
    app.last_request_time = datetime.datetime.now()


def update_seed():
    h = hashlib.blake2b()
    h.update(app.seed.encode('utf-8'))
    app.seed = h.hexdigest()[:64]


@app.route('/', methods=['POST'])
def submit():
    now = datetime.datetime.now()
    diff = (now - app.last_request_time).total_seconds()
    app.durations.append(diff)
    print(f"{diff} seconds for a job")
    if app.repeat <= len(app.durations):
        durations = sorted(app.durations)
        print(f"finish\t: {durations}")
        print(f"min\t: {durations[0]}")
        print(f"q1\t: {durations[int(len(durations) / 4)]}")
        print(f"median\t: {durations[int(len(durations) / 2)]}")
        print(f"q3\t: {durations[int(len(durations) - len(durations) / 4)]}")
        print(f"max\t: {durations[-1]}")
        print(f"mean\t: {sum(durations) / len(durations)}")
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
    submit_job()
    return ""


def parse_args():
    sample = '0x7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
    default_port = 8080
    default_miner = 3333
    default_repeat = 10
    default_seed = 0

    parser = argparse.ArgumentParser(description='A miner tester')
    parser.add_argument('--difficulty',
                        help=f"A difficulty in hex string. (e.x. {sample})")
    parser.add_argument('--port', default=default_port, type=int, help=f"A listening port (default: {default_port})")
    parser.add_argument('--miner', default=3333, type=int, help=f"A miner port (default: {default_miner})")
    parser.add_argument('--repeat', default=10, type=int, help=f"The number of repeat (default: {default_repeat})")
    parser.add_argument('--seed', default=0, type=int, help=f"A random seed (default: {default_seed})")
    return parser.parse_args()


def main():
    args = parse_args()
    difficulty = args.difficulty
    port = args.port
    miner_port = args.miner
    repeat = args.repeat
    seed = args.repeat

    if difficulty is None:
        print("No difficulty")
        exit(-1)

    app.repeat = repeat
    app.miner_port = miner_port
    app.difficulty = difficulty
    app.durations = []
    app.seed = str(seed)

    submit_job()
    app.run(host="127.0.0.1", port=port)


if __name__ == '__main__':
    main()
