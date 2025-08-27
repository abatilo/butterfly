import asyncio
import socket

from monarch.actor import Actor, current_rank, endpoint, proc_mesh, ProcMesh
from monarch._src.actor.allocator import RemoteAllocator, StaticRemoteAllocInitializer
from monarch._rust_bindings.monarch_hyperactor.alloc import AllocSpec, AllocConstraints


class EchoActor(Actor):
    """A simple actor with echo functionality for testing."""

    def __init__(self):
        self.rank = current_rank().rank

    def _rprint(self, msg):
        """Helper method to print with rank information."""
        print(f"{self.rank=} {msg}")

    @endpoint
    async def echo(self, message: str) -> str:
        """Simple echo function that returns the input message with rank info."""
        result = f"Echo from rank {self.rank}: {message}"
        self._rprint(result)
        return result

    @endpoint
    async def get_rank(self) -> int:
        """Return the rank of this actor."""
        return self.rank


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
        return

    # Create remote addresses using resolved IPs and port 26600
    remote_addresses = [f"tcp!{ip}:26600" for ip in ips]

    print(f"Creating static remote allocator with addresses: {remote_addresses}")

    # Create the static remote allocator
    allocator = RemoteAllocator(
        world_id="butterfly_echo_job",
        initializer=StaticRemoteAllocInitializer(*remote_addresses),
    )

    # Specify allocation requirements
    spec = AllocSpec(
        constraints=AllocConstraints(),
        host=len(ips),  # Use all resolved hosts
        gpu=8,  # Use 8 GPUs per host
    )

    # Allocate resources
    alloc = allocator.allocate(spec)

    # Wait for allocation to complete
    await alloc.initialized

    # Create process mesh from allocation
    remote_proc_mesh = ProcMesh.from_alloc(alloc)

    # Wait for process mesh to be ready
    await remote_proc_mesh.initialized

    print("Remote allocation successful, spawning actors...")

    # Spawn our actor mesh on top of the remote process mesh
    echo_actor = await remote_proc_mesh.spawn("echo_actor", EchoActor)

    # Test the echo function
    message = "Hello from butterfly!"
    echo_results = await echo_actor.echo.call(message)
    print(f"Echo results: {echo_results}")

    # Get ranks
    ranks = await echo_actor.get_rank.call()
    print(f"Actor ranks: {ranks}")

    # Clean up
    await remote_proc_mesh.stop()


if __name__ == "__main__":
    asyncio.run(main())
