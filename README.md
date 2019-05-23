# JollyCoin Node

JollyCoin (JLC) is a peer-to-peer Internet currency that enables instant, near-zero cost payments to anyone in the world. JollyCoin is an open source, global payment network that is fully decentralized without any central authorities with exception of Coordinator node. In order to protect network for bad actors, JollyCoin will use Coordinator node for some time. It is Coordinator's job to handle unconfirmed transactions, and to finally accept mined blocks.


## Setup

We highly recommend using Ubuntu 18.04 64-bit.

First you need appropriate Python environment:

```
sudo apt-get update -y
sudo apt-get install -y python3.6 python3.6-dev build-essential libssl-dev libffi-dev python-virtualenv
```

After unpacking archive, do the following:

```
cd jollycoin-node

python3.6 -m virtualenv -p `which python3.6` venv
source venv/bin/activate
pip install -r requirements.txt
```


## Run Mining Node

Make sure that you have source'ed into `virtualenv` environment from project directory.

```
source venv/bin/activate
```

Then run:

```
python -B node.py
```


## Run Test Mining Node

Use this only for testing purposes and not for real mining!

```
python -B node.py --host "0.0.0.0" --port 8081 --db "sqlite:///node.db" --coordinator "http://127.0.0.1:8080"
```


## Run Test Coordinator Node

Use this only for testing purposes!

```
python -B node.py --host "0.0.0.0" --port "8080" --db "sqlite:///coordinator.db" --coordinator "http://127.0.0.1:8080" --no-sync --no-mine --generate-genesis-block
```