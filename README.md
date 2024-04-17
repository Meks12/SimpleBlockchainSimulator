# Simple Blockchain Implementation

This repository contains a simple implementation of a blockchain using FastAPI. The system demonstrates basic blockchain functionalities such as transaction handling, block mining, node registration, and manual conflict resolution through a consensus algorithm.

## Features

- **Transaction Handling**: Users can create and broadcast transactions to the network.
- **Block Mining**: Nodes can mine blocks to confirm transactions and add them to the blockchain.
- **Node Registration**: Nodes can dynamically discover and register with other nodes.
- **Consensus Algorithm**: Nodes can manually trigger consensus to resolve conflicts and ensure all nodes have the correct blockchain state.
- **Swagger UI**: Interactive API documentation and testing through Swagger UI.

## Installation

Follow these steps to get your Blockchain node up and running.

### Prerequisites

- Python 3.8+
- Libraries: `fastapi`, `uvicorn`, `pydantic`, `requests`

You can install all required packages using pip:

```bash
pip install fastapi uvicorn pydantic requests
Running the Node
Clone the repository and navigate to the directory:

bash
Copy code
git clone https://github.com/yourgithub/simple-blockchain.git
cd simple-blockchain
Start the blockchain node server on your preferred port:

bash
Copy code
uvicorn main:app --host 0.0.0.0 --port 8001
Repeat the above command in different terminal windows, changing the port (8002, 8003, etc.) to simulate multiple nodes.

Using Swagger UI
Each node provides a Swagger UI which can be accessed via web browser at http://localhost:<port>/docs (replace <port> with the node's port number).

Register Nodes
To enable nodes to communicate, register each node with the others:

Navigate to /nodes/register.
Provide the full URL of another node (e.g., http://localhost:8002) and execute.
Repeat for each pair of nodes in the network.
Create Transactions
Add transactions through the /transactions/new endpoint:

Fill in the sender, recipient, and amount.
Submit the form to create a transaction.
Mine Blocks
To mine a new block:

Visit the /mine endpoint and execute the request.
This will process any pending transactions into a new block.
View Blockchain and Resolve Conflicts
View Blockchain: Use the /chain endpoint to see the current state of the blockchain.
Resolve Conflicts: Use the /nodes/resolve endpoint to trigger the consensus algorithm manually and synchronize the chain across all nodes.

Known Issues
Synchronization: Nodes must manually trigger conflict resolution to update their blockchain state.
Network Errors: Communication failures can disrupt node synchronization.
