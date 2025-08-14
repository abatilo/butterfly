import asyncio
import os
import socket

import torch
import torch.distributed as dist
import torch.nn as nn
import torch.optim as optim
from monarch.actor import Actor, current_rank, endpoint, proc_mesh
from torch.nn.parallel import DistributedDataParallel as DDP

WORLD_SIZE = int(os.getenv("WORLD_SIZE"))


class ToyModel(nn.Module):
    def __init__(self):
        super(ToyModel, self).__init__()
        self.net1 = nn.Linear(10, 10)
        self.relu = nn.ReLU()
        self.net2 = nn.Linear(10, 5)

    def forward(self, x):
        return self.net2(self.relu(self.net1(x)))


class DDPActor(Actor):
    """This Actor wraps the basic functionality from Torch's DDP example.

    Conveniently, all of the methods we need are already laid out for us,
    so we can just wrap them in the usual Actor endpoint semantic with some
    light modifications.

    Adapted from: https://docs.pytorch.org/tutorials/intermediate/ddp_tutorial.html#basic-use-case
    """

    def __init__(self):
        self.rank = current_rank().rank

    def _rprint(self, msg):
        """Helper method to print with rank information."""
        print(f"{self.rank=} {msg}")

    @endpoint
    async def setup(self):
        """Initialize the PyTorch distributed process group."""
        self._rprint("Initializing torch distributed")

        # create model and move it to GPU with id rank
        local_rank = int(os.getenv("LOCAL_RANK"))
        torch.cuda.set_device(local_rank)

        # initialize the process group
        dist.init_process_group("nccl")
        self._rprint("Finished initializing torch distributed")

    @endpoint
    async def cleanup(self):
        """Clean up the PyTorch distributed process group."""
        self._rprint("Cleaning up torch distributed")
        dist.destroy_process_group()

    @endpoint
    async def demo_basic(self):
        """Run a basic DDP training example."""
        self._rprint("Running basic DDP example")

        device_id = self.rank % torch.cuda.device_count()
        print(f"{device_id=}")

        model = ToyModel().to(device_id)
        ddp_model = DDP(model, device_ids=[device_id])

        loss_fn = nn.MSELoss()
        optimizer = optim.SGD(ddp_model.parameters(), lr=0.001)

        optimizer.zero_grad()
        outputs = ddp_model(torch.randn(20, 10))
        labels = torch.randn(20, 5).to(device_id)
        loss_fn(outputs, labels).backward()
        optimizer.step()

        print(f"{self.rank=} Finished running basic DDP example")


def demo_basic():
    torch.cuda.set_device(int(os.environ["LOCAL_RANK"]))
    dist.init_process_group("nccl")
    rank = dist.get_rank()
    print(f"Start running basic DDP example on rank {rank}.")
    # create model and move it to GPU with id rank
    device_id = rank % torch.cuda.device_count()
    print(f"{device_id=}")
    model = ToyModel().to(device_id)
    ddp_model = DDP(model, device_ids=[device_id])

    loss_fn = nn.MSELoss()
    optimizer = optim.SGD(ddp_model.parameters(), lr=0.001)

    optimizer.zero_grad()
    outputs = ddp_model(torch.randn(20, 10))
    labels = torch.randn(20, 5).to(device_id)
    loss_fn(outputs, labels).backward()
    optimizer.step()
    dist.destroy_process_group()
    print(f"Finished running basic DDP example on rank {rank}.")


async def main():
    # Resolve DNS entries for butterfly service, equivalent to 'dig butterfly.default.svc.cluster.local +short'
    print("Resolving DNS for butterfly.default.svc.cluster.local")
    try:
        # Resolve all IP addresses for the service
        ips = socket.gethostbyname_ex("butterfly.default.svc.cluster.local")[2]
        for ip in ips:
            print(ip)
        print(f"Found {len(ips)} IP addresses")
    except socket.gaierror as e:
        print(f"DNS resolution failed: {e}")

    local_proc_mesh = await proc_mesh(
        gpus=WORLD_SIZE,
    )
    # Spawn our actor mesh on top of the process mesh
    ddp_actor = await local_proc_mesh.spawn("ddp_actor", DDPActor)
    await ddp_actor.setup.call()
    await ddp_actor.demo_basic.call()
    await ddp_actor.cleanup.call()


if __name__ == "__main__":
    asyncio.run(main())
